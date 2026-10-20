# Metodologi

Dokumen ini menjelaskan metode dan data di balik aplikasi SPK Rekomendasi Karier.
Detail lengkap konstruksi dataset ada di [data-loker-id/README.md](../data-loker-id/README.md).

## Gambaran alur

Mahasiswa mengisi profil (tingkat penguasaan tiap skill 0 sampai 5 + karier yang diminati).
Sistem bekerja dalam dua tahap:

1. **Content-Based Filtering (CBF)** mengukur kecocokan profil skill mahasiswa terhadap
   22 vektor karier dengan *cosine similarity*. Hasilnya menjadi skor kriteria C1.
2. **Simple Additive Weighting (SAW)** menggabungkan C1 dengan tiga kriteria pasar
   (C2 gaji, C3 demand, C4 minat) memakai bobot, menghasilkan peringkat akhir 22 karier.

Setiap perhitungan disimpan sebagai batch tersendiri beserta bobot yang dipakai,
sehingga hasilnya dapat ditelusuri ulang dari halaman riwayat.

## Content-Based Filtering

Vektor karier dibangun dari Dataset Lowongan IT Indonesia: untuk tiap jabatan, 30 hard
skill diberi skor kepentingan 1 sampai 5. Vektor mahasiswa dibangun dari form profil:
tiap skill dinilai sendiri oleh mahasiswa dengan skala penguasaan 0 sampai 5
(0 = tidak menguasai, 5 = ahli). Kedua vektor simetris, lalu kecocokan dihitung dengan
*cosine similarity* (0 sampai 1) memakai scikit-learn. Tidak ada threshold biner,
sehingga nuansa tingkat kepentingan dan kedalaman penguasaan lestari.

## Simple additive weighting

### Kriteria dan bobot default

| Kode | Kriteria | Bobot default | Sumber nilai |
|------|----------|---------------|--------------|
| C1 | Kecocokan skill (dari CBF) | 0,35 | cosine similarity profil vs vektor karier |
| C2 | Gaji | 0,25 | median gaji observasi per jabatan (juta Rp/bulan) |
| C3 | Demand | 0,20 | jumlah lowongan per jabatan, dinormalisasi min-max ke skala 1–10 |
| C4 | Minat | 0,20 | 1 jika karier diminati di form profil, 0 jika tidak |

Keempat kriteria bertipe benefit; normalisasi memakai `rij = xij / max(xj)`, skor
preferensi dihitung sebagai `Vi = Σ wj × rij`, dan peringkat diurutkan dari Vi terbesar.

### Bobot kustom per mahasiswa

Mahasiswa dapat mengatur bobot C1 sampai C4 sendiri di halaman hasil (panel
"Atur Bobot Kriteria"). Bobot kustom tersimpan di sesi pengguna dan tidak mengubah
bobot default. Bila total bobot yang dimasukkan bukan 1, sistem menormalisasikannya
otomatis dan mencatatnya. Bobot yang benar-benar dipakai pada suatu perhitungan
(setelah normalisasi) disimpan pada batch hasil, ditampilkan di halaman riwayat,
dan disertakan sebagai baris metadata pada ekspor CSV.

## Dataset

Dataset primer adalah Dataset Lowongan IT Indonesia, matriks kebutuhan skill
22 jabatan IT × 30 hard skill, dibangun sendiri melalui text mining **1.066 lowongan
IT unik** (1.045 untuk mining, deskripsi > 200 karakter) dari id.indeed.com dan
glints.com, snapshot 19–20 Oktober 2026.

### Pipeline konstruksi

1. **Pengumpulan**: scraping halaman lowongan IT Indonesia (judul, deskripsi/requirements,
   info gaji). Target ±25 lowongan per jabatan per sumber, sopan (delay, user-agent wajar).
2. **Ekstraksi skill**: pipeline NLP berbasis spaCy (`en_core_web_sm`) atas 30 hard skill
   teknis (SQL, Python, JavaScript, Git, AWS, Agile, Linux, dst.):
   - segmentasi seksi deskripsi: skill hanya dihitung bila muncul di seksi
     persyaratan/kualifikasi/tanggung jawab, bukan di profil perusahaan atau benefit;
   - pencocokan frasa sadar lemma dengan aturan kelas kata untuk kata ambigu
     (mis. "Go" sebagai bahasa pemrograman, bukan kata kerja "go"; ".js" bukan JavaScript);
   - deteksi negasi: "CI/CD is a plus" atau "tidak wajib" tidak dihitung sebagai syarat.
3. **Skor 1–5**: untuk tiap jabatan *o* dan skill *s*,
   `skor(o,s) = 1 + 4 × (pct(o,s) / max_pct(o))` dengan `pct` = % lowongan jabatan *o*
   yang menyebut skill *s* (satu desimal, relatif per jabatan).
4. **Demand (C3)**: jumlah lowongan per jabatan, dinormalisasi min-max ke skala 1–10.
5. **Gaji (C2)**: dari info gaji yang tercantum di lowongan (median/min/max per jabatan,
   dalam juta Rp/bulan, tersedia untuk 12–26 lowongan per jabatan).

### Validasi metode ekstraksi

Hasil NLP dibandingkan head-to-head dengan metode lama (*keyword matching* regex)
pada 31.350 sel lowongan×skill: **agreement 99,68%**. NLP menggugurkan 98 deteksi
false positive (ambiguitas kata seperti "WHERE YOU'LL GO" yang tertangkap sebagai Go,
"the rest of the team" sebagai REST, "React.js" sebagai JavaScript, "excels at" sebagai
Excel; negasi; seksi tidak relevan). Skor berubah pada 106 dari 660 sel dengan
perubahan maksimum 1,0; 20 dari 22 jabatan memiliki top-3 skill yang identik persis.
Matriks NLP diadopsi sebagai versi resmi.

### Keterbatasan

- Sampel 39–55 lowongan per jabatan dari dua sumber: Indeed dan Glints.
- Ekstraksi berbasis kamus 30 skill: sinonim atau teknologi di luar kamus tidak
  tertangkap; aturan negasi bersifat lokal pada kalimat.
- Mayoritas iklan berbahasa Inggris; data gaji lebih sering tercantum di Glints
  daripada Indeed.
- Snapshot Oktober 2026: pasar kerja berubah seiring waktu, *re-scraping* berkala disarankan.
- Validasi silang dengan Indotask (World Bank 2020) hanya kualitatif karena taksonomi
  skill berbeda; detailnya di `data-loker-id/README.md`.

## Analisis Sensitivitas

Untuk menguji kestabilan ranking terhadap perubahan bobot, jalankan:

```bash
python analysis/sensitivitas.py
```

Skrip mengevaluasi tiga profil contoh (Backend/Data, Jaringan, Frontend; tiap skill
diberi rating penguasaan realistis 0 sampai 5) pada 6 skenario deterministik
(dominasi tunggal tiap kriteria dan perturbasi C1 sebesar ±0,10) serta 200 sampel
acak Dirichlet di sekitar bobot default (seed 42), memakai fungsi CBF dan SAW yang
sama persis dengan aplikasi. Hasil ditulis ke `analysis/hasil_sensitivitas.md`
(tabel dan kesimpulan, siap dikutip untuk Bab 4) dan `analysis/hasil_sensitivitas.csv`.

Ringkasan hasil: peringkat pertama bertahan pada 91,6% skenario dan himpunan
3 besar utuh pada 74,6% skenario; perubahan terbesar terjadi pada skenario
dominasi tunggal. Bobot default (0,35/0,25/0,20/0,20) layak dipakai karena ranking
cukup stabil pada variasi wajar, namun panel bobot kustom tetap ditawarkan agar
mahasiswa yang memprioritaskan gaji atau demand dapat menyesuaikan.

## Diagram Perancangan

Diagram use case, flowchart, activity, sequence, class, DFD, dan ERD tersedia sebagai
gambar (di luar repo ini). Khusus ERD: digenerate dari skema database aktual (SQLite
hasil seed, via refleksi SQLAlchemy), bukan digambar manual, sehingga dijamin 1:1
dengan tabel yang dipakai aplikasi.
