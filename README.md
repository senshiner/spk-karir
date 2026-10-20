<div align="center">

# **Rancang Bangun Sistem Pendukung Keputusan Rekomendasi Karier Mahasiswa Informatika Berbasis Web Menggunakan Metode Content-Based Filtering dan Simple Additive Weighting (SAW)**

*SPK Karier: sistem pendukung keputusan berbasis web untuk merekomendasikan karier mahasiswa Informatika.*

*Content-Based Filtering bertemu Simple Additive Weighting dalam satu alur yang transparan.*

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Flask](https://img.shields.io/badge/Flask-3.x-black)
![Dataset](https://img.shields.io/badge/Dataset-1.066%20lowongan%20%C2%B7%2022%20karier-orange)
![License](https://img.shields.io/badge/License-MIT-green)

| | |
|---|---|
| 22 okupasi IT Indonesia | matriks kebutuhan skill 22 jabatan × 30 hard skill |
| 1.066 lowongan asli | text mining id.indeed.com dan glints.com, snapshot Oktober 2026 |
| 2 metode SPK | Content-Based Filtering (cosine similarity) + SAW (4 kriteria berbobot) |
| Transparansi penuh | matriks keputusan, matriks ternormalisasi, dan skor preferensi ditampilkan di halaman hasil |

[Metodologi](docs/METHODOLOGY.md) · [Deploy](DEPLOY.md) · [Dataset](data-loker-id/) · [Analisis Sensitivitas](analysis/hasil_sensitivitas.md)

</div>

## Fitur

- **Autentikasi berbasis peran**: admin mengelola data, mahasiswa menerima rekomendasi.
- **Form profil mahasiswa**: nama, tingkat penguasaan tiap skill (skala 0 sampai 5), dan karier yang diminati.
- **Perhitungan dua tahap**: CBF mengukur kecocokan skill, SAW memberi peringkat akhir dari 4 kriteria berbobot.
- **Bobot SAW kustom**: mahasiswa dapat mengatur ulang bobot kriteria di halaman hasil tanpa mengubah bobot default; bobot yang dipakai tercatat di riwayat dan ekspor CSV.
- **Riwayat perhitungan**: setiap perhitungan tersimpan sebagai batch tersendiri dan bisa dibuka ulang.
- **Export CSV** dan panel admin (CRUD karier dan kriteria).

## Cara Jalan

Jalankan perintah berikut dari folder proyek untuk menyalakan aplikasi secara lokal:

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python seed.py
python run.py
```

Perintah `seed.py` mengisi database dari CSV di `data-loker-id/` dan aman dijalankan ulang kapan saja. Setelah server menyala, buka `http://127.0.0.1:5000`, lalu masuk sebagai admin (`admin` / `admin123`, segera ganti) atau daftar sebagai mahasiswa.

## Struktur

```
app/
├── auth/        login, daftar, keluar
├── admin/       dasbor, CRUD karier, CRUD kriteria
├── spk/         form profil, hitung rekomendasi, hasil
├── services/    cbf.py (cosine similarity), saw.py (normalisasi + skor)
├── models.py    User, Career, Criterion, StudentProfile, RecommendationResult
└── templates/   Jinja2 + Tailwind + Chart.js
analysis/        analisis sensitivitas bobot
data-loker-id/   Dataset Lowongan IT Indonesia (skill_matrix.csv, demand_gaji.csv, deskripsi.csv)
```

## Dokumen

- [docs/METHODOLOGY.md](docs/METHODOLOGY.md): metode CBF dan SAW, kriteria dan bobot, cara dataset dibangun, dan analisis sensitivitas.
- [DEPLOY.md](DEPLOY.md): panduan deploy ke VPS (Docker) dan PythonAnywhere.
- [data-loker-id/README.md](data-loker-id/README.md): metodologi dataset lengkap.
