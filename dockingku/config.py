import os
from pathlib import Path

HOST = "127.0.0.1"
PORT = 8765
# Folder aplikasi, mis. D:\Project ITS\2_Aplikasi DockingKu. Isi proyek/ tidak pernah ditimpa saat update.
HOME = Path(os.environ.get("DOCKINGKU_HOME", Path(__file__).resolve().parents[1]))
PROJECTS_DIR = HOME / "proyek"
CACHE_DB = HOME / "cache" / "http.sqlite"
P2RANK_DIR = HOME / "tools" / "p2rank"  # opsional, butuh Java 17
