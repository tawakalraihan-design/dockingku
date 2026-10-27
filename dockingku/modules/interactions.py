"""Interaksi protein-ligan (pengganti tampilan 2D BIOVIA): ikatan H, hidrofobik, pi, jembatan garam."""
from pathlib import Path

from dockingku.modules.base import ModuleInfo

INFO = ModuleInfo("interactions", "Interaksi", "BIOVIA Discovery Studio Visualizer", "PLIP", needs=["plip"])

KINDS = {"hbonds_pdon": "Ikatan H (protein donor)", "hbonds_ldon": "Ikatan H (ligan donor)",
         "hydrophobic_contacts": "Hidrofobik", "pistacking": "Pi-stacking",
         "saltbridge_lneg": "Jembatan garam", "saltbridge_pneg": "Jembatan garam",
         "pication_laro": "Pi-kation", "pication_paro": "Pi-kation", "halogen_bonds": "Halogen"}


def profile(complex_pdb: Path) -> list[dict]:
    """complex_pdb = reseptor + satu pose ligan dalam satu file PDB."""
    from plip.structure.preparation import PDBComplex

    mol = PDBComplex()
    mol.load_pdb(str(complex_pdb))
    mol.analyze()
    rows = []
    for site_id, site in mol.interaction_sets.items():
        for attr, label in KINDS.items():
            for it in getattr(site, attr, []):
                rows.append({"site": site_id, "type": label, "residue": f"{it.restype}{it.resnr}{it.reschain}",
                             "distance": round(float(getattr(it, "distance", getattr(it, "distance_ad", 0.0))), 2)})
    return rows
