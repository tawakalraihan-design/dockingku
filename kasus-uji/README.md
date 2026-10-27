# Kasus uji

## kelompok3-cox2-5kir

Sumber: laporan Project Molecular Docking Kelompok 3 (Teknologi Kedokteran ITS, 2026),
COX-2 PDB 5KIR, kontrol rofecoxib, kandidat quercetin, curcumin, resveratrol.
Laporan asli memakai PyRx + Vina dan BIOVIA; kasus ini mengulang langkah yang sama dengan modul DockingKu.

Jalankan dari folder aplikasi (lingkungan conda `dockingku` aktif):

```
python kasus-uji\jalankan_kasus.py kasus-uji\kelompok3-cox2-5kir
```

Waktu sekitar 5 sampai 15 menit di laptop. Hasilnya di `proyek\kelompok3-cox2-5kir\analysis\perbandingan.md`.

Syarat lulus tahap 2:
- Redocking rofecoxib RMSD di bawah 2 A (laporan: 1,004 A)
- Afinitas tiap ligan dalam 1 kkal/mol dari laporan (-9,8 / -9,8 / -8,9 / -8,0)
- Peringkat kandidat sama: quercetin, resveratrol, curcumin

Catatan: penghitung interaksi PLIP memakai aturan jarak yang berbeda dari BIOVIA, jadi daftar
residu bisa sedikit berbeda (misalnya C-H bond dan pi-sigma tidak dihitung PLIP).
