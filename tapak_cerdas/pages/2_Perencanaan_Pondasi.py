"""
=============================================================================
TAPAK CERDAS - MODUL PERENCANAAN BEBAN & 4 METODE FONDASI
=============================================================================
File: pages/2_Perencanaan_Pondasi.py
Deskripsi: Estimasi Beban Bangunan (Luas Bangunan per Lantai & Grid Kolom),
           Komparasi 4 Metode Daya Dukung (Terzaghi, Meyerhof, Vesic, Hansen),
           Pilihan Bentuk Fondasi (Bujur Sangkar, Persegi Panjang, Lingkaran, Strip),
           Sistem Penilai Cerdas Bentuk Fondasi Paling Efisien,
           Evaluasi Kelayakan Geoteknik: Fondasi Dangkal vs. Fondasi Dalam (Deep Foundation),
           Sketsa Potongan Teknik 2D, serta Ekspor Excel (.xlsx) & CSV.
=============================================================================
"""

import streamlit as st
import pandas as pd
import numpy as np
import os
import sys
import math
import urllib.parse

# Tambahkan path root
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from modules.bearing_capacity import calculate_terzaghi, calculate_meyerhof, calculate_vesic, calculate_hansen
from modules.reinforcement_design import design_footing_reinforcement
from modules.visualizer import (
    plot_foundation_3d,
    plot_cutaway_foundation_3d,
    plot_foundation_plan_view,
    plot_foundation_cross_section,
    plot_boussinesq_stress_bulb,
    plot_safety_gauge
)
from modules.deep_foundation import compare_foundation_shapes
from utils.excel_exporter import generate_excel_report, generate_csv_report
from database.db_manager import save_client_submission

# Konfigurasi Halaman
st.set_page_config(page_title="Analisis Beban & 4 Metode Fondasi Dangkal - TAPAK CERDAS", page_icon="🏛️", layout="wide")

# Muat CSS Dark
css_path = os.path.join(ROOT_DIR, "assets", "style.css")
if os.path.exists(css_path):
    with open(css_path, "r", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Top Navbar Sesuai Format PDF Halaman 2 & 3
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
    if st.button("🏠 Dashboard Utama", use_container_width=True):
        st.switch_page("app.py")
with c_nav2:
    if st.button("🔬 1. Korelasi N-SPT / CPT & Stratigrafi", use_container_width=True):
        st.switch_page("pages/1_Analisis_Tanah.py")
with c_nav3:
    st.button("🏛️ 2. Analisis Beban & 4 Metode Fondasi", type="primary", use_container_width=True)
with c_nav4:
    if st.button("📑 3. Riwayat / Masuk Klien", use_container_width=True):
        st.switch_page("pages/3_Riwayat_Laporan.py")

st.markdown("<div style='margin-bottom: 1rem;'></div>", unsafe_allow_html=True)

# LAYOUT DUA KOLOM BESAR
col_left, col_right = st.columns([1.15, 1.45])

# =========================================================================
# KOLOM KIRI: INPUT PEMBEBANAN GEDUNG & PARAMETER FONDASI
# =========================================================================
with col_left:
    st.markdown("### 🏢 Estimasi Beban Gedung (SNI 1727:2020)")
    
    BEBAN_HIDUP_SNI = {
        "Rumah Tinggal / Hunian Privat (1.92 kN/m²)": 1.92,
        "Ruang Kantor (2.40 kN/m²)": 2.40,
        "Sekolah / Ruang Kelas (1.92 kN/m²)": 1.92,
        "Toko / Bangunan Komersial / Retail (4.79 kN/m²)": 4.79,
        "Restoran / Tempat Makan (4.79 kN/m²)": 4.79,
        "Rumah Sakit / Ruang Pasien (1.92 kN/m²)": 1.92,
        "Gedung Pertemuan / Aula (4.79 kN/m²)": 4.79,
        "Gudang Kategori Ringan (6.00 kN/m²)": 6.00,
        "Gudang Kategori Berat (11.97 kN/m²)": 11.97
    }

    fungsi_bldg = st.selectbox("Fungsi Bangunan Gedung:", list(BEBAN_HIDUP_SNI.keys()), index=0)
    ll_val = BEBAN_HIDUP_SNI[fungsi_bldg]

    # REVISI PENGGUNA: Ganti Luas Tributari dengan Luas Bangunan per Lantai & Grid Kolom
    c_b1, c_b2 = st.columns(2)
    with c_b1:
        jml_lantai = st.number_input("Jumlah Lantai Gedung:", min_value=1, max_value=10, value=2, step=1)
    with c_b2:
        luas_bangunan_m2 = st.number_input(
            "Luas Bangunan per Lantai (m²):",
            min_value=20.0, max_value=2500.0, value=100.0, step=10.0,
            help="Total luas tapak bangunan 1 lantai. Contoh: Rumah 10m × 10m = 100 m², Ruko 5m × 15m = 75 m²"
        )

    grid_pilihan = st.selectbox(
        "Estimasi Pola Grid / Bentang Kolom (m):",
        [
            "4.0 m × 4.0 m (Standar Ruko & Rumah Tinggal — Kolom Sedang)",
            "3.0 m × 3.0 m (Rumah Sederhana / Grid Kolom Rapat)",
            "5.0 m × 5.0 m (Gedung Kantor / Toko Komersial)",
            "6.0 m × 6.0 m (Bentang Lebar / Showroom / Gudang)",
            "Kustom Bentang Manual"
        ],
        index=0
    )

    if grid_pilihan == "Kustom Bentang Manual":
        c_k1, c_k2 = st.columns(2)
        bentang_x = c_k1.number_input("Bentang Kolom X (m):", min_value=2.0, max_value=12.0, value=4.0, step=0.5)
        bentang_y = c_k2.number_input("Bentang Kolom Y (m):", min_value=2.0, max_value=12.0, value=4.0, step=0.5)
        luas_trib = bentang_x * bentang_y
    else:
        if "3.0 m" in grid_pilihan:
            luas_trib = 9.0
            span_desc = "3.0 m × 3.0 m"
        elif "5.0 m" in grid_pilihan:
            luas_trib = 25.0
            span_desc = "5.0 m × 5.0 m"
        elif "6.0 m" in grid_pilihan:
            luas_trib = 36.0
            span_desc = "6.0 m × 6.0 m"
        else:
            luas_trib = 16.0
            span_desc = "4.0 m × 4.0 m"

    # Perhitungan Beban Struktur SNI 1727:2020
    dl_val = 5.50  # kN/m2 (Pelat beton 12cm + spesi + keramik + plafon + utilitas)
    total_load_m2 = dl_val + ll_val
    est_num_columns = max(4, math.ceil(luas_bangunan_m2 / luas_trib))
    total_gedung_p = luas_bangunan_m2 * jml_lantai * total_load_m2
    total_beban_aksial_p = luas_trib * jml_lantai * total_load_m2
    pu_terfaktor = luas_trib * jml_lantai * (1.2 * dl_val + 1.6 * ll_val)

    st.html(f"""
    <div class="dark-card" style="margin-top:10px; padding:12px 16px;">
        <div style="display:flex; justify-content:space-between; font-size:0.85rem; color:#94A3B8; margin-bottom:4px;">
            <span>Luas Total Lantai & Beban per m²:</span>
            <strong style="color:#F8FAFC;">{luas_bangunan_m2:.0f} m² &times; {jml_lantai} Lantai ({total_load_m2:.2f} kN/m²)</strong>
        </div>
        <div style="display:flex; justify-content:space-between; font-size:0.85rem; color:#94A3B8; margin-bottom:4px;">
            <span>Perkiraan Total Titik Kolom Gedung:</span>
            <strong style="color:#38BDF8;">&plusmn; {est_num_columns} Titik Kolom (Area pikul {luas_trib:.1f} m²/kolom)</strong>
        </div>
        <div style="display:flex; justify-content:space-between; font-size:0.85rem; color:#94A3B8; margin-bottom:8px;">
            <span>Total Beban Seluruh Gedung:</span>
            <strong style="color:#A78BFA;">{total_gedung_p:.1f} kN (~{total_gedung_p/9.81:.1f} Ton)</strong>
        </div>
        <div style="display:flex; justify-content:space-between; align-items:center; border-top:1px solid #334155; padding-top:8px;">
            <span style="font-weight:750; color:#E2E8F0; font-size:0.95rem;">Beban Aksial Kolom Kritis (P):</span>
            <span style="font-size:1.35rem; font-weight:800; color:#FBBF24;">{total_beban_aksial_p:.2f} kN <span style="font-size:0.8rem; color:#94A3B8;">(~{total_beban_aksial_p/9.81:.1f} Ton)</span></span>
        </div>
    </div>
    """)

    st.markdown("---")

    st.markdown("### ⚠️ Parameter Tanah & Rencana Fondasi")
    
    soil = st.session_state.soil_params
    c_s1, c_s2 = st.columns(2)
    with c_s1:
        phi_in = st.number_input("Sudut Geser (φ°):", value=float(soil.get("friction_angle", 28.0)), step=1.0)
        gamma_in = st.number_input("Berat Isi (γ kN/m³):", value=float(soil.get("unit_weight", 17.5)), step=0.5)
        df_in = st.number_input("Kedalaman Fondasi Df (m):", min_value=0.5, max_value=5.0, value=1.5, step=0.1)
    with c_s2:
        c_in = st.number_input("Kohesi (c kPa):", value=float(soil.get("cohesion", 18.0)), step=1.0)
        dw_in = st.number_input("Muka Air Tanah dw (m):", min_value=0.0, max_value=20.0, value=float(st.session_state.project_info.get("water_table_depth", 1.5)), step=0.25)
        sf_in = st.selectbox("Safety Factor (SF):", [2.0, 2.5, 3.0, 3.5], index=2)

    gamma_sat_in = gamma_in + 1.8
    
    # Input Tebal Fondasi & Parameter Struktur SNI 2847:2019
    hf = st.slider("Tebal Pelat Fondasi hf (m):", min_value=0.30, max_value=1.20, value=0.45, step=0.05)

    with st.expander("🏗️ Data Material Struktur & Kolom Pedestal (SNI 2847:2019)", expanded=False):
        c_mat1, c_mat2 = st.columns(2)
        with c_mat1:
            fc_val = st.selectbox("Mutu Beton f'c (MPa):", [20.0, 25.0, 30.0, 35.0], index=1)
            fy_val = st.selectbox("Mutu Baja Tulangan fy (MPa):", [280.0, 420.0], index=1)
            cover_val = st.number_input("Selimut Beton Bersih (mm):", min_value=50.0, max_value=100.0, value=75.0, step=5.0)
        with c_mat2:
            bar_dia_val = st.selectbox("Diameter Tulangan Lentur (D):", [13.0, 16.0, 19.0, 22.0, 25.0], index=1)
            col_b_val = st.number_input("Lebar Kolom Pedestal bc (m):", min_value=0.20, max_value=1.50, value=0.40, step=0.05)
            col_h_val = st.number_input("Panjang Kolom Pedestal hc (m):", min_value=0.20, max_value=1.50, value=0.40, step=0.05)
        c_mom1, c_mom2 = st.columns(2)
        with c_mom1:
            mux_val = st.number_input("Momen Terfaktor Mux (kN.m):", value=15.0, step=2.5)
        with c_mom2:
            muy_val = st.number_input("Momen Terfaktor Muy (kN.m):", value=10.0, step=2.5)

    # REVISI PENGGUNA: Dukungan Berbagai Bentuk Fondasi
    st.markdown("#### 📐 Pilihan Bentuk & Geometri Fondasi:")
    bentuk_fondasi = st.selectbox(
        "Pilih Bentuk Fondasi:",
        [
            "⏹️ Bujur Sangkar (Square Footing — B = L)",
            "▭ Persegi Panjang (Rectangular Footing — B ≠ L)",
            "⭕ Lingkaran (Circular Footing — Diameter D)",
            "🧱 Pondasi Jalur / Menerus (Strip Footing)"
        ],
        index=0
    )

    mode_dimensi = st.radio("Mode Penentuan Dimensi:", ["⚡ Auto-Optimasi Dimensi (Rekomendasi Cerdas)", "✏️ Input Manual Dimensi"], horizontal=True)

    # Logika Penentuan Dimensi Berdasarkan Bentuk & Mode
    if "Bujur Sangkar" in bentuk_fondasi:
        shape_code = "Bujur Sangkar"
        if mode_dimensi == "⚡ Auto-Optimasi Dimensi (Rekomendasi Cerdas)":
            lebar_b = 0.80
            while lebar_b <= 4.0:
                panjang_l = lebar_b
                res_tz_t = calculate_terzaghi(c_in, phi_in, gamma_in, gamma_sat_in, lebar_b, panjang_l, df_in, dw_in, shape="Bujur Sangkar")
                res_my_t = calculate_meyerhof(c_in, phi_in, gamma_in, gamma_sat_in, lebar_b, panjang_l, df_in, dw_in, shape="Bujur Sangkar")
                res_vs_t = calculate_vesic(c_in, phi_in, gamma_in, gamma_sat_in, lebar_b, panjang_l, df_in, dw_in, shape="Bujur Sangkar")
                res_hs_t = calculate_hansen(c_in, phi_in, gamma_in, gamma_sat_in, lebar_b, panjang_l, df_in, dw_in, shape="Bujur Sangkar")
                
                area_t = lebar_b * panjang_l
                q_k_t = (total_beban_aksial_p / area_t) + (24.0 * hf) + (gamma_in * (df_in - hf))
                
                if all((q_k_t <= (it["qu"] - it["po"]) / sf_in + it["po"]) for it in [res_tz_t, res_my_t, res_vs_t, res_hs_t]):
                    break
                lebar_b += 0.05
            lebar_b = round(min(4.0, lebar_b), 2)
            panjang_l = lebar_b
            area_f = lebar_b * panjang_l
            st.caption(f"💡 Sistem memilih dimensi optimal: **B = {lebar_b:.2f} m &times; L = {panjang_l:.2f} m**")
        else:
            lebar_b = st.slider("Lebar & Panjang Sisi B = L (m):", min_value=0.8, max_value=4.0, value=1.50, step=0.05)
            panjang_l = lebar_b
            area_f = lebar_b * panjang_l

    elif "Persegi Panjang" in bentuk_fondasi:
        shape_code = "Persegi Panjang"
        if mode_dimensi == "⚡ Auto-Optimasi Dimensi (Rekomendasi Cerdas)":
            lebar_b = 0.80
            while lebar_b <= 3.5:
                panjang_l = round(lebar_b * 1.4, 2)
                res_tz_t = calculate_terzaghi(c_in, phi_in, gamma_in, gamma_sat_in, lebar_b, panjang_l, df_in, dw_in, shape="Persegi Panjang")
                res_my_t = calculate_meyerhof(c_in, phi_in, gamma_in, gamma_sat_in, lebar_b, panjang_l, df_in, dw_in, shape="Persegi Panjang")
                res_vs_t = calculate_vesic(c_in, phi_in, gamma_in, gamma_sat_in, lebar_b, panjang_l, df_in, dw_in, shape="Persegi Panjang")
                res_hs_t = calculate_hansen(c_in, phi_in, gamma_in, gamma_sat_in, lebar_b, panjang_l, df_in, dw_in, shape="Persegi Panjang")
                
                area_t = lebar_b * panjang_l
                q_k_t = (total_beban_aksial_p / area_t) + (24.0 * hf) + (gamma_in * (df_in - hf))
                
                if all((q_k_t <= (it["qu"] - it["po"]) / sf_in + it["po"]) for it in [res_tz_t, res_my_t, res_vs_t, res_hs_t]):
                    break
                lebar_b += 0.05
            lebar_b = round(min(3.5, lebar_b), 2)
            panjang_l = round(lebar_b * 1.4, 2)
            area_f = lebar_b * panjang_l
            st.caption(f"💡 Sistem memilih dimensi optimal: **B = {lebar_b:.2f} m &times; L = {panjang_l:.2f} m**")
        else:
            c_dim1, c_dim2 = st.columns(2)
            lebar_b = c_dim1.slider("Lebar B (m):", min_value=0.8, max_value=3.5, value=1.20, step=0.05)
            panjang_l = c_dim2.slider("Panjang L (m):", min_value=lebar_b, max_value=5.0, value=max(lebar_b, 1.80), step=0.05)
            area_f = lebar_b * panjang_l

    elif "Lingkaran" in bentuk_fondasi:
        shape_code = "Lingkaran"
        if mode_dimensi == "⚡ Auto-Optimasi Dimensi (Rekomendasi Cerdas)":
            diameter_d = 0.90
            while diameter_d <= 4.5:
                area_t = (math.pi / 4.0) * (diameter_d ** 2)
                res_tz_t = calculate_terzaghi(c_in, phi_in, gamma_in, gamma_sat_in, diameter_d, diameter_d, df_in, dw_in, shape="Lingkaran")
                res_my_t = calculate_meyerhof(c_in, phi_in, gamma_in, gamma_sat_in, diameter_d, diameter_d, df_in, dw_in, shape="Lingkaran")
                res_vs_t = calculate_vesic(c_in, phi_in, gamma_in, gamma_sat_in, diameter_d, diameter_d, df_in, dw_in, shape="Lingkaran")
                res_hs_t = calculate_hansen(c_in, phi_in, gamma_in, gamma_sat_in, diameter_d, diameter_d, df_in, dw_in, shape="Lingkaran")
                
                q_k_t = (total_beban_aksial_p / area_t) + (24.0 * hf) + (gamma_in * (df_in - hf))
                if all((q_k_t <= (it["qu"] - it["po"]) / sf_in + it["po"]) for it in [res_tz_t, res_my_t, res_vs_t, res_hs_t]):
                    break
                diameter_d += 0.05
            diameter_d = round(min(4.5, diameter_d), 2)
            lebar_b = diameter_d
            panjang_l = diameter_d
            area_f = (math.pi / 4.0) * (diameter_d ** 2)
            st.caption(f"💡 Sistem memilih diameter optimal: **Diameter D = {diameter_d:.2f} m** (Luas Kontak = {area_f:.2f} m²)")
        else:
            diameter_d = st.slider("Diameter Fondasi D (m):", min_value=0.8, max_value=4.5, value=1.60, step=0.05)
            lebar_b = diameter_d
            panjang_l = diameter_d
            area_f = (math.pi / 4.0) * (diameter_d ** 2)

    else:  # Pondasi Jalur / Menerus
        shape_code = "Memanjang"
        # Untuk jalur, beban dihitung per meter lari
        beban_per_meter = total_beban_aksial_p / 4.0
        if mode_dimensi == "⚡ Auto-Optimasi Dimensi (Rekomendasi Cerdas)":
            lebar_b = 0.60
            while lebar_b <= 3.0:
                area_t = lebar_b * 1.0
                res_tz_t = calculate_terzaghi(c_in, phi_in, gamma_in, gamma_sat_in, lebar_b, 10.0, df_in, dw_in, shape="Memanjang")
                res_my_t = calculate_meyerhof(c_in, phi_in, gamma_in, gamma_sat_in, lebar_b, 10.0, df_in, dw_in, shape="Memanjang")
                res_vs_t = calculate_vesic(c_in, phi_in, gamma_in, gamma_sat_in, lebar_b, 10.0, df_in, dw_in, shape="Memanjang")
                res_hs_t = calculate_hansen(c_in, phi_in, gamma_in, gamma_sat_in, lebar_b, 10.0, df_in, dw_in, shape="Memanjang")
                
                q_k_t = (beban_per_meter / area_t) + (24.0 * hf) + (gamma_in * (df_in - hf))
                if all((q_k_t <= (it["qu"] - it["po"]) / sf_in + it["po"]) for it in [res_tz_t, res_my_t, res_vs_t, res_hs_t]):
                    break
                lebar_b += 0.05
            lebar_b = round(min(3.0, lebar_b), 2)
            panjang_l = 1.0  # per meter panjang
            area_f = lebar_b * 1.0
            st.caption(f"💡 Sistem memilih lebar jalur: **B = {lebar_b:.2f} m** (per meter lari)")
        else:
            lebar_b = st.slider("Lebar Jalur B (m):", min_value=0.5, max_value=3.0, value=0.80, step=0.05)
            panjang_l = 1.0
            area_f = lebar_b * 1.0


# =========================================================================
# KOLOM KANAN: HASIL KOMPARASI 4 METODE, SISTEM PENILAI & EVALUASI FONDASI DALAM
# =========================================================================
with col_right:
    # Tegangan Kontak Dasar Fondasi (q_kontak)
    if shape_code == "Memanjang":
        beban_eval = total_beban_aksial_p / 4.0
    else:
        beban_eval = total_beban_aksial_p
        
    q_kontak = (beban_eval / area_f) + (24.0 * hf) + (gamma_in * (df_in - hf))

    # Hitung ke-4 metode
    res_tz = calculate_terzaghi(c_in, phi_in, gamma_in, gamma_sat_in, lebar_b, panjang_l, df_in, dw_in, shape=shape_code)
    res_my = calculate_meyerhof(c_in, phi_in, gamma_in, gamma_sat_in, lebar_b, panjang_l, df_in, dw_in, shape=shape_code)
    res_vs = calculate_vesic(c_in, phi_in, gamma_in, gamma_sat_in, lebar_b, panjang_l, df_in, dw_in, shape=shape_code)
    res_hs = calculate_hansen(c_in, phi_in, gamma_in, gamma_sat_in, lebar_b, panjang_l, df_in, dw_in, shape=shape_code)
    
    comp_list = [res_tz, res_my, res_vs, res_hs]
    table_comp = []
    
    all_methods_ok = True
    for item in comp_list:
        qu = item["qu"]
        po = item["po"]
        qun = qu - po
        qall = (qun / sf_in) + po
        q_all_total_kN = qall * area_f
        sf_act = qu / q_kontak if q_kontak > 0 else 0
        is_safe = (q_kontak <= qall)
        if not is_safe:
            all_methods_ok = False
            
        status_text = "AMAN (OK)" if is_safe else "OVERSTRESSED"
        
        table_comp.append({
            "metode": item["metode"],
            "Nc": item["Nc"],
            "Nq": item["Nq"],
            "Ngamma": item["Ngamma"],
            "sc": item.get("sc", 1.0),
            "sq": item.get("sq", 1.0),
            "sgamma": item.get("sgamma", 1.0),
            "dc": item.get("dc", 1.0),
            "dq": item.get("dq", 1.0),
            "dgamma": item.get("dgamma", 1.0),
            "po": po,
            "gamma_eff": item.get("gamma_eff", gamma_in),
            "qu": qu,
            "qall": qall,
            "Qall_kN": q_all_total_kN,
            "q_kontak": q_kontak,
            "sf_aktual": sf_act,
            "status": status_text,
            "is_safe": is_safe
        })

    min_sf_act = min([r["sf_aktual"] for r in table_comp])

    # 1. OTOMATIS CATAT SETIAP PENGGUNA YANG MELAKUKAN PERHITUNGAN KE DATABASE PEMILIK
    calc_sig = f"{st.session_state.project_info.get('name')}_{lebar_b}_{panjang_l}_{df_in}_{c_in}_{phi_in}_{total_beban_aksial_p}_{bentuk_fondasi}_{sf_in}"
    if st.session_state.get("last_auto_logged_sig") != calc_sig:
        try:
            sub_id = save_client_submission({
                "client_name": st.session_state.get("sub_client_name", "Pengguna Umum / Web"),
                "client_wa": st.session_state.get("sub_client_wa", "-"),
                "notes": f"Kalkulasi Otomatis ({bentuk_fondasi.split('(')[0].strip()}) B={lebar_b:.2f}m x L={panjang_l:.2f}m, Df={df_in:.2f}m, SF Target={sf_in}",
                "project_name": st.session_state.project_info.get("name", "Proyek Baru"),
                "location": st.session_state.project_info.get("location", "Semarang"),
                "building_function": fungsi_bldg,
                "floors": jml_lantai,
                "p_column": round(total_beban_aksial_p, 1),
                "width_b": lebar_b,
                "length_l": panjang_l,
                "depth_df": df_in,
                "cohesion": c_in,
                "friction_angle": phi_in,
                "unit_weight": gamma_in,
                "water_table": dw_in,
                "min_sf": round(min_sf_act, 2),
                "status": "AMAN (OK)" if all_methods_ok else "PERLU DIPERLEBAR"
            })
            st.session_state.last_auto_logged_sig = calc_sig
            st.session_state.last_auto_sub_id = sub_id
        except Exception:
            pass

    st.markdown(f"### 📊 Hasil Komparasi 4 Metode Daya Dukung ({bentuk_fondasi.split('(')[0]})")
    
    # Render Tabel Sesuai Format Profesional Geoteknik
    tbl_html = f"""
    <div class="geo-table-dark-container">
    <table class="geo-table-dark">
        <thead>
            <tr>
                <th style="text-align:left;">Metode Geoteknik</th>
                <th>Nc</th>
                <th>Nq</th>
                <th>Nγ</th>
                <th>qu (kPa)</th>
                <th>qall (kPa)</th>
                <th>Kapasitas Qall (SF={sf_in})</th>
                <th>SF Terhitung</th>
                <th>Status Keamanan</th>
            </tr>
        </thead>
        <tbody>
    """
    for r in table_comp:
        badge = "pill-safe" if r["is_safe"] else "pill-danger"
        tbl_html += f"""
        <tr>
            <td style="text-align:left; font-weight:750; color:#F8FAFC;">{r['metode']}</td>
            <td style="color:#A78BFA; font-weight:600;">{r['Nc']}</td>
            <td style="color:#38BDF8; font-weight:600;">{r['Nq']}</td>
            <td style="color:#34D399; font-weight:600;">{r['Ngamma']}</td>
            <td style="color:#E2E8F0; font-weight:600;">{r['qu']:,.1f}</td>
            <td style="color:#38BDF8; font-weight:750;">{r['qall']:,.1f}</td>
            <td style="color:#FBBF24; font-weight:700;">{r['Qall_kN']:,.1f} kN</td>
            <td style="color:#CBD5E1; font-weight:700;">{r['sf_aktual']:.2f}</td>
            <td><span class="pill-status {badge}">{r['status']}</span></td>
        </tr>
        """
    tbl_html += "</tbody></table></div>"
    st.html(tbl_html)

    auto_sub_id_disp = st.session_state.get('last_auto_sub_id', 'SUB-0001')
    st.markdown(
        f"<div style='font-size:0.82rem; color:#34D399; margin: 4px 0 10px 0; display:flex; align-items:center; gap:6px;'>"
        f"<span>💾 <em>Hasil perhitungan ini otomatis tercatat ke dalam Database Rekapitulasi Pemilik (ID: <strong>{auto_sub_id_disp}</strong>).</em></span>"
        f"</div>",
        unsafe_allow_html=True
    )

    # Catatan Teknis Geoteknik Mengenai Nilai Nc, Nq, Ngamma
    st.info(
        f"💡 **Penjelasan Faktor Daya Dukung ($N_c, N_q, N_\\gamma$):**\\n"
        f"- **$N_c$** : Pengaruh kohesi tanah ($c$).\\n"
        f"- **$N_q$** : Pengaruh beban tanah overburden di samping fondasi ($p_o = \\gamma \\cdot D_f$).\\n"
        f"- **$N_\\gamma$** : Pengaruh berat massa tanah di bawah dasar fondasi ($\\frac{{1}}{{2}} \\gamma B N_\\gamma$).\\n"
        f"- **Mengapa $N_\\gamma = 0$ jika $\\phi = 0^\\circ$?**  "
        f"Secara matematis, rumus $N_\\gamma$ berbanding lurus dengan $\\tan(\\phi)$. Pada Meyerhof: $N_\\gamma = (N_q - 1)\\tan(1.4\\phi)$, Vesic: $N_\\gamma = 2(N_q + 1)\\tan\\phi$, Hansen: $N_\\gamma = 1.5(N_q - 1)\\tan\\phi$. Karena $\\tan(0^\\circ) = 0$, maka saat sudut geser $\\phi = 0^\\circ$ (tanah lempung jenuh undrained), nilai $N_\\gamma$ secara eksak bernilai **0.0** (tidak ada perlawanan gesek baji tanah bawah). Jika tanah dianalisis dengan sudut geser efektif ($\\phi' > 0^\\circ$), maka $N_\\gamma$ otomatis bernilai positif."
    )

    # =========================================================================
    # MODUL DESAIN PENULANGAN PONDASI (SNI 2847:2019)
    # =========================================================================
    reinf_results = design_footing_reinforcement(
        B_m=lebar_b,
        L_m=panjang_l,
        hf_m=hf,
        col_b_m=col_b_val,
        col_h_m=col_h_val,
        Pu_kN=pu_terfaktor,
        Mux_kNm=mux_val,
        Muy_kNm=muy_val,
        fc_MPa=fc_val,
        fy_MPa=fy_val,
        cover_mm=cover_val,
        bar_dia_mm=bar_dia_val
    )

    st.markdown("### 🏗️ Desain Penulangan Struktur Fondasi Telapak (SNI 2847:2019)")
    
    # Banner Rekomendasi Utama Desain
    rf_sum = reinf_results["summary"]
    punch_res = reinf_results["punching_shear"]
    shear_res = reinf_results["one_way_shear"]
    reinf_x = reinf_results["flexure_rebar"]["dir_x"]
    reinf_y = reinf_results["flexure_rebar"]["dir_y"]
    boq = reinf_results["quantities"]

    st.html(f"""
    <div class="dark-card" style="border: 2px solid #10B981; background: rgba(6, 78, 59, 0.25); margin-bottom:16px;">
        <div style="font-size:0.85rem; font-weight:800; color:#34D399; text-transform:uppercase; letter-spacing:0.8px; margin-bottom:8px;">
            📌 REKOMENDASI PENULANGAN FONDASI ({reinf_results['standard']})
        </div>
        <div style="display:flex; justify-content:space-around; align-items:center; flex-wrap:wrap; gap:16px; margin: 12px 0;">
            <div style="text-align:center;">
                <div style="font-size:0.8rem; color:#94A3B8;">Tulangan Bawah Arah X</div>
                <div style="font-size:1.6rem; font-weight:800; color:#38BDF8;">{rf_sum['rebar_x']}</div>
                <div style="font-size:0.75rem; color:#94A3B8;">As perlu: {reinf_x['As_req_mm2']:.0f} mm² (Ada: {reinf_x['As_provided_mm2']:.0f} mm²)</div>
            </div>
            <div style="text-align:center; border-left:1px solid #334155; border-right:1px solid #334155; padding:0 24px;">
                <div style="font-size:0.8rem; color:#94A3B8;">Tulangan Bawah Arah Y</div>
                <div style="font-size:1.6rem; font-weight:800; color:#FBBF24;">{rf_sum['rebar_y']}</div>
                <div style="font-size:0.75rem; color:#94A3B8;">As perlu: {reinf_y['As_req_mm2']:.0f} mm² (Ada: {reinf_y['As_provided_mm2']:.0f} mm²)</div>
            </div>
            <div style="text-align:center;">
                <div style="font-size:0.8rem; color:#94A3B8;">Tebal Pelat Fondasi (hf)</div>
                <div style="font-size:1.6rem; font-weight:800; color:#F472B6;">{hf*100:.0f} cm</div>
                <div style="font-size:0.75rem; color:#94A3B8;">Selimut Beton: {int(cover_val)} mm (Kontak Tanah)</div>
            </div>
        </div>
        <div style="border-top:1px solid #334155; padding-top:10px; display:flex; justify-content:space-between; align-items:center; font-size:0.88rem;">
            <span>Status Keseluruhan Struktur: <strong style="color:{'#34D399' if rf_sum['is_all_safe'] else '#EF4444'};">{rf_sum['status']}</strong></span>
            <span>Penjangkaran: <strong style="color:#E2E8F0;">{reinf_results['development_length']['recommendation']}</strong></span>
        </div>
    </div>
    """)

    # 3 Kartu Pemeriksaan Kapasitas Struktur
    col_chk1, col_chk2, col_chk3 = st.columns(3)
    with col_chk1:
        st.html(f"""
        <div class="dark-card" style="border-left:4px solid {'#10B981' if punch_res['is_safe'] else '#EF4444'};">
            <div style="font-size:0.8rem; color:#94A3B8;">Kontrol Geser Pons (Punching)</div>
            <div style="font-size:1.25rem; font-weight:800; color:{'#34D399' if punch_res['is_safe'] else '#EF4444'};">{punch_res['status']}</div>
            <div style="font-size:0.82rem; color:#CBD5E1; margin-top:4px;">
                Vu2 = <strong>{punch_res['Vu2_kN']:.1f} kN</strong><br>
                φVc2 = <strong>{punch_res['phi_Vc2_kN']:.1f} kN</strong><br>
                Rasio Pembebanan: <strong>{punch_res['ratio']:.2f}</strong>
            </div>
        </div>
        """)
    with col_chk2:
        st.html(f"""
        <div class="dark-card" style="border-left:4px solid {'#10B981' if shear_res['is_safe'] else '#EF4444'};">
            <div style="font-size:0.8rem; color:#94A3B8;">Kontrol Geser 1 Arah (Beam Shear)</div>
            <div style="font-size:1.25rem; font-weight:800; color:{'#34D399' if shear_res['is_safe'] else '#EF4444'};">{shear_res['status']}</div>
            <div style="font-size:0.82rem; color:#CBD5E1; margin-top:4px;">
                Vu1 (X) = <strong>{shear_res['shear_x']['Vu1_kN']:.1f} kN</strong><br>
                φVc1 (X) = <strong>{shear_res['shear_x']['phi_Vc1_kN']:.1f} kN</strong><br>
                Rasio: <strong>{shear_res['shear_x']['ratio']:.2f}</strong>
            </div>
        </div>
        """)
    with col_chk3:
        st.html(f"""
        <div class="dark-card" style="border-left:4px solid #38BDF8;">
            <div style="font-size:0.8rem; color:#94A3B8;">Estimasi Kebutuhan Material (BoQ)</div>
            <div style="font-size:1.25rem; font-weight:800; color:#38BDF8;">{boq['total_rebar_weight_kg']:.1f} kg Besi</div>
            <div style="font-size:0.82rem; color:#CBD5E1; margin-top:4px;">
                Volume Beton Cor: <strong>{boq['vol_concrete_m3']:.2f} m³</strong><br>
                Total Panjang Baja: <strong>{boq['total_rebar_len_m']:.1f} m</strong><br>
                Indeks Pembesian: <strong>{boq['steel_ratio_kg_m3']:.1f} kg/m³</strong>
            </div>
        </div>
        """)

    with st.expander("📖 Rincian Rumus Matematis & Penjabaran 4 Metode Daya Dukung"):
        st.markdown(r"""
        #### 1. Persamaan Umum Kapasitas Dukung Tiga Suku:
        $$q_u = c \cdot N_c \cdot s_c \cdot d_c \cdot i_c + p_o \cdot N_q \cdot s_q \cdot d_q \cdot i_q + 0.5 \cdot \gamma_{\text{bawah}} \cdot B \cdot N_\gamma \cdot s_\gamma \cdot d_\gamma \cdot i_\gamma$$
        
        Kapasitas dukung izin neto ($q_{\text{all}}$):
        $$q_{\text{all}} = \frac{q_u - p_o}{\text{SF}} + p_o \quad (\text{dengan SF} = 2.0; 2.5; 3.0; 3.5)$$
        
        ---
        #### 2. Perumusan Khusus Keempat Metode:
        1. **Terzaghi (1943):**
           - Bujur Sangkar ($B = L$): $q_u = 1.3 c N_c + p_o N_q + 0.4 \gamma B N_\gamma$
           - Persegi Panjang: $q_u = c N_c (1 + 0.3 \frac{B}{L}) + p_o N_q + 0.5 \gamma B N_\gamma (1 - 0.2 \frac{B}{L})$
           - Lingkaran: $q_u = 1.3 c N_c + p_o N_q + 0.3 \gamma B N_\gamma$
           - Jalur / Strip: $q_u = c N_c + p_o N_q + 0.5 \gamma B N_\gamma$
        2. **Meyerhof (1963):**
           - $N_q = \tan^2(45^\circ + \phi/2) e^{\pi \tan\phi}$
           - $N_c = (N_q - 1)\cot\phi$ (jika $\phi = 0^\circ \implies N_c = 5.14$)
           - $N_\gamma = (N_q - 1)\tan(1.4\phi)$
           - Faktor bentuk: $s_c = 1 + 0.2 K_p (B/L)$, $s_q = s_\gamma = 1 + 0.1 K_p (B/L)$ (untuk $\phi \ge 10^\circ$)
           - Faktor kedalaman: $d_c = 1 + 0.2 \sqrt{K_p} (D_f/B)$, $d_q = d_\gamma = 1 + 0.1 \sqrt{K_p} (D_f/B)$
        3. **Vesic (1975):**
           - $N_\gamma = 2 (N_q + 1) \tan\phi$
           - Faktor bentuk: $s_c = 1 + \frac{B}{L}\frac{N_q}{N_c}$, $s_q = 1 + \frac{B}{L}\tan\phi$, $s_\gamma = 1 - 0.4 \frac{B}{L}$
           - Faktor kedalaman: $k = \min(1.0, D_f/B)$, $d_c = 1 + 0.4k$, $d_q = 1 + 2k\tan\phi(1-\sin\phi)^2$, $d_\gamma = 1.0$
        4. **Brinch Hansen (1970):**
           - Untuk $\phi = 0^\circ$: $q_u = 5.14 c (1 + 0.2 \frac{B}{L} + 0.4 k) + p_o$
           - Untuk $\phi > 0^\circ$: $N_\gamma = 1.5(N_q - 1)\tan\phi$, $s_c = 1 + \frac{B}{L}\frac{N_q}{N_c}$, $s_q = 1 + \frac{B}{L}\sin\phi$, $s_\gamma = 1 - 0.4 \frac{B}{L}$
        """)

    vol_beton = area_f * hf
    
    # 1. KOTAK STATUS & REKOMENDASI DESAIN FONDASI DANGKAL
    if all_methods_ok:
        st.html(f"""
        <div class="dark-card" style="border:1.5px solid #10B981; background:rgba(6, 78, 59, 0.2); padding:14px 18px; margin: 12px 0;">
            <div style="color:#34D399; font-weight:750; font-size:0.95rem; display:flex; align-items:center; gap:6px;">
                🟢 Rekomendasi Desain Fondasi Dangkal Terpilih:
            </div>
            <div style="font-size:0.88rem; color:#E2E8F0; margin-top:6px; line-height:1.55;">
                Gunakan <strong>Fondasi {bentuk_fondasi.split('(')[0]}</strong> dengan ukuran <strong>B = {lebar_b:.2f} m &times; L = {panjang_l:.2f} m</strong> (tebal pelat h = {hf:.2f} m) pada kedalaman <strong>Df = {df_in:.2f} m</strong>. Dimensi ini <strong>MEMENUHI KEAMANAN (SF &ge; {sf_in:.2f})</strong> pada ke-4 metode analisis dengan estimasi volume beton <strong>{vol_beton:.2f} m³</strong>.
            </div>
        </div>
        """)
    else:
        st.html(f"""
        <div class="dark-card" style="border:1.5px solid #EF4444; background:rgba(127, 29, 29, 0.2); padding:14px 18px; margin: 12px 0;">
            <div style="color:#F87171; font-weight:750; font-size:0.95rem; display:flex; align-items:center; gap:6px;">
                ⚠️ Peringatan: Terdapat Metode yang Belum Memenuhi (OVERSTRESSED)
            </div>
            <div style="font-size:0.88rem; color:#E2E8F0; margin-top:6px; line-height:1.55;">
                Tekanan kontak (<strong>{q_kontak:.1f} kPa</strong>) melebihi kapasitas izin salah satu metode. Disarankan memilih opsi <strong>Auto-Optimasi Dimensi</strong> atau perbesar ukuran tapak!
            </div>
        </div>
        """)

    # 2. SUITE SIMULASI & GAMBAR TEKNIK INTERAKTIF LENGKAP
    # Mendukung Bentuk Pilihan: Bujur Sangkar, Persegi Panjang, Lingkaran 3D Silinder, Strip/Jalur Bata
    st.markdown("### 📐 Studio Simulasi Geometri CAD & Analisis Interaktif")
    
    sk_col1, sk_col2 = st.columns([1.7, 0.9])
    with sk_col1:
        tab_cutaway, tab_3d, tab_plan, tab_cross, tab_bulb = st.tabs([
            "🌟 Model 3D Cutaway (Fondasi, Tulangan & Tanah)",
            "🕹️ Model 3D Blok Dasar",
            "📐 Gambar Kerja 2D (Tampak Atas & Tulangan)",
            "🏗️ Potongan Melintang Geoteknik 2D",
            "🌊 Kontur Isobar Tegangan Boussinesq"
        ])

        with tab_cutaway:
            st.caption("💡 **Model 3D Cutaway Realistis (Sesuai Referensi Konstruksi):** Memotong penampang fondasi dan tanah sekitarnya untuk menampilkan jaring tulangan X & Y, kait 90°, dowel kolom, dan sengkang dalam satu tampilan 3D interaktif 360°.")
            fig_cutaway = plot_cutaway_foundation_3d(
                shape=bentuk_fondasi,
                B=lebar_b,
                L=panjang_l,
                Df=df_in,
                dw=dw_in,
                P_kN=total_beban_aksial_p,
                hf=hf,
                col_b=col_b_val,
                col_h=col_h_val,
                cover_m=cover_val / 1000.0,
                bar_dia_mm=bar_dia_val,
                nx_bars=reinf_results["flexure_rebar"]["dir_x"]["n_bars"],
                ny_bars=reinf_results["flexure_rebar"]["dir_y"]["n_bars"],
                reinf_results=reinf_results,
                soil_name=soil.get("soil_type", "Tanah Dasar"),
                show_soil=True,
                show_rebar=True,
                show_cutaway=True
            )
            st.plotly_chart(fig_cutaway, use_container_width=True)
        
        with tab_3d:
            st.caption("💡 **Interaksi 3D:** Gunakan mouse / layar sentuh untuk **memutar sudut pandang (orbit 360°)**, zoom in/out, atau menggeser posisi.")
            fig_3d = plot_foundation_3d(
                shape=bentuk_fondasi,
                B=lebar_b,
                L=panjang_l,
                Df=df_in,
                dw=dw_in,
                P_kN=total_beban_aksial_p,
                hf=hf,
                soil_name=soil.get("soil_type", "Tanah Dasar")
            )
            st.plotly_chart(fig_3d, use_container_width=True)

        with tab_plan:
            st.caption("💡 **Tampak Atas (Plan View):** Memperlihatkan kontur bidang kontak tanah, posisi kolom struktur, dan estimasi tata letak tulangan beton.")
            fig_plan = plot_foundation_plan_view(
                shape=bentuk_fondasi,
                B=lebar_b,
                L=panjang_l,
                hf=hf,
                P_kN=total_beban_aksial_p
            )
            st.plotly_chart(fig_plan, use_container_width=True)

        with tab_cross:
            st.caption("💡 **Potongan Melintang 2D:** Hubungan kedalaman fondasi Df terhadap Muka Air Tanah (MAT) dan gaya aksial kolom P.")
            fig_pond = plot_foundation_cross_section(
                B=lebar_b,
                L=panjang_l,
                Df=df_in,
                dw=dw_in,
                P_kN=total_beban_aksial_p,
                soil_name=soil.get("soil_type", "Tanah Dasar"),
                c=c_in,
                phi=phi_in,
                gamma=gamma_in,
                hf=hf,
                shape=bentuk_fondasi
            )
            st.plotly_chart(fig_pond, use_container_width=True)

        with tab_bulb:
            st.caption("💡 **Teori Boussinesq:** Visualisasi gelembung tegangan tambahan (Δσz) yang menjalar ke dalam massa tanah di bawah dasar fondasi.")
            fig_bulb = plot_boussinesq_stress_bulb(
                B=lebar_b,
                L=panjang_l,
                Df=df_in,
                q_contact=q_kontak,
                shape=bentuk_fondasi
            )
            st.plotly_chart(fig_bulb, use_container_width=True)
        
    with sk_col2:
        min_sf_act = min([float(r["sf_aktual"]) for r in table_comp])
        fig_sf = plot_safety_gauge(min_sf_act, target_sf=float(sf_in))
        st.plotly_chart(fig_sf, use_container_width=True)
        
        # Panel Ringkasan Geometri Cerdas
        st.html(f"""
        <div class="dark-card" style="border-left: 4px solid #00E5FF; padding: 14px 16px; margin-top: -10px;">
            <div style="font-weight: 750; color: #38BDF8; font-size: 0.92rem; margin-bottom: 8px;">
                📋 Identitas Geometri Terpilih:
            </div>
            <div style="font-size: 0.85rem; color: #CBD5E1; line-height: 1.6;">
                <div>🔷 <strong>Bentuk:</strong> {bentuk_fondasi.split('(')[0]}</div>
                <div>📏 <strong>Dimensi:</strong> {lebar_b:.2f} m &times; {panjang_l:.2f} m</div>
                <div>📦 <strong>Luas Tapak A:</strong> {area_f:.2f} m²</div>
                <div>🧱 <strong>Volume Beton:</strong> {vol_beton:.2f} m³</div>
                <div>⚡ <strong>Tegangan Kontak q:</strong> <span style="color:#FBBF24; font-weight:700;">{q_kontak:.1f} kPa</span></div>
            </div>
        </div>
        """)

    # 3. KOMPARASI EFISIENSI & KEPRAKTISAN BENTUK FONDASI DANGKAL
    with st.expander("🏆 Sistem Penilai Cerdas Bentuk Fondasi Dangkal (Bujur Sangkar vs Persegi Panjang vs Lingkaran vs Jalur)", expanded=False):
        st.markdown("##### 🔍 Komparasi Dimensi Setara, Luas, Volume Beton & Kemudahan Konstruksi:")
        shapes_comp = compare_foundation_shapes(
            total_beban_aksial_p, c_in, phi_in, gamma_in, gamma_sat_in, df_in, dw_in, sf_target=sf_in, hf_val=hf
        )
        
        c_shp1, c_shp2 = st.columns(2)
        for idx, shp in enumerate(shapes_comp):
            target_col = c_shp1 if (idx % 2 == 0) else c_shp2
            with target_col:
                is_selected = (shape_code in shp["shape"])
                border_color = "#38BDF8" if is_selected else "#334155"
                badge_sel = "<span class='brand-badge' style='background:#0284C7; color:#FFF;'>SEDANG DIPILIH</span>" if is_selected else ""
                
                st.html(f"""
                <div class="dark-card" style="border: 1.5px solid {border_color}; margin-bottom: 10px; padding: 12px 14px;">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <span style="font-weight:750; color:#F8FAFC; font-size:0.95rem;">{shp['icon']} {shp['shape']}</span>
                        {badge_sel}
                    </div>
                    <div style="margin-top:8px; font-size:0.85rem; color:#CBD5E1; line-height:1.5;">
                        <div>📏 <strong>Dimensi Setara:</strong> <span style="color:#FBBF24;">{shp['dimensions']}</span></div>
                        <div>📦 <strong>Luas & Volume Beton:</strong> {shp['area']} m² &bull; {shp['vol_beton']} m³</div>
                        <div>🛡️ <strong>Safety Factor (SF):</strong> <span style="color:#34D399; font-weight:700;">{shp['sf']}</span> (Target &ge; {sf_in})</div>
                        <div style="margin-top:6px; color:#94A3B8; font-size:0.8rem;">🔨 <em>{shp['practicality']}</em> — {shp['practicality_desc']}</div>
                    </div>
                </div>
                """)

    st.markdown("<br>", unsafe_allow_html=True)

    # =========================================================================
    # TOMBOL EKSPOR EXCEL & CSV
    # =========================================================================
    st.markdown("#### 📥 Ekspor Laporan Resmi Excel (.xlsx) & CSV:")
    exp_col1, exp_col2 = st.columns(2)
    
    excel_bytes = generate_excel_report(
        project_info=st.session_state.project_info,
        soil_params=soil,
        load_params={
            "building_function": fungsi_bldg,
            "floors": jml_lantai,
            "floor_area": luas_bangunan_m2,
            "tributary_area": luas_trib,
            "dead_load_unit": dl_val,
            "live_load_unit": ll_val,
            "p_column": total_beban_aksial_p,
            "pu_column": pu_terfaktor,
            "Mux": mux_val,
            "Muy": muy_val
        },
        comp_results=table_comp,
        selected_dim={"B": lebar_b, "L": panjang_l, "Df": df_in, "hf": hf, "SF": sf_in, "shape": bentuk_fondasi},
        reinf_results=reinf_results
    )
    
    csv_str = generate_csv_report(
        comp_results=table_comp,
        selected_dim={"B": lebar_b, "L": panjang_l, "Df": df_in}
    )
    
    with exp_col1:
        st.download_button(
            label="📊 Unduh Laporan Perhitungan Struktur 6-Sheets (.xlsx)",
            data=excel_bytes,
            file_name=f"Laporan_Perhitungan_Fondasi_{st.session_state.project_info['name'].replace(' ', '_')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            type="primary",
            use_container_width=True
        )
        
    with exp_col2:
        st.download_button(
            label="📄 Unduh Data CSV (.csv)",
            data=csv_str,
            file_name="Komparasi_4_Metode_Pondasi.csv",
            mime="text/csv",
            use_container_width=True
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # =========================================================================
    # FITUR PENGIRIMAN DATA DARI PENGGUNA LAIN KE PEMILIK APLIKASI
    # =========================================================================
    with st.expander("📤 Ajukan / Kirim Data Desain Ini ke Pemilik Aplikasi (Konsultan)", expanded=False):
        st.markdown("""
        <div style="font-size:0.9rem; color:#CBD5E1; margin-bottom:12px;">
            Apakah Anda pengguna lain yang sedang merencanakan bangunan? 
            Anda dapat mengirimkan data pembebanan, kondisi tanah, dan rekomendasi dimensi fondasi ini langsung ke pemilik aplikasi. 
            Data akan otomatis tersimpan dalam <strong>Rekapitulasi Excel Pemilik</strong> dan dapat diteruskan ke WhatsApp!
        </div>
        """, unsafe_allow_html=True)
        
        c_sub1, c_sub2 = st.columns(2)
        client_name = c_sub1.text_input("Nama Anda / Perencana:", value="Budi Santoso", key="sub_client_name")
        client_wa = c_sub2.text_input("Nomor WhatsApp / HP:", value="081234567890", key="sub_client_wa")
        client_notes = st.text_area("Catatan Tambahan / Lokasi Spesifik:", value="Mohon bantuan review fondasi untuk ruko 3 lantai di tanah pekarangan sedang.", key="sub_client_notes")
        
        if st.button("🚀 Kirim Data Desain ke Database Pemilik", type="primary", use_container_width=True):
            sub_payload = {
                "client_name": client_name,
                "client_wa": client_wa,
                "notes": client_notes,
                "project_name": st.session_state.project_info.get("name", "Proyek Baru"),
                "location": st.session_state.project_info.get("location", "Semarang"),
                "building_function": fungsi_bldg,
                "floors": jml_lantai,
                "p_column": total_beban_aksial_p,
                "width_b": lebar_b,
                "length_l": panjang_l,
                "depth_df": df_in,
                "cohesion": c_in,
                "friction_angle": phi_in,
                "unit_weight": gamma_in,
                "water_table": dw_in,
                "min_sf": min_sf_act,
                "status": "AMAN (OK)" if min_sf_act >= float(sf_in) else "PERLU DIPERBESAR"
            }
            sub_id = save_client_submission(sub_payload)
            st.success(f"✅ Data berhasil dikirim dan tersimpan dengan ID: **{sub_id}** ke dalam file Excel Rekapitulasi Pemilik!")
            
            # Format pesan WhatsApp otomatis
            wa_text = (
                f"*PENGAJUAN DESAIN PONDASI TAPAK CERDAS*\n"
                f"ID Pengajuan: {sub_id}\n"
                f"Nama Klien: {client_name} ({client_wa})\n"
                f"Proyek: {st.session_state.project_info.get('name')}\n"
                f"Beban Aksial P: {total_beban_aksial_p:.1f} kN\n"
                f"Bentuk Fondasi: {bentuk_fondasi.split('(')[0]}\n"
                f"Dimensi Usulan: {lebar_b:.2f} x {panjang_l:.2f} m (Df = {df_in:.2f} m)\n"
                f"SF Terendah: {min_sf_act:.2f} ({'AMAN' if min_sf_act >= float(sf_in) else 'PERLU DIPERLEBAR'})\n"
                f"Catatan: {client_notes}"
            )
            wa_encoded = urllib.parse.quote(wa_text)
            wa_link = f"https://api.whatsapp.com/send?text={wa_encoded}"
            st.markdown(f"""
            <a href="{wa_link}" target="_blank" style="display:inline-block; background:#25D366; color:#FFFFFF; padding:10px 18px; border-radius:8px; font-weight:700; text-decoration:none; margin-top:8px;">
                📲 Teruskan Rincian Ini via WhatsApp ke Pemilik / Insinyur
            </a>
            """, unsafe_allow_html=True)

st.markdown("---")

# =========================================================================
# PENJELASAN KHUSUS GEOTEKNIK (JAWABAN PERTANYAAN POIN 5 USER)
# =========================================================================
with st.expander("❓ Solusi & Analisis Ahli: Bagaimana Jika Salah Satu Metode Tidak Memenuhi (OVERSTRESSED)?", expanded=True):
    st.html("""
    <div style="font-size:0.92rem; line-height:1.65; color:#E2E8F0;">
        <h4 style="color:#38BDF8; margin-top:0;">📚 Mengapa Hasil 4 Metode Bisa Berbeda?</h4>
        <p>Dalam rekayasa geoteknik, masing-masing peneliti mengembangkan asumsi baji runtuh yang berbeda:</p>
        <ul>
            <li><strong>Terzaghi (1943):</strong> Mengasumsikan dasar fondasi kasar dan mengabaikan tahanan geser tanah di atas dasar fondasi (hanya beban overburden po). Akibatnya, metode Terzaghi sering memberikan <em>nilai daya dukung paling rendah (paling konservatif)</em>.</li>
            <li><strong>Meyerhof (1963):</strong> Memperhitungkan keruntuhan tanah yang melengkung sampai ke atas permukaan tanah. Umumnya menghasilkan kapasitas lebih tinggi karena kontribusi geser tanah di samping fondasi dihitung.</li>
            <li><strong>Vesic (1975) & Hansen (1970):</strong> Menggunakan sudut baji beralas (45° + φ/2) dan faktor bentuk/kedalaman trigonometri. Hansen memiliki formulasi khusus untuk tanah lempung jenuh (φ=0).</li>
        </ul>
        <h4 style="color:#FBBF24; margin-top:14px;">🛠️ Solusi Rekayasa Fondasi Jika Terjadi Perbedaan:</h4>
        <ol>
            <li><strong>Gunakan Prinsip Desain Terkritis (Governing Method):</strong> Rekomendasi utama di dunia konstruksi adalah mengambil metode dengan kapasitas izin terkecil (biasanya Terzaghi) sebagai acuan batas aman. Jika 1 metode saja tidak lolos, perbesar ukuran pondasi!</li>
            <li><strong>Aktifkan Fitur Auto-Optimasi Dimensi:</strong> Anda cukup memilih opsi <em>'Auto-Optimasi Dimensi'</em> di atas. Sistem Tapak Cerdas secara otomatis menaikkan dimensi tapak sampai <strong>seluruh 4 metode serentak berstatus AMAN (OK)</strong>.</li>
            <li><strong>Evaluasi Perbaikan Tanah Dasar:</strong> Jika tanah permukaan lunak (N-SPT &lt; 5 atau qc &lt; 25 kg/cm²), lakukan perbaikan tanah (seperti penggantian tanah urug sirtu padat / matras bambu) atau perbesar tapak fondasi hingga batas aman tercapai.</li>
        </ol>
    </div>
    """)
