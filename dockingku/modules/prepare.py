"""Membersihkan protein (pengganti BIOVIA Discovery Studio): buang air dan heteroatom,
lengkapi atom yang hilang, tambah hidrogen pada pH tertentu."""
from pathlib import Path

from dockingku.modules.base import ModuleInfo

INFO = ModuleInfo("prepare", "Siapkan reseptor", "BIOVIA Discovery Studio Visualizer",
                  "PDBFixer + OpenMM", needs=["pdbfixer", "openmm"])


def clean(pdb_in: Path, pdb_out: Path, chains: list[str] | None = None, ph: float = 7.4,
          keep_water: bool = False) -> Path:
    from openmm.app import PDBFile
    from pdbfixer import PDBFixer

    fixer = PDBFixer(filename=str(pdb_in))
    if chains:
        drop = [c.id for c in fixer.topology.chains() if c.id not in chains]
        fixer.removeChains(chainIds=drop)
    fixer.findMissingResidues()
    fixer.missingResidues = {}  # loop panjang tidak dimodelkan
    fixer.findNonstandardResidues()
    fixer.replaceNonstandardResidues()
    fixer.removeHeterogens(keepWater=keep_water)
    fixer.findMissingAtoms()
    fixer.addMissingAtoms()
    fixer.addMissingHydrogens(ph)
    with open(pdb_out, "w") as fh:
        PDBFile.writeFile(fixer.topology, fixer.positions, fh, keepIds=True)
    return pdb_out


def extract_ligand(pdb_in: Path, het_code: str, out: Path, chain: str | None = None) -> Path:
    """Ambil ligan ko-kristal (untuk kotak docking dan redocking). Altloc selain A dibuang."""
    lines = [l for l in pdb_in.read_text().splitlines()
             if l.startswith("HETATM") and l[17:20].strip() == het_code.upper()
             and (chain is None or l[21] == chain) and l[16] in " A"]
    if not lines:
        raise ValueError(f"Ligan {het_code} tidak ditemukan di {pdb_in.name}")
    out.write_text("\n".join(lines) + "\nEND\n")
    return out
