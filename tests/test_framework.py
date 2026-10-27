from pathlib import Path

from dockingku.core.pipeline import STEPS, ready_steps
from dockingku.core.project import Project, SUBDIRS
from dockingku.modules import base


def test_semua_modul_terdaftar_dan_punya_info():
    for key in base.REGISTRY:
        info = base.load(key).INFO
        assert info.key == key


def test_langkah_menunjuk_modul_yang_ada():
    assert len(STEPS) == 8
    for step in STEPS:
        assert all(m in base.REGISTRY for m in step.modules)


def test_urutan_langkah():
    assert ready_steps({}) == ["target", "ligand"]
    done = {k: "done" for k in ("target", "receptor", "pocket", "ligand", "ligprep")}
    assert "docking" in ready_steps(done)


def test_proyek_dibuat_dan_dibuka(tmp_path: Path):
    p = Project.create(tmp_path, "EGFR Kunyit")
    assert all((p.root / s).is_dir() for s in SUBDIRS)
    assert Project.open(p.root).name == "EGFR Kunyit"


def test_kotak_dari_ligan_kokristal(tmp_path: Path):
    from dockingku.modules.pocket import from_ligand
    lig = tmp_path / "lig.pdb"
    lig.write_text("HETATM    1  C1  LIG A   1       0.000   0.000   0.000\n"
                   "HETATM    2  C2  LIG A   1       4.000   2.000   6.000\n")
    pocket = from_ligand(lig, padding=8)
    assert pocket.box.center == (2.0, 1.0, 3.0)
    assert pocket.box.size == (20.0, 18.0, 22.0)


def test_baca_skor_output_vina(tmp_path: Path):
    from dockingku.modules.docking import parse_poses
    out = tmp_path / "out.pdbqt"
    out.write_text("MODEL 1\nREMARK VINA RESULT:    -9.812      0.000      0.000\nENDMDL\n"
                   "MODEL 2\nREMARK VINA RESULT:    -9.100      1.532      2.101\nENDMDL\n")
    poses = parse_poses(out)
    assert [p.affinity for p in poses] == [-9.812, -9.1]
    assert [p.rank for p in poses] == [1, 2]
