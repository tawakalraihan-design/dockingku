"""Buka DockingKu di jendela desktop."""
import threading

import uvicorn

from dockingku.app import app
from dockingku.config import HOST, PORT


def main():
    server = uvicorn.Server(uvicorn.Config(app, host=HOST, port=PORT, log_level="warning"))
    threading.Thread(target=server.run, daemon=True).start()
    try:
        import webview
    except ImportError:
        print(f"pywebview belum terpasang. Buka http://{HOST}:{PORT} di browser.")
        threading.Event().wait()
        return
    webview.create_window("DockingKu", f"http://{HOST}:{PORT}", width=1400, height=900)
    webview.start()


if __name__ == "__main__":
    main()
