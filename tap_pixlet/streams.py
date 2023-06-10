"""Stream type classes for tap-pixlet."""

from __future__ import annotations
from functools import partial
import os
from pathlib import Path
from http.server import HTTPServer, SimpleHTTPRequestHandler
import threading

from typing import Iterable
import subprocess
import base64

from singer_sdk import typing as th  # JSON Schema typing helpers

from tap_pixlet.client import PixletStream


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

        app_config = self.config.get("app_config", {})
        app_config["$tz"] = os.getenv("TZ")

        if path.is_dir():
            server = HTTPServer(('', 0), partial(SimpleHTTPRequestHandler, directory=path))
            ip, port = server.server_address

            daemon = threading.Thread(name='asset_server', target=server.serve_forever)
            daemon.setDaemon(True)
            daemon.start()

            asset_url = f"http://{ip}:{port}/"
            app_config["$asset_url"] = asset_url

        self.logger.info("Rendering pixlet", script_path, app_config.keys())

        config_args = [f"{k}={v}" for k, v in app_config.items()]
        # TODO: Configuration of pixlet path
        result = subprocess.run(["pixlet", "render", script_path, '-o', '-', *config_args], capture_output=True)

        if result.returncode != 0:
            raise ValueError(f"Pixlet failed: {result.stderr.decode('utf-8')}")

        image_data = base64.b64encode(result.stdout).decode("utf-8")

        yield {
            "image_data": image_data,
            "installation_id": installation_id,
            "background": background,
        }
