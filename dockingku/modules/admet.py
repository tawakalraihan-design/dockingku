"""Penyaringan sifat obat (pengganti ADMETlab): aturan lokal RDKit + ADMETlab 3.0 online."""
from dockingku.modules.base import ModuleInfo

INFO = ModuleInfo("admet", "Saring ADMET", "ADMETlab", "RDKit (lokal) + ADMETlab 3.0 API", needs=["rdkit"])

ADMETLAB = "https://admetlab3.scbdd.com/"  # endpoint API dicek saat implementasi


def druglike(smiles: str) -> dict:
    from rdkit import Chem
    from rdkit.Chem import QED, Crippen, Descriptors, Lipinski, rdMolDescriptors
    from rdkit.Chem.FilterCatalog import FilterCatalog, FilterCatalogParams

    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        raise ValueError(f"SMILES tidak valid: {smiles}")
    p = {
        "mw": round(Descriptors.MolWt(mol), 2),
        "logp": round(Crippen.MolLogP(mol), 2),
        "hbd": Lipinski.NumHDonors(mol),
        "hba": Lipinski.NumHAcceptors(mol),
        "tpsa": round(rdMolDescriptors.CalcTPSA(mol), 2),
        "rotb": Lipinski.NumRotatableBonds(mol),
        "qed": round(QED.qed(mol), 3),
    }
    p["lipinski_violations"] = sum([p["mw"] > 500, p["logp"] > 5, p["hbd"] > 5, p["hba"] > 10])
    p["lipinski_pass"] = p["lipinski_violations"] <= 1
    p["veber_pass"] = p["rotb"] <= 10 and p["tpsa"] <= 140
    params = FilterCatalogParams()
    params.AddCatalog(FilterCatalogParams.FilterCatalogs.PAINS)
    match = FilterCatalog(params).GetFirstMatch(mol)
    p["pains"] = match.GetDescription() if match else None
    return p


def admetlab(smiles_list: list[str]) -> list[dict]:
    """Prediksi ADME/toksisitas lengkap lewat ADMETlab 3.0. Diisi di tahap 4."""
    raise NotImplementedError("Integrasi ADMETlab 3.0 dijadwalkan di tahap 4")
