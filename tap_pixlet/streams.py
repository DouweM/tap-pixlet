"""Stream type classes for tap-pixlet."""

from __future__ import annotations
from contextlib import contextmanager
from functools import partial
import json
import os
from pathlib import Path
from http.server import HTTPServer, SimpleHTTPRequestHandler
import re
import tempfile
import threading
import time
import importlib.resources

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

def compile_app_source(app_source, dir_path):
    def update_symbol(symbol, source):
        symbol_regex = rf'(?<![a-z]){symbol}\.([A-Z_]+(?=[^A-Z])|([a-z_]+\())'
        return re.sub(symbol_regex, f"{symbol}__\\1", source)

    def extract_loads(source):
        all_loads = {'system': {}, 'resolved': {}}
        my_loads = {'system': {}, 'resolved': {}}

        def load(match):
            load_path = match['path']
            symbol = match['symbol']
            if match["assign_symbol"]:
                # TODO: Support symbol reassigning
                raise Exception("Loading with symbol reassignment is not supported")

            file_path = None
            if load_path.startswith('pixlib/'):
                file_path = importlib.resources.files("tap_pixlet.pixlib") / Path(load_path).relative_to('pixlib')
            elif load_path.startswith('./'):
                file_path = dir_path / load_path

            if file_path:
                load_source = file_path.read_text()
                load_source, child_loads = extract_loads(load_source)
                load_source = update_symbol(symbol, load_source)

                all_loads['system'].update(child_loads['system'])
                all_loads['resolved'].update(child_loads['resolved'])

                my_loads['resolved'][symbol] = "\n".join([
                    f"### Start {load_path}",
                    load_source.strip("\n"),
                    f"### End {load_path}"
                ])
            else:
                load_source = f'load("{load_path}", "{symbol}")'
                my_loads['system'][symbol] = load_source

            return ""

        load_regex = r'^load\([\'"](?P<path>[^"\']+.star)[\'"]\, ?((?P<assign_symbol>[a-z_]+) ?= ?)?[\'"](?P<symbol>[^"\']+)[\'"]\)\n'
        source = re.sub(load_regex, load, source, flags=re.MULTILINE)

        for symbol in my_loads['resolved'].keys():
            source = update_symbol(symbol, source)

        all_loads['system'].update(my_loads['system'])
        all_loads['resolved'].update(my_loads['resolved'])

        return source, all_loads

    app_source, loads = extract_loads(app_source)

    return "\n\n".join(
        [
            *loads['system'].values(),
            *loads['resolved'].values(),
            app_source.strip("\n")
        ]
    )

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

        installation_id = self.config.get("installation_id", name) # TODO: Strip dashes
        background = self.config.get("background", True)

        app_config = {
            "$tz": os.getenv("TZ"),
        }
        app_config.update(self.config.get("app_config", {}))

        with self.asset_server(path) as asset_url:
            if asset_url:
                app_config["$asset_url"] = asset_url

            with self.compile_app(path) as app_path:
                attempts = 0
                while True:
                    self.logger.info("Rendering Pixlet app '%s' (config: %s)", app_path, app_config.keys())

                    # TODO: Configuration of pixlet path
                    result = subprocess.run(
                        [
                            "pixlet",
                            "render",
                            app_path,
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

    @contextmanager
    def compile_app(self, path: Path):
        if not path.is_dir():
            yield path
            return

        app_path = path / f"{path.stem}.star"
        app_source = app_path.read_text()
        app_source = compile_app_source(app_source, path)

        with tempfile.NamedTemporaryFile(mode="w+t", prefix=path.stem, suffix=".star", delete=False) as temp_app_file:
            with temp_app_file.file as temp_app_file:
                temp_app_file.write(app_source)

            try:
                yield Path(temp_app_file.name)
            except:
                try:
                    raise
                finally:
                    self.logger.info("Compiled Pixlet app: %s", temp_app_file.name)
            else:
                os.unlink(temp_app_file.name)

