import socket

def send_to_blender(script: str, host: str = "127.0.0.1", port: int = 8123) -> dict:
    """
    Sends the generated Python script to the blender-mcp TCP server.
    """
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(5.0)
            s.connect((host, port))
            s.sendall(script.encode('utf-8'))
            response = s.recv(4096).decode('utf-8')
            return {"status": "success", "response": response}
    except Exception as e:
        return {"status": "error", "message": f"Could not connect to Blender MCP at {host}:{port}. Error: {str(e)}"}
