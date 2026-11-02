"""blender_bridge tests against a throwaway local TCP server."""

import socket
import threading

from blender_bridge import send_to_blender


def _serve_once(reply: bytes, close_after: bool = True):
    srv = socket.socket()
    srv.bind(("127.0.0.1", 0))
    srv.listen(1)
    port = srv.getsockname()[1]

    def run():
        conn, _ = srv.accept()
        conn.recv(65536)
        conn.sendall(reply)
        if close_after:
            conn.close()
        else:
            threading.Event().wait(2)
            conn.close()
        srv.close()

    threading.Thread(target=run, daemon=True).start()
    return port


def test_reads_replies_longer_than_one_recv():
    reply = b"A" * 20000
    port = _serve_once(reply)
    res = send_to_blender("print(1)", host="127.0.0.1", port=port)
    assert res == {"status": "success", "response": reply.decode()}


def test_returns_reply_when_server_keeps_connection_open():
    port = _serve_once(b"ok", close_after=False)
    res = send_to_blender("print(1)", host="127.0.0.1", port=port, timeout=0.5)
    assert res == {"status": "success", "response": "ok"}


def test_connection_refused_is_reported():
    s = socket.socket()
    s.bind(("127.0.0.1", 0))
    port = s.getsockname()[1]
    s.close()
    res = send_to_blender("print(1)", host="127.0.0.1", port=port, timeout=0.5)
    assert res["status"] == "error"
