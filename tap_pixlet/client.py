"""Custom client handling, including PixletStream base class."""

from __future__ import annotations

from singer_sdk.streams import Stream


class PixletStream(Stream):
    """Stream class for Pixlet streams."""
