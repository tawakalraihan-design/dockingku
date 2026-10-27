import json
from pathlib import Path

import pytest

KASUS = Path(__file__).resolve().parents[1] / "kasus-uji" / "kelompok3-cox2-5kir" / "kasus.json"


def test_kasus_lengkap():
    case = json.loads(KASUS.read_text(encoding="utf-8"))
    assert case["reseptor"]["pdb_id"] == "5KIR"
    assert len(case["kotak"]["center"]) == 3
    nama = {l["nama"] for l in case["ligan"]}
    assert nama == set(case["hasil_laporan"]["afinitas"])


def test_smiles_ligan_valid_dan_sesuai_pubchem():
    pytest.importorskip("rdkit")
    from rdkit import Chem
    from rdkit.Chem import Descriptors, rdMolDescriptors

    case = json.loads(KASUS.read_text(encoding="utf-8"))
    rumus = {"Rofecoxib": "C17H14O4S", "Quercetin": "C15H10O7",
             "Curcumin": "C21H20O6", "Resveratrol": "C14H12O3"}
    for lig in case["ligan"]:
        mol = Chem.MolFromSmiles(lig["smiles"])
        assert rdMolDescriptors.CalcMolFormula(mol) == rumus[lig["nama"]]
        assert Descriptors.MolWt(mol) < 500


def test_rmsd_simetri_tanpa_superposisi():
    pytest.importorskip("rdkit")
    from rdkit import Chem
    from rdkit.Chem import AllChem
    from rdkit.Geometry import Point3D

    from dockingku.modules.rmsd import pose_rmsd

    mol = Chem.AddHs(Chem.MolFromSmiles("Cc1ccccc1"))
    AllChem.EmbedMolecule(mol, randomSeed=1)
    ref = Chem.Mol(mol)
    assert pose_rmsd(ref, mol) == pytest.approx(0, abs=1e-6)
    geser = Chem.Mol(mol)
    conf = geser.GetConformer()
    for i in range(geser.GetNumAtoms()):
        p = conf.GetAtomPosition(i)
        conf.SetAtomPosition(i, Point3D(p.x + 1.0, p.y, p.z))
    # tanpa superposisi: geser 1 A semua atom = RMSD 1 A
    assert pose_rmsd(ref, geser) == pytest.approx(1.0, abs=1e-6)
