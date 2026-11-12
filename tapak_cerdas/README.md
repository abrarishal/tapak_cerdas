# TAPAK CERDAS v2.0 PRO 🏗️🔬
## Aplikasi Web Geoteknik Terpadu & Perancangan Struktur Pondasi Dangkal
**Standar Baku:** SNI 1727:2020 (Beban Gedung) | SNI 2847:2019 (Beton Struktural) | SNI 8460:2017 (Geoteknik) | ASTM D1586 (SPT) | SNI 2827:2008 (CPT)

Aplikasi rekayasa sipil berbasis web untuk penyelidikan tanah lapangan, pemodelan 3D stratigrafi bawah permukaan, komparasi kapasitas dukung 4 metode geoteknik (Terzaghi, Meyerhof, Vesic, Hansen), desain penulangan lentur & geser fondasi telapak, serta ekspor dokumen laporan Excel profesional dengan rumus aktif.

---

## 🚀 Fitur Utama & Pengembangan Baru v2.0

### 1. Modul Penyelidikan Tanah (Soil Investigation)
- **Uji Penetrasi Standar (N-SPT):** Korelasi sudut geser $\phi'$, kohesi $c_u$, berat volume $\gamma$, dan tegangan geser $\tau_f$ dengan Borelog Lapangan Nyata (UNDIP BH-4).
- **Uji Sondir Bikonus 2.5 Ton (CPT):** Klasifikasi tanah Robertson (1986) dan profil $q_c$ serta $f_s$ terhadap kedalaman.
- **Katalog Asumsi Pengguna Awam:** Estimasi tanah lapangan instan tanpa uji laboratorium.
- **Visualisasi Model Blok 3D Bawah Permukaan:** Pemodelan balok geoteknik 3D stratigrafi lapisan tanah dengan silinder borehole berwarna dan bidang muka air tanah.
- **Laporan Soil Investigation Report (5 Sheets):** General Info, Boring Log SPT (N1/N2/N3, GWL $\nabla$, grafik N-SPT), CPT Log, Soil Profile, dan Summary.

### 2. Modul Daya Dukung Fondasi Dangkal (4 Metode)
- **Estimasi Beban SNI 1727:2020:** Beban mati ($DL$), beban hidup ($LL$), beban servis ($P$), dan kombinasi terfaktor ($P_u = 1.2 DL + 1.6 LL$).
- **Faktor Keamanan (Safety Factor / SF):** Opsi fleksibel 2.0; 2.5; 3.0; dan 3.5.
- **Komparasi 4 Metode Dunia:** Terzaghi (1943), Meyerhof (1963), Vesic (1975), dan Brinch Hansen (1970).
- **Auto-Optimasi Dimensi:** Otomatis mencari dimensi tapak terkecil paling ekonomis agar seluruh 4 metode serentak aman.

### 3. Modul Desain Penulangan Struktur Fondasi (SNI 2847:2019)
- **Material:** Mutu beton $f'_c$ (17.5 - 35 MPa), mutu baja $f_y$ (280 - 520 MPa), selimut beton bersih $c_c = 75\text{ mm}$ (standar kontak tanah), diameter tulangan $D10 - D25$.
- **Pedestal & Momen:** Dimensi kolom $b_c \times h_c$, momen terfaktor $M_{ux}$ & $M_{uy}$.
- **Desain Lentur Tulangan Arah X & Y:** Menghitung $A_{s\_req}$, $A_{s\_min}$, jumlah batang $n$, spasi $s \le \min(3h_f, 450\text{ mm})$.
- **Kontrol Geser Balok 1 Arah:** Penampang kritis pada jarak $d$ dari muka kolom ($V_{u1} \le \phi V_{c1}$).
- **Kontrol Geser Pons 2 Arah (Punching Shear):** Evaluasi keliling kritis $b_o$ dengan 3 persamaan baku SNI 2847:2019 ($V_{u2} \le \phi V_{c2}$).
- **Detailing & BoQ:** Panjang penyaluran kait $90^\circ$ ($l_{dh}$), volume beton ($m^3$), total berat besi ($\text{kg}$), dan rasio $\text{kg}/m^3$.

### 4. Studio Visualisasi 3D Interaktif Cutaway
- **3D Cutaway Foundation:** Model 3D potongan pondasi fotorealistik yang memperlihatkan badan beton terpotong, jaring tulangan bawah X & Y, kait $90^\circ$, stek kolom (*starter dowels*), sengkang/begel, lantai kerja beton kurus (*blinding*), lubang galian bertingkat, dan muka air tanah.
- Rotasi $360^\circ$, *zoom in/out*, *pan*, dan *hover tooltip*.

### 5. Ekspor Dokumen Excel 6-Sheets Rumus Aktif Excel
- **Sheet 1:** Design Criteria (Input data & parameter struktur)
- **Sheet 2:** Soil Parameter (Karakteristik tanah & daya dukung)
- **Sheet 3:** Foundation Dimension Calculation (Rumus aktif $q_u, q_{\text{all}}, q_{\text{kontak}}, SF$)
- **Sheet 4:** Structural Calculation (Rumus aktif $q_u, M_u, V_{u1}, \phi V_{c1}, V_{u2}, \phi V_{c2}$)
- **Sheet 5:** Reinforcement Calculation (Rumus aktif $R_n, \rho, A_s, n, s$, berat baja)
- **Sheet 6:** Final Design Summary (Rekapitulasi desain, matriks keamanan, dan BoQ)

---

## 📁 Struktur Direktori
```text
tapak_cerdas/
├── app.py                         # Dashboard utama & inisialisasi proyek
├── BUKU_PANDUAN_TAPAK_CERDAS.pdf  # Manual penggunaan komprehensif
├── generate_manual_pdf.py         # Skrip generator buku panduan PDF
├── requirements.txt               # Dependensi Python
├── run_app.bat                    # Peluncur 1-klik lokal Windows
├── assets/
│   └── style.css                  # Desain tema Dark Slate & Navy Blue
├── database/
│   ├── data_pengguna_masuk.json   # Log input pengguna web
│   ├── db_manager.py              # Handler penyimpanan database
│   ├── projects.json              # Riwayat proyek tersimpan
│   └── Rekap_Data_Pengguna_Masuk.xlsx
├── modules/
│   ├── bearing_capacity.py        # 4 metode daya dukung geoteknik
│   ├── cpt_analyzer.py            # Analisis CPT & Robertson
│   ├── deep_foundation.py         # Komparasi bentuk fondasi
│   ├── reinforcement_design.py    # Desain penulangan SNI 2847:2019
│   ├── spt_analyzer.py            # Analisis SPT & korelasi
│   ├── subsurface_3d.py           # Model blok 3D stratigrafi tanah
│   └── visualizer.py              # Visualisasi 3D Cutaway, CAD 2D & Bulb
├── pages/
│   ├── 1_Analisis_Tanah.py        # Modul penyelidikan tanah & blok 3D
│   ├── 2_Perencanaan_Pondasi.py   # Modul beban, 4 metode, penulangan, 3D
│   ├── 3_Riwayat_Laporan.py       # Kotak masuk klien & database
│   └── 4_Tentang_Aplikasi.py      # Dokumentasi SNI & unduh panduan PDF
└── utils/
    └── excel_exporter.py          # Generator Excel 5-Sheet & 6-Sheet Aktif
```

---

## 🌐 Panduan Deploy ke GitHub & Streamlit Cloud

### Mengatasi Error `AttributeError: importlib.reload(utils.excel_exporter)`
Error tersebut terjadi karena pemanggilan debugging lokal `importlib.reload` pada lingkungan multi-threading Streamlit Cloud. 
Pada versi ini, **seluruh kode telah dibersihkan secara total** dan distandarisasi menggunakan impor Python murni.

### Langkah Update ke GitHub:
1. Salin seluruh isi folder `C:\Users\Asus\.gemini\antigravity\scratch\tapak_cerdas` ke folder repositori git lokal Anda.
2. Buka terminal git dan jalankan:
   ```bash
   git add .
   git commit -m "Update Tapak Cerdas v2.0: 3D cutaway, reinforcement design SNI 2847, 5-sheet & 6-sheet excel"
   git push origin main
   ```
3. Buka dashboard di [Streamlit Cloud](https://share.streamlit.io). Streamlit akan mendeteksi commit baru dan memperbarui aplikasi secara otomatis di `https://tapakcerdas-abrar.streamlit.app`.
4. Jika diperlukan, klik menu **Manage app** di pojok kanan bawah lalu pilih **Reboot app**.
