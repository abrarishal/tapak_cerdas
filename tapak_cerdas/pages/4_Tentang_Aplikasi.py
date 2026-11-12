"""
=============================================================================
TAPAK CERDAS - TENTANG APLIKASI & DOKUMENTASI TEKNIS
=============================================================================
File: pages/4_Tentang_Aplikasi.py
Deskripsi: Landasan teori geoteknik, referensi SNI 1727:2020, SNI 2847:2019,
           visualisasi 3D, serta pusat unduh Buku Panduan Penggunaan PDF.
=============================================================================
"""

import streamlit as st
import os

ROOT_DIR = os.path.dirname(os.path.dirname(__file__))

st.set_page_config(page_title="Tentang Aplikasi - TAPAK CERDAS", page_icon="📘", layout="wide")

# Muat CSS Dark
css_path = os.path.join(ROOT_DIR, "assets", "style.css")
if os.path.exists(css_path):
    with open(css_path, "r", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Top Navbar
st.html("""
<div class="top-nav">
    <div class="brand-title">
        <span>📘 Tentang Aplikasi & Dokumentasi Standar Geoteknik</span>
        <span class="brand-badge">REFERENSI TEKNIK & SNI</span>
    </div>
    <div style="font-size:0.85rem; color:#94A3B8;">
        <span>Standar Rekayasa Sipil, Geoteknik, & Struktur Beton Terpadu</span>
    </div>
</div>
""")

st.html("""
<div class="hero-banner-dark">
    <div class="hero-tag">🔬 Filosofi & Landasan Rekayasa Presisi</div>
    <h1>TAPAK CERDAS v2.0 PRO — Software Geoteknik & Struktur Terpadu</h1>
    <p>Dirancang untuk memadukan hasil pengujian penyelidikan tanah lapangan (N-SPT & CPT Sondir 2.5 Ton), pemodelan 3D geologi bawah permukaan, perhitungan pembebanan bangunan gedung SNI 1727:2020, analisis daya dukung 4 metode geoteknik (Terzaghi, Meyerhof, Vesic, Hansen), desain penulangan struktur pondasi telapak SNI 2847:2019, serta ekspor dokumen laporan Excel profesional dengan rumus aktif.</p>
</div>
""")

col_r1, col_r2 = st.columns(2)

with col_r1:
    st.html("""
    <div class="dark-card">
        <h3 style="color:#38BDF8; margin-top:0;">1. Teori Kapasitas Dukung Fondasi Dangkal</h3>
        <ul style="color:#E2E8F0; line-height:1.7; font-size:0.92rem;">
            <li><strong>Metode Terzaghi (1943):</strong> <em>Theoretical Soil Mechanics</em>. Menghitung kapasitas dukung tanah homogen berdasarkan keruntuhan geser umum dan lokal. Bersifat paling konservatif (acuan batas aman batas bawah).</li>
            <li><strong>Metode Meyerhof (1963):</strong> <em>Some Recent Research on the Bearing Capacity of Foundations</em>. Menghitung tahanan geser tanah di atas dasar fondasi sampai ke permukaan tanah serta menyertakan faktor bentuk dan kedalaman.</li>
            <li><strong>Metode Vesic (1975):</strong> <em>Analysis of Ultimate Bearing Capacity of Shallow Foundations</em>. Menggunakan sudut baji beralas (45° + φ/2) dan memperhitungkan indeks kompresibilitas massa tanah.</li>
            <li><strong>Metode Brinch Hansen (1970):</strong> <em>A Revised and Extended Formula for Bearing Capacity</em>. Solusi paling komprehensif untuk tanah kohesif murni (φ=0°) maupun tanah butiran berpasir.</li>
        </ul>
    </div>
    """)

with col_r2:
    st.html("""
    <div class="dark-card">
        <h3 style="color:#34D399; margin-top:0;">2. Standar Pembebanan Bangunan & Investigasi Tanah</h3>
        <ul style="color:#E2E8F0; line-height:1.7; font-size:0.92rem;">
            <li><strong>SNI 1727:2020:</strong> <em>Beban Desain Minimum dan Kriteria Terkait untuk Bangunan Gedung dan Struktur Lain</em>. Acuan penentuan beban hidup (Tabel 4.3-1) dan kombinasi beban terfaktor Pu = 1.2 DL + 1.6 LL.</li>
            <li><strong>ASTM D1586 / SNI 8460:2017:</strong> Uji Penetrasi Standar (SPT) dan penentuan nilai N-SPT = N2 + N3 serta korelasi sudut geser (Peck/Wolff) dan kohesi tak terdrainase (Stroud).</li>
            <li><strong>SNI 2827:2008 / ASTM D3441:</strong> Cara Uji Penetrasi Lapangan dengan Alat Sondir Bikonus 2.5 Ton dan Klasifikasi Robertson (1986).</li>
            <li><strong>Faktor Keamanan (Safety Factor / SF):</strong> Disediakan opsi 2.0; 2.5; 3.0; dan 3.5 sesuai kelas risiko konstruksi.</li>
        </ul>
    </div>
    """)

st.markdown("<br>", unsafe_allow_html=True)

col_r3, col_r4 = st.columns(2)

with col_r3:
    st.html("""
    <div class="dark-card">
        <h3 style="color:#FBBF24; margin-top:0;">3. Desain Penulangan Struktur Beton (SNI 2847:2019)</h3>
        <ul style="color:#E2E8F0; line-height:1.7; font-size:0.92rem;">
            <li><strong>Analisis Lentur Tulangan Bawah Arah X & Y:</strong> Menghitung rasio tulangan perlu ρ_req dan tulangan minimum susut-suhu ρ_min = 0.0018 x (420/fy) dengan faktor reduksi kekuatan lentur φ = 0.90.</li>
            <li><strong>Kontrol Spasi & Retak:</strong> Jarak spasi tulangan dibatasi maksimum s_max = min(3hf, 450 mm) sesuai Pasal 13.3.2.1.</li>
            <li><strong>Kontrol Geser Balok Satu Arah (One-Way Shear):</strong> Penampang kritis berjarak d dari muka kolom pedestal. Kapasitas geser φVc1 = 0.75 x 0.17 x λ x √(f'c) x L x d.</li>
            <li><strong>Kontrol Geser Pons Dua Arah (Punching Shear):</strong> Ditinjau mengelilingi perimeter kritis bo pada jarak d/2 dari muka kolom dengan 3 persamaan baku SNI Pasal 22.6.5.2.</li>
            <li><strong>Detailing & Panjang Penyaluran:</strong> Kait standar 90° dengan panjang penyaluran ldh dan Bill of Quantities (BoQ) volume beton (m³) serta berat baja (kg).</li>
        </ul>
    </div>
    """)

with col_r4:
    st.html("""
    <div class="dark-card">
        <h3 style="color:#A78BFA; margin-top:0;">4. Visualisasi 3D Interaktif & Ekspor Laporan Excel</h3>
        <ul style="color:#E2E8F0; line-height:1.7; font-size:0.92rem;">
            <li><strong>3D Cutaway Foundation Model:</strong> Model 3D fotorealistik potongan pondasi yang memperlihatkan jaring tulangan bawah X & Y, kait 90°, stek kolom (starter dowels), sengkang/begel, lantai kerja beton kurus, lubang galian bertingkat, dan muka air tanah.</li>
            <li><strong>3D Subsurface Strata Block Model:</strong> Pemodelan balok geoteknik 3D stratigrafi lapisan tanah dengan kolom silinder lubang bor (borehole) berkode warna N-SPT/qc.</li>
            <li><strong>Soil Investigation Report (5 Sheets):</strong> Dokumen Excel resmi penyelidikan tanah (General Info, Boring Log SPT, CPT Log, Soil Profile, dan Summary).</li>
            <li><strong>Foundation Calculation Report (6 Sheets):</strong> Dokumen perhitungan pondasi dengan <strong>RUMUS AKTIF EXCEL</strong> yang terhubung dinamis antar sel.</li>
        </ul>
    </div>
    """)

st.markdown("<br>", unsafe_allow_html=True)

# Unduh Buku Panduan Resmi PDF
st.markdown("### 📥 Unduh Buku Panduan Penggunaan Resmi (PDF)")

pdf_path = os.path.join(ROOT_DIR, "BUKU_PANDUAN_TAPAK_CERDAS.pdf")
if os.path.exists(pdf_path):
    with open(pdf_path, "rb") as f:
        pdf_bytes = f.read()
    
    st.download_button(
        label="📄 Unduh Buku Panduan Lengkap TAPAK CERDAS v2.0 (.pdf)",
        data=pdf_bytes,
        file_name="BUKU_PANDUAN_TAPAK_CERDAS_v2.0.pdf",
        mime="application/pdf",
        type="primary",
        use_container_width=True
    )
else:
    st.info("Buku panduan PDF sedang digenerate oleh sistem.")
