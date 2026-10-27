"""Prediksi pocket (pengganti PrankWeb/CavityPlus): P2Rank lokal, atau kotak dari ligan ko-kristal."""
import csv
import subprocess
from pathlib import Path

from dockingku.config import P2RANK_DIR
from dockingku.core.models import Box, Pocket
from dockingku.modules.base import ModuleInfo

INFO = ModuleInfo("pocket", "Prediksi pocket", "PrankWeb / CavityPlus", "P2Rank (Java) atau ligan ko-kristal",
                  needs=["bin:java"])

PRANKWEB = "https://prankweb.cz/"  # tombol pembanding; endpoint API dicek saat implementasi
CAVITYPLUS = "http://www.pkumdl.cn:8000/cavityplus/"


def from_ligand(ligand_pdb: Path, padding: float = 8.0) -> Pocket:
    """Kotak yang membungkus ligan ko-kristal + padding di tiap sisi."""
    xyz = [(float(l[30:38]), float(l[38:46]), float(l[46:54]))
           for l in ligand_pdb.read_text().splitlines() if l.startswith(("ATOM", "HETATM"))]
    lo = [min(c[i] for c in xyz) for i in range(3)]
    hi = [max(c[i] for c in xyz) for i in range(3)]
    center = tuple(round((a + b) / 2, 3) for a, b in zip(lo, hi))
    size = tuple(round(b - a + 2 * padding, 1) for a, b in zip(lo, hi))
    return Pocket(rank=1, score=0.0, box=Box(center, size), method="cocrystal")


def p2rank(pdb: Path, out_dir: Path, size: float = 22.0) -> list[Pocket]:
    exe = P2RANK_DIR / ("prank.bat" if (P2RANK_DIR / "prank.bat").exists() else "prank")
    subprocess.run([str(exe), "predict", "-f", str(pdb), "-o", str(out_dir)], check=True, capture_output=True)
    table = out_dir / f"{pdb.name}_predictions.csv"
    pockets = []
    with open(table) as fh:
        for row in csv.DictReader(fh, skipinitialspace=True):
            row = {k.strip(): v.strip() for k, v in row.items()}
            center = (float(row["center_x"]), float(row["center_y"]), float(row["center_z"]))
            pockets.append(Pocket(rank=int(row["rank"]), score=float(row["score"]),
                                  box=Box(center, (size, size, size)),
                                  residues=row["residue_ids"].split(), method="p2rank"))
    return pockets
