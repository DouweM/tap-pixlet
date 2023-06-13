"""Stream type classes for tap-pixlet."""

from __future__ import annotations
from contextlib import contextmanager
from functools import partial
import json
import os
from pathlib import Path
from http.server import HTTPServer, SimpleHTTPRequestHandler
import threading
import time

from typing import Iterable
import subprocess
import base64

from singer_sdk import typing as th  # JSON Schema typing helpers

from tap_pixlet.client import PixletStream



class AssetServerRequestHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, cache={}, **kwargs):
        self.cache = cache

        super().__init__(*args, **kwargs)

    def do_POST(self):
        length = int(self.headers['Content-Length'])
        data = self.rfile.read(length) if length else ""

        if self.path in self.cache and data in self.cache[self.path]:
            status, text = self.cache[self.path][data]
        else:
            result = subprocess.run(
                [
                    "python",
                    self.translate_path(self.path),
                    data
                ],
                capture_output=True
            )


            if result.returncode == 0:
                status = 200
                text = result.stdout
            else:
                status = 500
                text = json.dumps({"error": result.stderr.decode('utf-8')}).encode()

            self.cache.setdefault(self.path, {})[data] = (status, text)

        self.send_response(status)
        if text.startswith(b'{'):
            self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', len(text))
        self.end_headers()

        self.wfile.write(text)

class ImagesStream(PixletStream):
    """Stream of rendered WebP images."""

    name = "images"
    primary_keys = []
    replication_key = None
    schema = th.PropertiesList(
        th.Property(
            "image_data",
            th.StringType,
            description="Base64-encoded WebP file",
        ),
        th.Property(
            "installation_id",
            th.StringType,
            description="Tidbyt App Installation ID",
        ),
        th.Property(
            "background",
            th.BooleanType,
            description="When false, show application immediately",
        ),
    ).to_dict()

    def get_records(
        self,
        context: dict | None,  # noqa: ARG002
    ) -> Iterable[dict]:
        path = self.config.get("path")
        if not path:
            raise ValueError("No path configured")
        path = Path(path)
        name = path.stem
        script_path = path / f"{name}.star" if path.is_dir() else path

        installation_id = self.config.get("installation_id", name) # TODO: Strip dashes
        background = self.config.get("background", True)

        app_config = {
            "$tz": os.getenv("TZ"),
        }
        app_config.update(self.config.get("app_config", {}))

        with self.asset_server(path) as asset_url:
            if asset_url:
                app_config["$asset_url"] = asset_url

            attempts = 0
            while True:
                self.logger.info("Rendering Pixlet app '%s' (config: %s)", script_path, app_config.keys())

                # TODO: Configuration of pixlet path
                result = subprocess.run(
                    [
                        "pixlet",
                        "render",
                        script_path,
                        '-o',
                        '-',
                        *[f"{k}={v}" for k, v in app_config.items()]
                    ],
                    capture_output=True
                )

                if result.returncode == 0:
                    break

                error_message = result.stderr.decode('utf-8')

                if "context deadline exceeded" in error_message and attempts < 3:
                    attempts += 1
                    self.logger.warning("Pixlet timed out, retrying after 3 seconds (%d/3)", attempts)
                    time.sleep(3)
                    continue

                raise ValueError(f"Pixlet failed: {error_message}")

        image_data = base64.b64encode(result.stdout).decode("utf-8")

        yield {
            "image_data": image_data,
            "installation_id": installation_id,
            "background": background,
        }

    @contextmanager
    def asset_server(self, path: Path) -> None:
        if not path.is_dir():
            yield None
            return

        cache = {}
        server = HTTPServer(('', 0), partial(AssetServerRequestHandler, directory=path, cache=cache))
        ip, port = server.server_address

        daemon = threading.Thread(name='asset_server', target=server.serve_forever)
        daemon.setDaemon(True)
        daemon.start()

        asset_url = f"http://{ip}:{port}/"
        self.logger.info("Serving local assets from %s", asset_url)

        yield asset_url

        server.shutdown()
