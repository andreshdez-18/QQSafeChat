
import webview
import threading
import socket
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path

def pick_port():
    s = socket.socket()
    s.bind(("127.0.0.1", 0))
    port = s.getsockname()[1]
    s.close()
    return port

def start_docs_server():
    docs_dir = Path.cwd() / "docs"
    port = pick_port()

    class Handler(SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=str(docs_dir), **kwargs)

    httpd = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    t = threading.Thread(target=httpd.serve_forever, daemon=True)
    t.start()

    return port

def main():
    port = start_docs_server()
    url = f"http://127.0.0.1:{port}/index.html"
    print(f"{url}")
    webview.create_window(
        "帮助文档 - QQSafeChat",
        url,
        width=960,
        height=720,
    )
    webview.start(gui="edgechromium")

if __name__ == "__main__":
    main()
