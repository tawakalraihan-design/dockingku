# DockingKu (v0.2)

Aplikasi desktop molecular docking yang menggabungkan PyRx, AutoDock Vina, Open Babel,
BIOVIA DS Visualizer, PyMOL, RCSB PDB + Mol*, PubChem, PrankWeb/CavityPlus, KNApSAcK,
ADMETlab, SIMCOMP, dan DockRMSD dalam satu alur 8 langkah.

Ini tahap framework: struktur, antarmuka modul, model proyek, API lokal, dan UI kerangka.
Rancangan lengkap ada di dokumen "Arsitektur Aplikasi Molecular Docking".

## Menjalankan di Windows

1. Pasang Miniforge: https://github.com/conda-forge/miniforge
2. Di "Miniforge Prompt", masuk ke folder aplikasi (`D:\Project ITS\2_Aplikasi DockingKu`) lalu:
   ```
   mamba env create -f environment.yml
   conda activate dockingku
   python run.py
   ```
3. AutoDock Vina untuk Windows: paket Python `vina` tidak tersedia untuk Windows, jadi unduh
   `vina_1.2.x_win.exe` dari https://github.com/ccsb-scripps/AutoDock-Vina/releases, ganti namanya
   jadi `vina.exe`, dan taruh di `tools\vina\vina.exe` di folder aplikasi.
4. Opsional, P2Rank untuk prediksi pocket: unduh dari https://github.com/rdk/p2rank/releases,
   ekstrak ke folder `tools\p2rank` di dalam folder aplikasi, dan pasang Java 17.

## Status modul

| Modul | Menggantikan | Status |
| --- | --- | --- |
| sources.rcsb | RCSB PDB | cari, metadata, unduh |
| sources.pubchem | PubChem | SMILES, sifat, SDF 3D |
| sources.knapsack | KNApSAcK | parser pencarian (perlu diuji ke situs) |
| prepare | BIOVIA DSV | bersihkan protein, ambil ligan ko-kristal |
| convert | Open Babel | SMILES ke 3D, PDBQT ligan dan reseptor |
| pocket | PrankWeb / CavityPlus | kotak dari ligan ko-kristal, P2Rank lokal |
| docking | AutoDock Vina | dock satu ligan, screening banyak ligan |
| interactions | BIOVIA DSV | profil interaksi PLIP |
| admet | ADMETlab | Lipinski, Veber, QED, PAINS; ADMETlab API menyusul |
| similarity | SIMCOMP | Tanimoto ke KEGG DRUG |
| rmsd | DockRMSD | RMSD simetri tanpa superposisi (RDKit) |

UI baru menghubungkan langkah 1 (cari di RCSB + tampil di Mol*); langkah lain menyusul di tahap 2-4.

## Kasus uji

Kasus pertama adalah laporan Kelompok 3 (COX-2, PDB 5KIR). Lihat `kasus-uji/README.md`.

## Data

Proyek docking tersimpan di `proyek\`, cache database online di `cache\`. Keduanya tidak ikut repo dan tidak ditimpa saat update.

## Tes

```
pytest
```
