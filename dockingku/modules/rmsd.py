"""RMSD pose terhadap referensi dengan koreksi simetri (pengganti DockRMSD).

Seperti DockRMSD: atom berat saja, tanpa superposisi (pose dan kristal sudah di kerangka
koordinat reseptor yang sama), dan atom yang setara secara simetri dipasangkan secara optimal.
"""
from dockingku.modules.base import ModuleInfo

INFO = ModuleInfo("rmsd", "RMSD", "DockRMSD", "RDKit CalcRMS", needs=["rdkit"])

REDOCK_OK = 2.0  # angstrom; batas umum validasi redocking


def pose_rmsd(reference, pose, pose_conf_id: int = -1) -> float:
    """reference, pose: molekul RDKit dengan bond order benar (topologi sama)."""
    from rdkit import Chem
    from rdkit.Chem import rdMolAlign

    ref = Chem.RemoveHs(reference)
    prb = Chem.RemoveHs(pose)
    return rdMolAlign.CalcRMS(prb, ref, prbId=pose_conf_id)


def all_poses(reference, pose) -> list[float]:
    """RMSD setiap konformer (pose Vina) terhadap referensi."""
    return [round(pose_rmsd(reference, pose, c.GetId()), 3) for c in pose.GetConformers()]
