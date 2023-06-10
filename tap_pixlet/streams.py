"""Stream type classes for tap-pixlet."""

from __future__ import annotations
from pathlib import Path

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

        installation_id = self.config.get("installation_id", path.stem) # TODO: Strip dashes
        background = self.config.get("background", True)
        app_config = self.config.get("app_config", {})

        self.logger.info("Running curl")
        result = subprocess.run(["curl", "https://raw.githubusercontent.com/DouweM/PebbleRevolution/master/resources/images/date_1.png"], capture_output=True)

        if result.returncode != 0:
            raise ValueError(f"Curl failed: {result.stderr.decode('utf-8')}")

        self.logger.info("Result", result)
        self.logger.info("Stdout", result.stdout)

        # TODO: Configuration of pixlet path
        # TODO: $tz by default
        config_args = [f"{k}={v}" for k, v in app_config.items()]
        self.logger.info("Rendering pixlet", path, app_config.keys())
        result = subprocess.run(["pixlet", "render", path, '-o', '-', *config_args], capture_output=True)

        if result.returncode != 0:
            raise ValueError(f"Pixlet failed: {result.stderr.decode('utf-8')}")

        image_data = base64.b64encode(result.stdout).decode("utf-8")

        yield {
            "image_data": image_data,
            "installation_id": installation_id,
            "background": background,
        }
