"""Kemiripan struktur dengan obat KEGG (pengganti SIMCOMP): Tanimoto fingerprint Morgan."""
import json
from pathlib import Path

from dockingku.config import HOME
from dockingku.core.cache import cache
from dockingku.modules.base import ModuleInfo

INFO = ModuleInfo("similarity", "Kemiripan obat", "SIMCOMP (KEGG)", "RDKit + KEGG REST", needs=["rdkit"])

KEGG_LIST = "https://rest.kegg.jp/list/drug"
KEGG_MOL = "https://rest.kegg.jp/get/{id}/mol"
SIMCOMP = "https://www.genome.jp/tools/simcomp/"
LIBRARY = HOME / "kegg_drug.json"  # {D-number: {"name":..., "smiles":...}}


def build_library(limit: int | None = None, job=None) -> Path:
    """Unduh struktur KEGG DRUG sekali (ribuan file mol, bisa lama), simpan sebagai SMILES."""
    from rdkit import Chem

    lines = cache().get(KEGG_LIST).decode().splitlines()[:limit]
    lib = {}
    for i, line in enumerate(lines):
        did, name = line.split("\t", 1)
        did = did.replace("dr:", "")
        try:
            mol = Chem.MolFromMolBlock(cache().get(KEGG_MOL.format(id=did)).decode())
        except Exception:
            continue
        if mol is not None:
            lib[did] = {"name": name.split(";")[0], "smiles": Chem.MolToSmiles(mol)}
        if job and i % 50 == 0:
            job.report(i / len(lines), f"KEGG {i}/{len(lines)}")
    LIBRARY.parent.mkdir(parents=True, exist_ok=True)
    LIBRARY.write_text(json.dumps(lib))
    return LIBRARY


def tanimoto(a: str, b: str) -> float:
    from rdkit import Chem, DataStructs
    from rdkit.Chem import rdFingerprintGenerator

    gen = rdFingerprintGenerator.GetMorganGenerator(radius=2, fpSize=2048)
    fa, fb = (gen.GetFingerprint(Chem.MolFromSmiles(s)) for s in (a, b))
    return DataStructs.TanimotoSimilarity(fa, fb)


def nearest_drugs(smiles: str, top: int = 10, library: dict | None = None) -> list[dict]:
    lib = library if library is not None else json.loads(LIBRARY.read_text())
    scored = [{"kegg": k, "name": v["name"], "tanimoto": round(tanimoto(smiles, v["smiles"]), 3)}
              for k, v in lib.items()]
    return sorted(scored, key=lambda r: r["tanimoto"], reverse=True)[:top]
