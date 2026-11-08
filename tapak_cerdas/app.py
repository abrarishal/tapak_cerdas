"""
=============================================================================
TAPAK CERDAS - APLIKASI WEB GEOTEKNIK & PERENCANAAN PONDASI DANGKAL
=============================================================================
File: app.py (Dashboard Utama)
Desain: Dark Slate Geotechnical Suite (Sesuai Referensi PDF)
=============================================================================
"""

import streamlit as st
import os
import sys

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

# 1. Konfigurasi Halaman Streamlit
st.set_page_config(
    page_title="Dashboard Utama - TAPAK CERDAS",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Muat Gaya CSS Dark Slate
css_path = os.path.join(os.path.dirname(__file__), "assets", "style.css")
if os.path.exists(css_path):
    with open(css_path, "r", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# 3. Inisialisasi Session State Global
if "project_info" not in st.session_state:
    st.session_state.project_info = {
        "name": "Pembangunan Ruko 3 Lantai Cerdas",
        "location": "Kawasan Komersial Mandiri",
        "engineer": "Insinyur Geoteknik / Perencana",
        "borehole_id": "BH-01",
        "water_table_depth": 1.50
    }

if "soil_params" not in st.session_state:
    st.session_state.soil_params = {
        "status": "Siap Digunakan",
        "source": "Katalog Lapangan Praktis",
        "soil_type": "Tanah Lempung Sedang / Teguh",
        "cohesion": 35.0,
        "friction_angle": 12.0,
        "unit_weight": 17.5,
        "sat_unit_weight": 19.0,
        "water_table": 1.50
    }

if "spt_layers" not in st.session_state:
    st.session_state.spt_layers = [
        {"depth_top": 0.0, "depth_bot": 1.5, "n1": 3, "n2": 4, "n3": 4, "n_spt": 8, "n60": 6.7, "phi": 0.0, "c": 40.0, "gamma": 16.2, "gamma_sat": 17.7, "soil_type": "Lempung (Cohesive)", "konsistensi": "Sedang / Teguh", "interval_str": "0.0 - 1.5 m"},
        {"depth_top": 1.5, "depth_bot": 3.5, "n1": 6, "n2": 9, "n3": 9, "n_spt": 18, "n60": 15.3, "phi": 31.6, "c": 0.0, "gamma": 17.7, "gamma_sat": 19.5, "soil_type": "Pasir (Granular)", "konsistensi": "Kepadatan Sedang", "interval_str": "1.5 - 3.5 m"},
        {"depth_top": 3.5, "depth_bot": 6.0, "n1": 10, "n2": 16, "n3": 16, "n_spt": 32, "n60": 30.4, "phi": 35.8, "c": 0.0, "gamma": 19.3, "gamma_sat": 21.1, "soil_type": "Pasir (Granular)", "konsistensi": "Padat", "interval_str": "3.5 - 6.0 m"}
    ]

if "cpt_points" not in st.session_state:
    st.session_state.cpt_points = [
        {"depth": 0.5, "qc_kg": 15.0, "fs_kg": 0.60, "qc_kpa": 1471.0, "fs_kpa": 58.8, "rf_pct": 4.0, "soil_type": "Lempung Lanauan", "phi": 0.0, "c": 35.0, "gamma": 16.5},
        {"depth": 1.0, "qc_kg": 22.0, "fs_kg": 0.85, "qc_kpa": 2157.5, "fs_kpa": 83.4, "rf_pct": 3.86, "soil_type": "Lempung Lanauan", "phi": 0.0, "c": 48.0, "gamma": 17.0},
        {"depth": 1.5, "qc_kg": 30.0, "fs_kg": 1.05, "qc_kpa": 2942.1, "fs_kpa": 103.0, "rf_pct": 3.5, "soil_type": "Lempung Lanauan", "phi": 0.0, "c": 62.0, "gamma": 17.5},
        {"depth": 2.0, "qc_kg": 65.0, "fs_kg": 0.90, "qc_kpa": 6374.5, "fs_kpa": 88.3, "rf_pct": 1.38, "soil_type": "Pasir Kelanauan", "phi": 33.5, "c": 0.0, "gamma": 18.5},
        {"depth": 3.0, "qc_kg": 110.0, "fs_kg": 1.10, "qc_kpa": 10787.7, "fs_kpa": 107.9, "rf_pct": 1.0, "soil_type": "Pasir Bersih", "phi": 36.0, "c": 0.0, "gamma": 19.5}
    ]

if "load_params" not in st.session_state:
    st.session_state.load_params = {
        "status": "Tersedia (Estimasi Otomatis)",
        "building_function": "Toko / Bangunan Komersial / Retail (4.79 kN/m²)",
        "floors": 3,
        "floor_area": 120.0,
        "total_area": 360.0,
        "dead_load_unit": 7.85,
        "live_load_unit": 4.79,
        "p_column": 464.5,
        "pu_column": 627.8
    }

# 4. Top Navbar Dark Persis PDF
col_top1, col_top2 = st.columns([3, 1])
with col_top1:
    st.html("""
    <div style="display:flex; align-items:center; gap:12px; margin-bottom:8px;">
        <span style="font-weight:850; font-size:1.3rem; color:#FFFFFF;">Tapak Cerdas</span>
        <span class="brand-badge">v1.4 PRO METRIK</span>
        <span style="font-size:0.85rem; color:#94A3B8; font-weight:500;">| Software Geoteknik & Perancangan Daya Dukung Fondasi Dangkal</span>
    </div>
    """)
with col_top2:
    c_btn_rpt1, c_btn_rpt2 = st.columns([1.8, 1.2])
    with c_btn_rpt1:
        st.html("<div style='font-size:0.8rem; color:#38BDF8; font-weight:600; text-align:right; margin-top:6px;'>📘 Acuan Standard: SNI 1727:2020 & Textbook Geoteknik</div>")
    with c_btn_rpt2:
        if st.button("🖨️ Cetak Laporan", use_container_width=True):
            st.switch_page("pages/3_Riwayat_Laporan.py")

# Sub-Navbar Horizontal Tabs Persis PDF
c_nav1, c_nav2, c_nav3, c_nav4 = st.columns(4)
with c_nav1:
    st.button("🏠 Dashboard Utama", type="primary", use_container_width=True)
with c_nav2:
    if st.button("🔬 1. Korelasi N-SPT / CPT & Stratigrafi", use_container_width=True):
        st.switch_page("pages/1_Analisis_Tanah.py")
with c_nav3:
    if st.button("🏛️ 2. Analisis Beban & 4 Metode Fondasi", use_container_width=True):
        st.switch_page("pages/2_Perencanaan_Pondasi.py")
with c_nav4:
    if st.button("📑 3. Riwayat / Masuk Klien", use_container_width=True):
        st.switch_page("pages/3_Riwayat_Laporan.py")

st.markdown("<div style='margin-bottom: 1.2rem;'></div>", unsafe_allow_html=True)

# 5. Sidebar Navigasi
with st.sidebar:
    st.markdown("### 🧭 **Menu Navigasi**")
    st.caption("Pilih halaman untuk berpindah modul:")
    
    st.markdown("---")
    st.markdown("#### 📋 Profil Proyek Aktif")
    proj_name = st.text_input("Nama Proyek:", value=st.session_state.project_info["name"])
    proj_loc = st.text_input("Lokasi:", value=st.session_state.project_info["location"])
    st.session_state.project_info["name"] = proj_name
    st.session_state.project_info["location"] = proj_loc
    
    st.markdown("---")
    st.caption("© 2026 TAPAK CERDAS PRO")

# 6. Hero Banner Dark Mode dengan Interactive Blueprint Terminal
st.html(r"""
<div class="hero-banner-dark">
    <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:10px;">
        <div class="hero-tag">⚡ AUTONOMOUS GEOTECHNICAL ENGINE &bull; CAD SUITE V1.4</div>
        <div style="font-family:'JetBrains Mono',monospace; font-size:0.75rem; color:#00E5FF; background:rgba(0,229,255,0.1); padding:4px 12px; border-radius:6px; border:1px solid rgba(0,229,255,0.3);">
            ● LIVE CLOUD SYSTEM &bull; SNI 1727:2020 & 2827:2008
        </div>
    </div>
    <h1>Perancangan Daya Dukung Fondasi Dangkal Otomatis, Presisi & Efisien</h1>
    <p>Aplikasi Tapak Cerdas mengintegrasikan penyelidikan tanah geoteknik (Boring N-SPT & Sondir CPT), estimasi otomatis beban bangunan bertingkat sesuai SNI 1727:2020, serta komparasi 4 teori daya dukung klasik: <strong>Terzaghi (1943), Meyerhof (1963), Vesic (1975), dan Hansen (1970)</strong> dalam antarmuka grafis 3D interaktif.</p>
</div>
""")

# ALUR KERJA REKAYASA INTERAKTIF (WORKFLOW MAP)
st.html("""
<div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(220px, 1fr)); gap:14px; margin-bottom:1.6rem;">
    <div class="dark-card" style="border-left:4px solid #38BDF8; padding:14px 18px; margin-bottom:0;">
        <div style="font-size:0.75rem; color:#94A3B8; font-weight:800; text-transform:uppercase;">Tahap 1 &bull; Penyelidikan</div>
        <div style="font-weight:800; color:#38BDF8; font-size:1.05rem; margin-top:2px;">🔬 Analisis Tanah</div>
        <div style="font-size:0.8rem; color:#CBD5E1; margin-top:4px;">Uji N-SPT, Bore Log Undip, Sondir CPT Bikonus, & Interpolasi c, φ, γ.</div>
    </div>
    <div class="dark-card" style="border-left:4px solid #F59E0B; padding:14px 18px; margin-bottom:0;">
        <div style="font-size:0.75rem; color:#94A3B8; font-weight:800; text-transform:uppercase;">Tahap 2 &bull; Struktur</div>
        <div style="font-weight:800; color:#FBBF24; font-size:1.05rem; margin-top:2px;">🏢 Beban SNI 1727</div>
        <div style="font-size:0.8rem; color:#CBD5E1; margin-top:4px;">Estimasi otomatis beban mati & hidup gedung bertingkat per kolom kritis.</div>
    </div>
    <div class="dark-card" style="border-left:4px solid #00E5FF; padding:14px 18px; margin-bottom:0;">
        <div style="font-size:0.75rem; color:#94A3B8; font-weight:800; text-transform:uppercase;">Tahap 3 &bull; Desain CAD</div>
        <div style="font-weight:800; color:#00E5FF; font-size:1.05rem; margin-top:2px;">🏛️ Studio 3D Fondasi</div>
        <div style="font-size:0.8rem; color:#CBD5E1; margin-top:4px;">Simulasi 3D Silinder/Persegi/Jalur, 4 metode daya dukung & Boussinesq.</div>
    </div>
    <div class="dark-card" style="border-left:4px solid #10B981; padding:14px 18px; margin-bottom:0;">
        <div style="font-size:0.75rem; color:#94A3B8; font-weight:800; text-transform:uppercase;">Tahap 4 &bull; Selesai</div>
        <div style="font-weight:800; color:#34D399; font-size:1.05rem; margin-top:2px;">📊 Laporan & Excel</div>
        <div style="font-size:0.8rem; color:#CBD5E1; margin-top:4px;">Ekspor lembar kalkulasi resmi .xlsx, CSV, & kotak masuk pengajuan klien.</div>
    </div>
</div>
""")

# Tombol Navigasi Aksi Cepat
c_btn1, c_btn2 = st.columns(2)
with c_btn1:
    if st.button("🔬 1. Mulai Input Data Tanah (SPT & CPT) ➜", type="primary", use_container_width=True):
        st.switch_page("pages/1_Analisis_Tanah.py")

with c_btn2:
    if st.button("🏛️ 2. Langsung Perhitungan & Simulasi 3D ➜", type="secondary", use_container_width=True):
        st.switch_page("pages/2_Perencanaan_Pondasi.py")

st.markdown("<br>", unsafe_allow_html=True)

# 7. Empat Kartu Metrik Dark Mode Sesuai Halaman 1 PDF
col_m1, col_m2, col_m3, col_m4 = st.columns(4)

with col_m1:
    st.html("""
    <div class="metric-tile-dark" style="border-top-color: #EC4899;">
        <div class="tile-tag-dark" style="color: #F472B6;">Teori Geoteknik</div>
        <div class="tile-val-dark">4 Metode</div>
        <div class="tile-sub-dark">Terzaghi, Meyerhof, Vesic, Hansen</div>
    </div>
    """)

with col_m2:
    st.html("""
    <div class="metric-tile-dark cyan">
        <div class="tile-tag-dark" style="color: #38BDF8;">Acuan Pembebanan</div>
        <div class="tile-val-dark" style="font-size: 1.45rem;">SNI 1727:2020</div>
        <div class="tile-sub-dark">Kombinasi DL & LL SNI Terkini</div>
    </div>
    """)

with col_m3:
    st.html("""
    <div class="metric-tile-dark emerald">
        <div class="tile-tag-dark" style="color: #34D399;">Faktor Aman (SF)</div>
        <div class="tile-val-dark">SF = 3.0</div>
        <div class="tile-sub-dark">Standar Fondasi Dangkal Aman</div>
    </div>
    """)

with col_m4:
    st.html(r"""
    <div class="metric-tile-dark amber">
        <div class="tile-tag-dark" style="color: #FBBF24;">Optimasi Material</div>
        <div class="tile-val-dark" style="font-size: 1.45rem;">Auto B &times; L</div>
        <div class="tile-sub-dark">Mencari volume beton paling hemat</div>
    </div>
    """)

st.markdown("---")

# 8. Ringkasan Status Proyek
st.markdown("### 📌 Status Ringkasan Proyek Saat Ini")

col_sum1, col_sum2 = st.columns(2)

with col_sum1:
    st.html(f"""
    <div class="dark-card">
        <div style="font-weight:750; color:#38BDF8; font-size:1.1rem; margin-bottom:0.8rem;">🌍 Parameter Tanah Aktif</div>
        <table style="width:100%; font-size:0.9rem; color:#E2E8F0;">
            <tr><td style="color:#94A3B8; padding:4px 0;">Jenis Tanah:</td><td><strong>{st.session_state.soil_params['soil_type']}</strong></td></tr>
            <tr><td style="color:#94A3B8; padding:4px 0;">Kohesi (c):</td><td><strong>{st.session_state.soil_params['cohesion']} kPa</strong></td></tr>
            <tr><td style="color:#94A3B8; padding:4px 0;">Sudut Geser (φ):</td><td><strong>{st.session_state.soil_params['friction_angle']}°</strong></td></tr>
            <tr><td style="color:#94A3B8; padding:4px 0;">Berat Isi (γ):</td><td><strong>{st.session_state.soil_params['unit_weight']} kN/m³</strong></td></tr>
            <tr><td style="color:#94A3B8; padding:4px 0;">Muka Air Tanah (dw):</td><td><strong style="color:#06B6D4;">{st.session_state.project_info['water_table_depth']} meter</strong></td></tr>
        </table>
    </div>
    """)

with col_sum2:
    p_kol = st.session_state.load_params['p_column']
    st.html(f"""
    <div class="dark-card">
        <div style="font-weight:750; color:#34D399; font-size:1.1rem; margin-bottom:0.8rem;">🏢 Estimasi Pembebanan Bangunan</div>
        <table style="width:100%; font-size:0.9rem; color:#E2E8F0;">
            <tr><td style="color:#94A3B8; padding:4px 0;">Fungsi Gedung:</td><td><strong>{st.session_state.load_params['building_function']}</strong></td></tr>
            <tr><td style="color:#94A3B8; padding:4px 0;">Jumlah Lantai:</td><td><strong>{st.session_state.load_params['floors']} Lantai</strong></td></tr>
            <tr><td style="color:#94A3B8; padding:4px 0;">Luas per Lantai:</td><td><strong>{st.session_state.load_params['floor_area']} m²</strong></td></tr>
            <tr><td style="color:#94A3B8; padding:4px 0;">Beban Kolom Rencana (P):</td><td><strong style="color:#FBBF24;">{p_kol:.1f} kN (~{p_kol/9.81:.1f} Ton)</strong></td></tr>
            <tr><td style="color:#94A3B8; padding:4px 0;">Beban Terfaktor (Pu):</td><td><strong>{st.session_state.load_params['pu_column']:.1f} kN (1.2D + 1.6L)</strong></td></tr>
        </table>
    </div>
    """)
