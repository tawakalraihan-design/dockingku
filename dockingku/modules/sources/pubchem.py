"""PubChem PUG REST: cari senyawa dan ambil SMILES/SDF 3D."""
import json
from pathlib import Path
from urllib.parse import quote

from dockingku.core.cache import cache
from dockingku.core.models import Ligand
from dockingku.modules.base import ModuleInfo

INFO = ModuleInfo("sources.pubchem", "PubChem", "PubChem", "PUG REST", online=True, needs=["httpx"])

BASE = "https://pubchem.ncbi.nlm.nih.gov/rest/pug"
PROPS = "CanonicalSMILES,IsomericSMILES,MolecularFormula,MolecularWeight,IUPACName"


def by_name(name: str) -> Ligand:
    body = cache().get(f"{BASE}/compound/name/{quote(name)}/property/{PROPS}/JSON")
    p = json.loads(body)["PropertyTable"]["Properties"][0]
    smiles = p.get("IsomericSMILES") or p.get("CanonicalSMILES") or p.get("SMILES")
    return Ligand(name=name, smiles=smiles, source="pubchem", source_id=str(p["CID"]),
                  props={"formula": p.get("MolecularFormula"), "mw": float(p.get("MolecularWeight", 0))})


def sdf3d(cid: str, folder: Path) -> Path | None:
    """Konformer 3D dari PubChem; None jika tidak tersedia (nanti dibuat RDKit)."""
    try:
        body = cache().get(f"{BASE}/compound/cid/{cid}/SDF?record_type=3d")
    except Exception:
        return None
    path = folder / f"CID{cid}.sdf"
    path.write_bytes(body)
    return path
