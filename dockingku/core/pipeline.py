"""Urutan 8 langkah dan modul yang menjalankan tiap langkah."""
from dataclasses import dataclass


@dataclass(frozen=True)
class Step:
    key: str
    title: str
    track: str  # protein, ligand, merge
    modules: tuple[str, ...]
    needs: tuple[str, ...] = ()


STEPS = (
    Step("target", "Cari target", "protein", ("sources.rcsb",)),
    Step("receptor", "Siapkan reseptor", "protein", ("prepare", "convert"), ("target",)),
    Step("pocket", "Tentukan pocket", "protein", ("pocket",), ("receptor",)),
    Step("ligand", "Cari ligan", "ligand", ("sources.pubchem", "sources.knapsack")),
    Step("ligprep", "Siapkan ligan", "ligand", ("convert",), ("ligand",)),
    Step("admet", "Saring ADMET", "ligand", ("admet",), ("ligand",)),
    Step("docking", "Docking", "merge", ("docking",), ("pocket", "ligprep")),
    Step("analysis", "Analisis", "merge", ("interactions", "rmsd", "similarity"), ("docking",)),
)


def ready_steps(status: dict) -> list[str]:
    """Langkah yang semua prasyaratnya sudah selesai tetapi dirinya belum."""
    return [s.key for s in STEPS
            if status.get(s.key) != "done" and all(status.get(n) == "done" for n in s.needs)]
