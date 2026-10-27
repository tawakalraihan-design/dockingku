"""RCSB PDB: cari dan unduh struktur protein (pengganti situs RCSB PDB)."""
import json
from pathlib import Path

from dockingku.core.cache import cache
from dockingku.modules.base import ModuleInfo

INFO = ModuleInfo("sources.rcsb", "RCSB PDB", "RCSB PDB", "RCSB Search/Data API", online=True, needs=["httpx"])

SEARCH = "https://search.rcsb.org/rcsbsearch/v2/query"
ENTRY = "https://data.rcsb.org/rest/v1/core/entry/{id}"
FILE = "https://files.rcsb.org/download/{id}.{fmt}"


def search(text: str, max_resolution: float = 2.5, limit: int = 20) -> list[str]:
    """Cari ID PDB dari kata kunci (nama protein, gen, organisme)."""
    query = {
        "query": {"type": "group", "logical_operator": "and", "nodes": [
            {"type": "terminal", "service": "full_text", "parameters": {"value": text}},
            {"type": "terminal", "service": "text", "parameters": {
                "attribute": "rcsb_entry_info.resolution_combined",
                "operator": "less_or_equal", "value": max_resolution}},
        ]},
        "return_type": "entry",
        "request_options": {"paginate": {"start": 0, "rows": limit}},
    }
    body = cache().get(SEARCH, method="POST", json=query)
    return [hit["identifier"] for hit in json.loads(body).get("result_set", [])] if body else []


def entry(pdb_id: str) -> dict:
    """Metadata ringkas: judul, metode, resolusi, ligan ko-kristal."""
    data = json.loads(cache().get(ENTRY.format(id=pdb_id.upper())))
    info = data.get("rcsb_entry_info", {})
    return {
        "id": pdb_id.upper(),
        "title": data.get("struct", {}).get("title"),
        "method": info.get("experimental_method"),
        "resolution": (info.get("resolution_combined") or [None])[0],
        "ligands": info.get("nonpolymer_bound_components") or [],
    }


def download(pdb_id: str, folder: Path, fmt: str = "pdb") -> Path:
    path = folder / f"{pdb_id.upper()}.{fmt}"
    path.write_bytes(cache().get(FILE.format(id=pdb_id.upper(), fmt=fmt)))
    return path
