"""Antarmuka bersama semua modul. Alat baru cukup menambah satu berkas dan mendaftar di sini."""
import importlib
import importlib.util
import shutil
from dataclasses import dataclass, field


@dataclass
class ModuleInfo:
    key: str
    title: str
    replaces: str  # alat di daftar asli
    engine: str  # pustaka atau layanan yang dipakai
    online: bool = False
    needs: list[str] = field(default_factory=list)  # paket Python atau program yang wajib ada


REGISTRY = {
    "sources.rcsb": "dockingku.modules.sources.rcsb",
    "sources.pubchem": "dockingku.modules.sources.pubchem",
    "sources.knapsack": "dockingku.modules.sources.knapsack",
    "prepare": "dockingku.modules.prepare",
    "convert": "dockingku.modules.convert",
    "pocket": "dockingku.modules.pocket",
    "docking": "dockingku.modules.docking",
    "interactions": "dockingku.modules.interactions",
    "admet": "dockingku.modules.admet",
    "similarity": "dockingku.modules.similarity",
    "rmsd": "dockingku.modules.rmsd",
}


def load(key: str):
    return importlib.import_module(REGISTRY[key])


def available(info: ModuleInfo) -> dict:
    """Cek pustaka yang dibutuhkan modul, untuk ditampilkan di layar Status."""
    missing = []
    for need in info.needs:
        if need.startswith("bin:"):
            if not shutil.which(need[4:]):
                missing.append(need)
        elif importlib.util.find_spec(need) is None:
            missing.append(need)
    return {"key": info.key, "title": info.title, "replaces": info.replaces,
            "engine": info.engine, "online": info.online, "missing": missing}


def status_all() -> list[dict]:
    rows = []
    for key in REGISTRY:
        mod = load(key)
        row = available(mod.INFO)
        if hasattr(mod, "check"):  # modul dengan lebih dari satu cara jalan menilai dirinya sendiri
            row["missing"] += mod.check()
        rows.append(row)
    return rows
