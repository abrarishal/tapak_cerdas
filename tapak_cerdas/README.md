# TAPAK CERDAS 🏗️
## Aplikasi Web Investigasi Tanah & Perencanaan Awal Pondasi Dangkal

Aplikasi berbasis web modern untuk pengolahan data geoteknik (SPT & CPT Sondir), estimasi beban bangunan (SNI 1727:2020), dan analisis daya dukung pondasi telapak dengan 4 metode klasik (Terzaghi, Meyerhof, Vesic, Hansen).

---

## 📁 Struktur Folder Proyek
```text
tapak_cerdas/
├── app.py                      # Dashboard utama & navigasi
├── requirements.txt            # Daftar pustaka Python
├── run_app.bat                 # Peluncur 1-klik untuk Windows
├── assets/
│   └── style.css               # Desain antarmuka profesional (Slate & Navy Blue)
├── pages/
│   ├── 1_Analisis_Tanah.py     # Modul SPT, CPT & Preset Tanah Praktis
│   ├── 2_Perencanaan_Pondasi.py# Estimasi Beban SNI & Analisis Daya Dukung
│   ├── 3_Riwayat_Laporan.py    # Database & Ekspor Laporan
│   └── 4_Tentang_Aplikasi.py   # Landasan Teori & Referensi
├── modules/                    # Modul kalkulasi teknis (bertahap)
├── database/                   # Penyimpanan data proyek
└── utils/                      # Generator PDF & Excel
```

---

## 🚀 Cara Menjalankan Aplikasi

### Cara 1: Menggunakan File Batch (Paling Praktis)
Cukup klik dua kali (double-click) file:
👉 `run_app.bat`

### Cara 2: Melalui Terminal / Visual Studio Code
1. Buka folder `C:\Users\Asus\.gemini\antigravity\scratch\tapak_cerdas` di Visual Studio Code.
2. Buka Terminal (Ctrl + `).
3. Jalankan perintah:
```bash
"C:\Program Files\QGIS 3.40.7\apps\Python312\python.exe" -m streamlit run app.py
```
4. Buka tautan yang muncul di browser: `http://localhost:8501`.
