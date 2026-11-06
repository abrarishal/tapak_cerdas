"""
=============================================================================
TAPAK CERDAS - TENTANG APLIKASI & DOKUMENTASI TEKNIS
=============================================================================
File: pages/4_Tentang_Aplikasi.py
Deskripsi: Landasan teori geoteknik, referensi SNI 1727:2020, dan rumus daya dukung.
=============================================================================
"""

import streamlit as st
import os

ROOT_DIR = os.path.dirname(os.path.dirname(__file__))

st.set_page_config(page_title="Tentang Aplikasi - TAPAK CERDAS", page_icon="ℹ️", layout="wide")

# Muat CSS Dark
css_path = os.path.join(ROOT_DIR, "assets", "style.css")
if os.path.exists(css_path):
    with open(css_path, "r", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Top Navbar
st.html("""
<div class="top-nav">
    <div class="brand-title">
        <span>ℹ️ Tentang Aplikasi & Dokumentasi Standar Geoteknik</span>
        <span class="brand-badge">REFERENSI TEKNIK</span>
    </div>
    <div style="font-size:0.85rem; color:#94A3B8;">
        <span>Standar Rekayasa Sipil & Fondasi Terpadu</span>
    </div>
</div>
""")

st.html("""
<div class="hero-banner-dark">
    <div class="hero-tag">📖 Filosofi & Referensi Ilmiah</div>
    <h1>TAPAK CERDAS — Software Geoteknik Presisi</h1>
    <p>Dikembangkan untuk mempermudah insinyur geoteknik, praktisi konstruksi, dan akademisi dalam memadukan hasil pengujian tanah lapangan (SPT & CPT) dengan perhitungan pembebanan bangunan gedung SNI 1727:2020 dan analisis kapasitas dukung 4 metode utama.</p>
</div>
""")

col_r1, col_r2 = st.columns(2)

with col_r1:
    st.html("""
    <div class="dark-card">
        <h3 style="color:#38BDF8; margin-top:0;">1. Teori Daya Dukung Fondasi Dangkal</h3>
        <ul style="color:#E2E8F0; line-height:1.7; font-size:0.92rem;">
            <li><strong>Metode Terzaghi (1943):</strong> <em>Theoretical Soil Mechanics</em>, John Wiley and Sons. Menghitung kapasitas dukung tanah homogen berdasarkan keruntuhan geser umum dan lokal.</li>
            <li><strong>Metode Meyerhof (1963):</strong> <em>Some Recent Research on the Bearing Capacity of Foundations</em>, Canadian Geotechnical Journal. Menghitung tahanan geser tanah di atas dasar fondasi sampai ke permukaan.</li>
            <li><strong>Metode Vesic (1975):</strong> <em>Analysis of Ultimate Bearing Capacity of Shallow Foundations</em>. Menggunakan sudut baji beralas 45° + φ/2 dan solusi Caquot-Kerisel.</li>
            <li><strong>Metode Brinch Hansen (1970):</strong> <em>A Revised and Extended Formula for Bearing Capacity</em>. Solusi komprehensif untuk tanah kohesif (φ=0) dan tanah granular.</li>
        </ul>
    </div>
    """)

with col_r2:
    st.html("""
    <div class="dark-card">
        <h3 style="color:#34D399; margin-top:0;">2. Standar Pembebanan Bangunan & Uji Tanah</h3>
        <ul style="color:#E2E8F0; line-height:1.7; font-size:0.92rem;">
            <li><strong>SNI 1727:2020:</strong> <em>Beban Desain Minimum dan Kriteria Terkait untuk Bangunan Gedung dan Struktur Lain</em>. Acuan penentuan beban hidup (Tabel 4.3-1) dan estimasi beban mati komponen bangunan.</li>
            <li><strong>ASTM D1586 / SNI 03-2827-2008:</strong> Uji Penetrasi Standar (SPT) dan penentuan nilai N-SPT = N2 + N3.</li>
            <li><strong>ASTM D3441 / SNI 2828:2011:</strong> Uji Penetrasi Konus Mekanis (CPT / Sondir) dan rasio gesekan Rf.</li>
            <li><strong>Faktor Keamanan (Safety Factor / SF):</strong> Nilai SF = 3.0 diterapkan sebagai rasio keamanan izin konvensional pondasi dangkal.</li>
        </ul>
    </div>
    """)
