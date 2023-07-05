"""Pixlet tap class."""

from __future__ import annotations

from singer_sdk import Tap
from singer_sdk import typing as th  # JSON schema typing helpers

from tap_pixlet import streams


class TapPixlet(Tap):
    """Pixlet tap class."""

    name = "tap-pixlet"

    config_jsonschema = th.PropertiesList(
        th.Property(
            "path",
            th.StringType,
            required=True,
            description="Path to the Pixlet .star file"
        ),
        th.Property(
            "installation_id",
            th.StringType,
            description="Application installation ID (default: filename)"
        ),
        th.Property(
            "background",
            th.BooleanType,
            description="When false, show application immediately",
            default=True
        ),
        th.Property(
            "app_config",
            th.ObjectType(),
            description="Configuration to pass to the Pixlet application"
        ),
    ).to_dict()

    def discover_streams(self) -> list[streams.PixletStream]:
        """Return a list of discovered streams.

        Returns:
            A list of discovered streams.
        """
        return [
            streams.ImagesStream(self),
        ]


if __name__ == "__main__":
    TapPixlet.cli()
