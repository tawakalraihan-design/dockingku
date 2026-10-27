"""Docking dengan AutoDock Vina 1.2 (mesin yang sama dengan di PyRx).

Dua cara menjalankan Vina, dipilih otomatis:
- paket Python `vina` (Linux/macOS dari conda-forge);
- program vina.exe resmi (Windows, karena paket Python vina tidak tersedia untuk Windows),
  ditaruh di tools\\vina\\vina.exe di folder aplikasi atau ada di PATH.
"""
import importlib.util
import shutil
import subprocess
from pathlib import Path

from dockingku.config import HOME
from dockingku.core.models import Box, Pose
from dockingku.modules.base import ModuleInfo

INFO = ModuleInfo("docking", "Docking", "AutoDock Vina", "vina (Python) atau vina.exe", needs=[])

VINA_RELEASES = "https://github.com/ccsb-scripps/AutoDock-Vina/releases"


def vina_exe() -> Path | None:
    for path in (HOME / "tools" / "vina" / "vina.exe", HOME / "tools" / "vina" / "vina"):
        if path.exists():
            return path
    found = shutil.which("vina")
    return Path(found) if found else None


def check() -> list[str]:
    """Kosong jika salah satu cara menjalankan Vina tersedia."""
    if importlib.util.find_spec("vina") or vina_exe():
        return []
    return [f"vina (unduh vina.exe dari {VINA_RELEASES} ke tools\\vina\\vina.exe)"]


def dock(receptor_pdbqt: Path, ligand_pdbqt: Path, box: Box, out: Path,
         exhaustiveness: int = 8, n_poses: int = 9, seed: int = 42, job=None) -> list[Pose]:
    if job:
        job.report(0.1, f"Docking {ligand_pdbqt.stem}")
    if importlib.util.find_spec("vina"):
        return _dock_python(receptor_pdbqt, ligand_pdbqt, box, out, exhaustiveness, n_poses, seed)
    exe = vina_exe()
    if exe is None:
        raise RuntimeError(check()[0])
    return _dock_exe(exe, receptor_pdbqt, ligand_pdbqt, box, out, exhaustiveness, n_poses, seed)


def _dock_python(receptor_pdbqt, ligand_pdbqt, box, out, exhaustiveness, n_poses, seed):
    from vina import Vina

    v = Vina(sf_name="vina", seed=seed, verbosity=0)
    v.set_receptor(str(receptor_pdbqt))
    v.set_ligand_from_file(str(ligand_pdbqt))
    v.compute_vina_maps(center=list(box.center), box_size=list(box.size))
    v.dock(exhaustiveness=exhaustiveness, n_poses=n_poses)
    v.write_poses(str(out), n_poses=n_poses, overwrite=True)
    return [Pose(rank=i + 1, affinity=float(e[0]), path=out) for i, e in enumerate(v.energies(n_poses=n_poses))]


def _dock_exe(exe, receptor_pdbqt, ligand_pdbqt, box, out, exhaustiveness, n_poses, seed):
    (cx, cy, cz), (sx, sy, sz) = box.center, box.size
    cmd = [str(exe), "--receptor", str(receptor_pdbqt), "--ligand", str(ligand_pdbqt),
           "--center_x", str(cx), "--center_y", str(cy), "--center_z", str(cz),
           "--size_x", str(sx), "--size_y", str(sy), "--size_z", str(sz),
           "--exhaustiveness", str(exhaustiveness), "--num_modes", str(n_poses),
           "--seed", str(seed), "--out", str(out)]
    run = subprocess.run(cmd, capture_output=True, text=True)
    if run.returncode != 0:
        raise RuntimeError(f"vina gagal: {run.stderr or run.stdout}")
    return parse_poses(out)


def parse_poses(out_pdbqt: Path) -> list[Pose]:
    """Skor dari baris 'REMARK VINA RESULT' di output Vina."""
    poses = []
    for line in out_pdbqt.read_text().splitlines():
        if line.startswith("REMARK VINA RESULT:"):
            poses.append(Pose(rank=len(poses) + 1, affinity=float(line.split()[3]), path=out_pdbqt))
    return poses


def screen(receptor_pdbqt: Path, ligands: list[Path], box: Box, out_dir: Path, job=None, **kw) -> dict:
    """Virtual screening: dock banyak ligan, kembalikan skor terbaik per ligan."""
    best = {}
    for i, lig in enumerate(ligands):
        if job:
            job.report(i / len(ligands), f"{i + 1}/{len(ligands)} {lig.stem}")
        poses = dock(receptor_pdbqt, lig, box, out_dir / f"{lig.stem}_out.pdbqt", **kw)
        best[lig.stem] = poses[0].affinity
    return dict(sorted(best.items(), key=lambda kv: kv[1]))
