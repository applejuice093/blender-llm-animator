"""Thin TCP client for the blender-mcp add-on running inside Blender."""

import socket
from typing import Optional

from config import BLENDER_HOST, BLENDER_PORT

# Upper bound on how much reply we buffer, so a misbehaving peer cannot make us
# hold an unbounded amount of memory.
MAX_RESPONSE_BYTES = 1024 * 1024


def _read_reply(sock: socket.socket) -> bytes:
    """Read until the peer closes, goes quiet after replying, or the cap is hit.

    A single ``recv(4096)`` cut longer replies (e.g. tracebacks) short.
    """
    chunks, size = [], 0
    while size < MAX_RESPONSE_BYTES:
        try:
            chunk = sock.recv(65536)
        except socket.timeout:
            if chunks:
                break  # server keeps the connection open after replying
            raise
        if not chunk:
            break
        chunks.append(chunk)
        size += len(chunk)
    return b"".join(chunks)[:MAX_RESPONSE_BYTES]


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
            response = _read_reply(s).decode("utf-8", errors="replace")
            return {"status": "success", "response": response}
    except OSError as e:
        return {"status": "error", "message": f"Could not connect to Blender MCP at {host}:{port}. Error: {e}"}
