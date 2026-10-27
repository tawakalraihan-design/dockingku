"""Objek data yang dioper antar modul."""
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class Box:
    """Kotak pencarian Vina dalam angstrom."""
    center: tuple[float, float, float]
    size: tuple[float, float, float] = (20.0, 20.0, 20.0)


@dataclass
class Receptor:
    pdb_id: str
    raw_path: Path | None = None
    clean_path: Path | None = None
    pdbqt_path: Path | None = None
    cocrystal_ligand: str | None = None  # kode HET, untuk redocking


@dataclass
class Ligand:
    name: str
    smiles: str
    source: str = "manual"  # pubchem, knapsack, manual
    source_id: str | None = None
    sdf_path: Path | None = None
    pdbqt_path: Path | None = None
    props: dict = field(default_factory=dict)  # Lipinski, ADMET, kemiripan


@dataclass
class Pocket:
    rank: int
    score: float
    box: Box
    residues: list[str] = field(default_factory=list)
    method: str = "p2rank"


@dataclass
class Pose:
    rank: int
    affinity: float  # kkal/mol
    path: Path | None = None
    rmsd: float | None = None
    interactions: list[dict] = field(default_factory=list)
