"""Docking dengan AutoDock Vina 1.2 (mesin yang sama dengan di PyRx)."""
from pathlib import Path

from dockingku.core.models import Box, Pose
from dockingku.modules.base import ModuleInfo

INFO = ModuleInfo("docking", "Docking", "AutoDock Vina", "vina (Python)", needs=["vina"])


def dock(receptor_pdbqt: Path, ligand_pdbqt: Path, box: Box, out: Path,
         exhaustiveness: int = 8, n_poses: int = 9, seed: int = 42, job=None) -> list[Pose]:
    from vina import Vina

    v = Vina(sf_name="vina", seed=seed, verbosity=0)
    v.set_receptor(str(receptor_pdbqt))
    v.set_ligand_from_file(str(ligand_pdbqt))
    v.compute_vina_maps(center=list(box.center), box_size=list(box.size))
    if job:
        job.report(0.1, f"Docking {ligand_pdbqt.stem}")
    v.dock(exhaustiveness=exhaustiveness, n_poses=n_poses)
    v.write_poses(str(out), n_poses=n_poses, overwrite=True)
    return [Pose(rank=i + 1, affinity=float(e[0]), path=out) for i, e in enumerate(v.energies(n_poses=n_poses))]


def screen(receptor_pdbqt: Path, ligands: list[Path], box: Box, out_dir: Path, job=None, **kw) -> dict:
    """Virtual screening: dock banyak ligan, kembalikan skor terbaik per ligan."""
    best = {}
    for i, lig in enumerate(ligands):
        if job:
            job.report(i / len(ligands), f"{i + 1}/{len(ligands)} {lig.stem}")
        poses = dock(receptor_pdbqt, lig, box, out_dir / f"{lig.stem}_out.pdbqt", **kw)
        best[lig.stem] = poses[0].affinity
    return dict(sorted(best.items(), key=lambda kv: kv[1]))
