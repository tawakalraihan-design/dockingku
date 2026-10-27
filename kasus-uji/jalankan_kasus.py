"""Jalankan ulang kasus uji Kelompok 3 (COX-2, 5KIR) dengan modul DockingKu, lalu bandingkan
hasilnya dengan laporan asli (PyRx + BIOVIA).

Pakai:  python kasus-uji/jalankan_kasus.py kasus-uji/kelompok3-cox2-5kir
Hasil:  proyek/<nama kasus>/analysis/perbandingan.md
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from dockingku.config import PROJECTS_DIR  # noqa: E402
from dockingku.core.models import Box  # noqa: E402
from dockingku.core.project import Project  # noqa: E402
from dockingku.modules import admet, convert, docking, interactions, pocket, prepare, rmsd  # noqa: E402
from dockingku.modules.sources import rcsb  # noqa: E402


def log(msg):
    print(f"[DockingKu] {msg}", flush=True)


def main(case_dir: Path, seed: int = 42):
    case = json.loads((case_dir / "kasus.json").read_text(encoding="utf-8"))
    rec, box_cfg = case["reseptor"], case["kotak"]
    project = Project.create(PROJECTS_DIR, case_dir.name)
    project.params = {"kasus": case_dir.name, "seed": seed, "kotak": box_cfg}

    log(f"1. Unduh {rec['pdb_id']} dari RCSB")
    raw = rcsb.download(rec["pdb_id"], project.path("receptor"))

    log(f"2. Bersihkan reseptor (chain {rec['chain']}, buang air/heme/glikan/ligan) dan buat PDBQT")
    clean = prepare.clean(raw, project.path("receptor", f"{rec['pdb_id']}_{rec['chain']}_bersih.pdb"),
                          chains=[rec["chain"]])
    receptor = convert.receptor_pdbqt(clean, project.path("receptor", f"{rec['pdb_id']}_{rec['chain']}.pdbqt"))

    log("3. Kotak docking dari laporan, dibandingkan dengan pusat ligan ko-kristal")
    kristal_pdb = prepare.extract_ligand(raw, rec["ligan_kokristal"],
                                         project.path("ligands", f"{rec['ligan_kokristal']}_kristal.pdb"),
                                         chain=rec["chain"])
    auto = pocket.from_ligand(kristal_pdb)
    box = Box(tuple(box_cfg["center"]), tuple(box_cfg["size"]))
    geser = sum((a - b) ** 2 for a, b in zip(auto.box.center, box.center)) ** 0.5
    log(f"   pusat laporan {box.center}, pusat ko-kristal {auto.box.center}, selisih {geser:.2f} A")

    hasil = {}
    for lig in case["ligan"]:
        nama = lig["nama"]
        log(f"4-7. {nama}: 3D + minimasi MMFF, PDBQT, docking Vina (exhaustiveness {box_cfg['exhaustiveness']})")
        sdf = convert.smiles_to_3d(lig["smiles"], project.path("ligands", f"{nama}.sdf"), seed=seed)
        lig_pdbqt = convert.ligand_pdbqt(sdf, project.path("ligands", f"{nama}.pdbqt"))
        out = project.path("docking", f"{nama}_out.pdbqt")
        poses = docking.dock(receptor, lig_pdbqt, box, out, exhaustiveness=box_cfg["exhaustiveness"], seed=seed)
        mols = convert.vina_poses(out)
        convert.write_sdf(mols, project.path("docking", f"{nama}_pose.sdf"))

        cpx = convert.complex_pdb(clean, mols, project.path("analysis", f"{nama}_kompleks.pdb"))
        inter = interactions.profile(cpx)
        residu = sorted({i["residue"].rstrip(rec["chain"]) for i in inter})
        sifat = admet.druglike(lig["smiles"])
        heavy = sum(1 for a in mols.GetAtoms() if a.GetAtomicNum() > 1)
        hasil[nama] = {"afinitas": poses[0].affinity, "le": round(-poses[0].affinity / heavy, 3),
                       "residu": residu, "interaksi": inter, "sifat": sifat}

        if lig["peran"] == "kontrol":
            ref = convert.crystal_ligand(kristal_pdb, lig["smiles"])
            semua = rmsd.all_poses(ref, mols)
            hasil[nama]["rmsd_redocking"] = semua[0]
            hasil[nama]["rmsd_semua_pose"] = semua
            log(f"   redocking RMSD pose 1 = {semua[0]} A ({'VALID' if semua[0] <= rmsd.REDOCK_OK else 'TIDAK VALID'})")

    laporan = perbandingan(case, hasil, geser)
    (project.path("analysis", "hasil.json")).write_text(json.dumps(hasil, indent=2, default=str), encoding="utf-8")
    (project.path("analysis", "perbandingan.md")).write_text(laporan, encoding="utf-8")
    project.steps = {k: "done" for k in ("target", "receptor", "pocket", "ligand", "ligprep", "admet",
                                          "docking", "analysis")}
    project.save()
    print(laporan)
    log(f"Selesai. Folder proyek: {project.root}")


def perbandingan(case, hasil, geser) -> str:
    asli = case["hasil_laporan"]
    kunci = set(case["residu_kunci"])
    tol = case["toleransi"]["afinitas_kkal"]
    baris = ["# Perbandingan DockingKu vs laporan Kelompok 3", "",
             f"Selisih pusat kotak laporan terhadap pusat ligan ko-kristal: {geser:.2f} A", "",
             "| Ligan | Afinitas laporan | Afinitas DockingKu | Selisih | LE | Residu kunci (laporan / DockingKu) | Lipinski |",
             "| --- | --- | --- | --- | --- | --- | --- |"]
    for nama, h in hasil.items():
        a0 = asli["afinitas"][nama]
        d = h["afinitas"] - a0
        cocok_baru = len(kunci & set(h["residu"]))
        cocok_lama = asli["residu_kunci_cocok"].get(nama, len(kunci))
        tanda = "" if abs(d) <= tol else " (!)"
        baris.append(f"| {nama} | {a0} | {h['afinitas']:.1f} | {d:+.1f}{tanda} | {h['le']} | "
                     f"{cocok_lama}/7 / {cocok_baru}/7 | {'lolos' if h['sifat']['lipinski_pass'] else 'gagal'} |")
    urut_lama = sorted(asli["afinitas"], key=asli["afinitas"].get)
    urut_baru = sorted(hasil, key=lambda n: hasil[n]["afinitas"])
    kontrol = next(n for n in hasil if "rmsd_redocking" in hasil[n])
    r = hasil[kontrol]["rmsd_redocking"]
    baris += ["", f"Redocking {kontrol}: RMSD {r} A (laporan {asli['redocking']['rmsd']} A), "
                  f"{'valid' if r <= asli['redocking']['batas_rmsd'] else 'tidak valid'}.",
              f"Peringkat laporan: {', '.join(urut_lama)}.", f"Peringkat DockingKu: {', '.join(urut_baru)}.", ""]
    for nama, h in hasil.items():
        baris.append(f"- {nama}: {', '.join(h['residu'])}")
    return "\n".join(baris) + "\n"


if __name__ == "__main__":
    main(Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).parent / "kelompok3-cox2-5kir")
