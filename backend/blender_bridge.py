"""Thin TCP client for the blender-mcp add-on running inside Blender."""

import socket
from typing import Optional

from config import BLENDER_HOST, BLENDER_PORT


def send_to_blender(
    script: str,
    host: Optional[str] = None,
    port: Optional[int] = None,
    timeout: float = 5.0,
) -> dict:
    """Send a generated Python script to the blender-mcp TCP server.

    Host/port default to ``BLENDER_HOST``/``BLENDER_PORT`` from config.
    Never raises: connection problems are returned as ``{"status": "error"}``.
    """
    host = host or BLENDER_HOST
    port = port or BLENDER_PORT
    try:
        with socket.create_connection((host, port), timeout=timeout) as s:
            s.sendall(script.encode("utf-8"))
            response = s.recv(4096).decode("utf-8")
            return {"status": "success", "response": response}
    except OSError as e:
        return {"status": "error", "message": f"Could not connect to Blender MCP at {host}:{port}. Error: {e}"}
