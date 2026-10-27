"""Konversi format dan persiapan PDBQT (pengganti Open Babel di dalam PyRx)."""
import subprocess
from pathlib import Path

from dockingku.modules.base import ModuleInfo

INFO = ModuleInfo("convert", "Konversi dan PDBQT", "Open Babel", "RDKit + Meeko + Open Babel",
                  needs=["rdkit", "meeko", "bin:obabel"])


def smiles_to_3d(smiles: str, out_sdf: Path, seed: int = 42) -> Path:
    """SMILES -> 3D + minimasi energi MMFF94."""
    from rdkit import Chem
    from rdkit.Chem import AllChem

    mol = Chem.AddHs(Chem.MolFromSmiles(smiles))
    AllChem.EmbedMolecule(mol, randomSeed=seed)
    AllChem.MMFFOptimizeMolecule(mol)
    with Chem.SDWriter(str(out_sdf)) as w:
        w.write(mol)
    return out_sdf


def ligand_pdbqt(sdf: Path, out: Path) -> Path:
    from meeko import MoleculePreparation, PDBQTWriterLegacy
    from rdkit import Chem

    mol = Chem.MolFromMolFile(str(sdf), removeHs=False)
    setups = MoleculePreparation().prepare(mol)
    text, ok, err = PDBQTWriterLegacy.write_string(setups[0])
    if not ok:
        raise ValueError(err)
    out.write_text(text)
    return out


def receptor_pdbqt(pdb: Path, out: Path) -> Path:
    """PDB bersih (sudah ber-H) -> PDBQT kaku, lewat Open Babel."""
    subprocess.run(["obabel", str(pdb), "-xr", "-O", str(out)], check=True, capture_output=True)
    return out


def obabel(src: Path, out: Path, *args: str) -> Path:
    """Konversi umum, format ditebak dari ekstensi (sdf, mol2, pdb, pdbqt)."""
    subprocess.run(["obabel", str(src), "-O", str(out), *args], check=True, capture_output=True)
    return out


def crystal_ligand(pdb: Path, smiles: str):
    """Ligan ko-kristal (PDB tanpa bond order) -> molekul RDKit, bond order dari SMILES."""
    from rdkit import Chem
    from rdkit.Chem import AllChem

    raw = Chem.MolFromPDBFile(str(pdb), removeHs=True)
    return AllChem.AssignBondOrdersFromTemplate(Chem.MolFromSmiles(smiles), raw)


def vina_poses(pdbqt: Path):
    """Output Vina (PDBQT) -> satu molekul RDKit, satu konformer per pose."""
    from meeko import PDBQTMolecule, RDKitMolCreate

    pmol = PDBQTMolecule.from_file(str(pdbqt), skip_typing=True)
    return RDKitMolCreate.from_pdbqt_mol(pmol)[0]


def write_sdf(mol, out: Path) -> Path:
    from rdkit import Chem

    with Chem.SDWriter(str(out)) as w:
        for conf in mol.GetConformers():
            w.write(mol, confId=conf.GetId())
    return out


def complex_pdb(receptor_pdb: Path, mol, out: Path, conf_id: int = 0, resname: str = "LIG") -> Path:
    """Gabung reseptor + satu pose jadi satu PDB, untuk PLIP."""
    from rdkit import Chem

    lig = Chem.Mol(mol)
    keep = Chem.Conformer(lig.GetConformer(conf_id))
    lig.RemoveAllConformers()
    lig.AddConformer(keep, assignId=True)
    protein = [l for l in receptor_pdb.read_text().splitlines() if l.startswith(("ATOM", "HETATM", "TER"))]
    offset = len(protein)  # nomor atom ligan melanjutkan reseptor agar CONECT tidak salah tunjuk
    for atom in lig.GetAtoms():
        name = f"{atom.GetSymbol()}{atom.GetIdx() + 1}"[:4]
        info = Chem.AtomPDBResidueInfo(f"{name:<4}" if len(name) == 4 else f" {name:<3}", residueName=resname,
                                       chainId="Z", residueNumber=1, isHeteroAtom=True)
        atom.SetMonomerInfo(info)
    ligand = []
    for line in Chem.MolToPDBBlock(lig, flavor=4).splitlines():
        if line.startswith("HETATM"):
            ligand.append(f"HETATM{int(line[6:11]) + offset:5d}{line[11:]}")
        elif line.startswith("CONECT"):
            ids = [int(line[i:i + 5]) + offset for i in range(6, len(line.rstrip()), 5)]
            ligand.append("CONECT" + "".join(f"{i:5d}" for i in ids))
    out.write_text("\n".join(protein + ligand + ["END"]) + "\n")
    return out
