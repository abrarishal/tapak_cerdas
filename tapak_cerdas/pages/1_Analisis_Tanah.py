"""
=============================================================================
TAPAK CERDAS - MODUL INVESTIGASI & ANALISIS KARAKTERISTIK TANAH
=============================================================================
File: pages/1_Analisis_Tanah.py
Deskripsi: Pengolahan Bore Log SPT (ASTM D1586 & Referensi Undip Mangkang),
           Uji Sondir CPT Bikonus 2.5 Ton (SNI 2827:2008 & ASTM D3441),
           serta Mode Cepat Pengguna Awam (Estimasi Lapangan).
=============================================================================
"""

import streamlit as st
import pandas as pd
import numpy as np
import os
import sys

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from modules.spt_analyzer import (
    compute_spt_layer,
    compute_weighted_average_params,
    plot_single_unified_spt_chart,
    plot_spt_profile,
    plot_stratigraphy_column,
    SAMPLE_BORELOG_UNDIP_BH4
)
from modules.cpt_analyzer import (
    compute_cpt_table,
    plot_single_unified_cpt_chart,
    SAMPLE_SONDIR_2_5TON
)
from modules.subsurface_3d import plot_subsurface_block_3d
from utils.excel_exporter import generate_spt_excel, generate_cpt_excel

# Konfigurasi Halaman
st.set_page_config(page_title="Investigasi Tanah - TAPAK CERDAS", page_icon="📊", layout="wide")

# Muat CSS Dark Slate dengan Watermark Blueprint Fondasi
css_path = os.path.join(ROOT_DIR, "assets", "style.css")
if os.path.exists(css_path):
    with open(css_path, "r", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Top Navbar Sesuai Format PDF Halaman 1 & 2
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
    st.button("🔬 1. Korelasi N-SPT / CPT & Stratigrafi", type="primary", use_container_width=True)
with c_nav3:
    if st.button("🏛️ 2. Analisis Beban & 4 Metode Fondasi", use_container_width=True):
        st.switch_page("pages/2_Perencanaan_Pondasi.py")
with c_nav4:
    if st.button("📑 3. Riwayat / Masuk Klien", use_container_width=True):
        st.switch_page("pages/3_Riwayat_Laporan.py")

st.markdown("<div style='margin-bottom: 1rem;'></div>", unsafe_allow_html=True)

# Inisialisasi Session State Global
if "project_info" not in st.session_state:
    st.session_state.project_info = {
        "name": "Pembangunan Ruko 3 Lantai Cerdas",
        "location": "Kawasan Komersial Mandiri",
        "borehole_id": "BH-01",
        "water_table_depth": 1.50
    }

if "soil_params" not in st.session_state:
    st.session_state.soil_params = {
        "status": "Siap Digunakan",
        "source": "Mode Cepat Pengguna Awam",
        "soil_type": "Tanah Lempung Sedang / Teguh",
        "cohesion": 35.0,
        "friction_angle": 12.0,
        "unit_weight": 17.5,
        "sat_unit_weight": 19.0,
        "water_table": 1.50
    }

if "spt_initialized" not in st.session_state:
    st.session_state.spt_initialized = True
    st.session_state.spt_layers = [
        {"depth_top": 0.0, "depth_bot": 1.5, "n1": 2, "n2": 4, "n3": 4, "n_spt": 8, "n60": 6.7, "phi": 5.0, "c": 40.0, "gamma": 17.5, "gamma_sat": 19.0, "soil_type": "Lempung Sedang", "konsistensi": "Sedang / Teguh", "deskripsi": "Lempung kelanauan coklat teguh", "color": "#3B82F6", "interval_str": "0.00 - 1.50 m"},
        {"depth_top": 1.5, "depth_bot": 3.5, "n1": 4, "n2": 8, "n3": 9, "n_spt": 17, "n60": 15.3, "phi": 32.0, "c": 0.0, "gamma": 18.2, "gamma_sat": 20.0, "soil_type": "Pasir Sedang", "konsistensi": "Kepadatan Sedang", "deskripsi": "Pasir berlanau abu-abu", "color": "#D97706", "interval_str": "1.50 - 3.50 m"},
        {"depth_top": 3.5, "depth_bot": 6.0, "n1": 8, "n2": 15, "n3": 17, "n_spt": 32, "n60": 30.4, "phi": 36.5, "c": 0.0, "gamma": 19.5, "gamma_sat": 21.2, "soil_type": "Pasir Padat", "konsistensi": "Padat", "deskripsi": "Pasir padat kecoklatan", "color": "#B45309", "interval_str": "3.50 - 6.00 m"}
    ]
if "spt_layers" not in st.session_state:
    st.session_state.spt_layers = []

# Sanitasi session state spt_layers untuk mencegah KeyError jika session lama tersimpan di browser
sanitized_spt = []
for lyr in st.session_state.spt_layers:
    if isinstance(lyr, dict):
        z_t = float(lyr.get("depth_top", 0.0))
        z_b = float(lyr.get("depth_bot", z_t + 1.5))
        n_v = int(lyr.get("n_spt", 10))
        stype = lyr.get("soil_type", "Lempung Sedang")
        desc = lyr.get("deskripsi", lyr.get("soil_type", "Lapisan Tanah"))
        sanitized_spt.append({
            "depth_top": z_t,
            "depth_bot": z_b,
            "interval_str": lyr.get("interval_str", f"{z_t:.2f} - {z_b:.2f} m"),
            "thickness": round(z_b - z_t, 2),
            "n1": lyr.get("n1", max(1, int(n_v * 0.35))),
            "n2": lyr.get("n2", int(n_v * 0.5)),
            "n3": lyr.get("n3", int(n_v * 0.5)),
            "n_spt": n_v,
            "n60": lyr.get("n60", round(n_v * 0.85, 1)),
            "soil_type": stype,
            "konsistensi": lyr.get("konsistensi", "Sedang"),
            "deskripsi": desc,
            "phi": float(lyr.get("phi", 0.0)),
            "c": float(lyr.get("c", 25.0)),
            "gamma": float(lyr.get("gamma", 17.5)),
            "gamma_sat": float(lyr.get("gamma_sat", 19.0)),
            "color": lyr.get("color", "#3B82F6")
        })
st.session_state.spt_layers = sanitized_spt

if "cpt_initialized" not in st.session_state:
    st.session_state.cpt_initialized = True
    st.session_state.cpt_raw_points = SAMPLE_SONDIR_2_5TON[:12]
if "cpt_raw_points" not in st.session_state:
    st.session_state.cpt_raw_points = []

# TABS UTAMA (SESUAI REVISI PENGGUNA)
tab_spt, tab_cpt, tab_layman = st.tabs([
    "🔨 1. Uji Penetrasi Standar (SPT) & Bore Log",
    "🧪 2. Uji Sondir (CPT / Dutch Cone 2.5 Ton)",
    "🏡 3. Mode Cepat Pengguna Awam (Tanpa Uji Lab — Estimasi Lapangan)"
])

# =========================================================================
# TAB 1: UJI SPT & BORE LOG LAPANGAN (SESUAI DED UNDIP MANGKANG BH-4)
# =========================================================================
with tab_spt:
    st.markdown("### 🔨 Input Data Boring SPT & Pembuatan Bore Log Geoteknik")
    
    st.info(
        r"💡 **Penjelasan Geoteknik Penting**: Sebelum dilakukan pemboran dan pengujian, jenis tanah sebenarnya belum diketahui. "
        r"Oleh karena itu, dari jumlah pukulan penetrasi **N-SPT ($N_2 + N_3$)** dan pengamatan sampel split spoon, "
        r"sistem TAPAK CERDAS akan **mengidentifikasi jenis tanah, tingkat konsistensi/kepadatan, serta menghitung parameter $c$, $\phi$, dan $\gamma$ secara otomatis** "
        r"(sesuai standar Terzaghi & Peck, Meyerhof, dan format Bore Log Undip)."
    )

    c_top1, c_top2 = st.columns([1.5, 2.5])
    with c_top1:
        mat_spt = st.number_input(
            "Kedalaman Muka Air Tanah (MAT) dari Permukaan (meter):",
            min_value=0.0, max_value=20.0,
            value=float(st.session_state.project_info.get("water_table_depth", 1.50)),
            step=0.25
        )
        st.session_state.project_info["water_table_depth"] = mat_spt

    with c_top2:
        st.write("")
        st.write("")
        if st.button("📋 Muat Contoh Nyata Bore Log Undip (STA. 3+000 Mangkang BH-4)", use_container_width=True):
            st.session_state.spt_layers = SAMPLE_BORELOG_UNDIP_BH4
            st.success("✅ Berhasil memuat data uji lapangan asli dari Bore Log Undip BH-4 (Semarang)!")
            st.rerun()

    st.markdown("#### 📋 Tabel Formasi Lapisan Tanah (Bore Log):")

    # Form Tambah Lapisan Baru Cepat
    with st.expander("➕ Tambah Lapisan Tanah Baru ke Tabel", expanded=False):
        c_add1, c_add2, c_add3, c_add4, c_add5 = st.columns([1.2, 1.2, 1.5, 2, 1.5])
        last_bot = st.session_state.spt_layers[-1]["depth_bot"] if st.session_state.spt_layers else 0.0
        new_top = c_add1.number_input("Top (m)", value=float(last_bot), step=0.5)
        new_bot = c_add2.number_input("Bot (m)", value=float(last_bot + 2.0), step=0.5)
        new_n = c_add3.number_input("Nilai N-SPT (pukulan)", min_value=1, max_value=100, value=12, step=1)
        new_desc = c_add4.text_input("Deskripsi Visual (Opsional)", value="Lempung kelanauan abu-abu")
        new_type_hint = c_add5.selectbox("Jenis Dominan", ["Auto (Deteksi N-SPT)", "Lempung (Kohesif)", "Pasir (Granular)"])
        
        if st.button("Tambahkan Lapisan Ini ke Bore Log", type="primary"):
            added_layer = compute_spt_layer(
                depth_top=new_top, depth_bot=new_bot,
                n1=max(1, int(new_n * 0.35)), n2=int(new_n * 0.5), n3=int(new_n * 0.5),
                user_desc=new_desc, soil_type=new_type_hint, gw_depth=mat_spt
            )
            st.session_state.spt_layers.append(added_layer)
            st.rerun()

    # Tampilkan Tabel Bore Log Terformat
    if len(st.session_state.spt_layers) == 0:
        st.warning("⚠️ **Tabel Bore Log SPT saat ini kosong.** Anda dapat menambahkan lapisan tanah baru melalui formulir *'➕ Tambah Lapisan Tanah Baru ke Tabel'* di atas, atau klik tombol *'📋 Muat Contoh Nyata Bore Log Undip'* di bagian atas.")
    else:
        tbl_html = """
        <div class="geo-table-dark-container">
        <table class="geo-table-dark">
            <thead>
                <tr>
                    <th>Kedalaman (m)</th>
                    <th>Tebal (m)</th>
                    <th>N-SPT</th>
                    <th>Konsistensi / Kepadatan</th>
                    <th>Tipe Tanah</th>
                    <th>Deskripsi Lapangan</th>
                    <th>Kuat Geser cu (kPa)</th>
                    <th>Sudut Geser φ (°)</th>
                    <th>Sudut Geser Efektif φ' (°)</th>
                    <th>Berat Isi γ (kN/m³)</th>
                </tr>
            </thead>
            <tbody>
        """
        for r in st.session_state.spt_layers:
            z_t = float(r.get("depth_top", 0.0))
            z_b = float(r.get("depth_bot", z_t + 1.5))
            thick = round(z_b - z_t, 2)
            interval = r.get("interval_str", f"{z_t:.2f} - {z_b:.2f} m")
            n_val = r.get("n_spt", 0)
            kons = r.get("konsistensi", "-")
            stype = r.get("soil_type", "Tanah")
            desc = r.get("deskripsi", stype)
            c_val = r.get("c", 0.0)
            cu_val = r.get("cu", c_val)
            phi_val = r.get("phi", 0.0)
            phi_eff = r.get("phi_eff", phi_val if phi_val > 0 else 22.0)
            gam_val = r.get("gamma", 17.5)
            
            tbl_html += f"""
            <tr>
                <td style="font-weight:750; color:#38BDF8;">{interval}</td>
                <td>{thick:.2f} m</td>
                <td style="font-weight:800; color:#FBBF24;">{n_val}</td>
                <td><span class="pill-status pill-safe">{kons}</span></td>
                <td style="font-weight:600; color:#E2E8F0;">{stype}</td>
                <td style="font-size:0.85rem; color:#94A3B8;">{desc}</td>
                <td style="color:#F472B6; font-weight:700;">{cu_val} kPa</td>
                <td style="color:#38BDF8; font-weight:700;">{phi_val}°</td>
                <td style="color:#A78BFA; font-weight:700;">{phi_eff}°</td>
                <td style="color:#34D399; font-weight:700;">{gam_val}</td>
            </tr>
            """
        tbl_html += "</tbody></table></div>"
        st.html(tbl_html)

    # Baris Tombol Aksi & Ekspor Excel/CSV untuk SPT
    col_btn1, col_btn2, col_btn3, col_btn4 = st.columns([1.5, 1.8, 1.8, 1.4])
    with col_btn1:
        if len(st.session_state.spt_layers) > 0:
            if st.button("🗑️ Hapus Lapisan Bawah", use_container_width=True):
                st.session_state.spt_layers.pop()
                st.rerun()
    with col_btn2:
        if len(st.session_state.spt_layers) > 0:
            if st.button("⚠️ Kosongkan Tabel SPT", use_container_width=True):
                st.session_state.spt_layers = []
                st.rerun()
    with col_btn3:
        if len(st.session_state.spt_layers) > 0:
            spt_xlsx = generate_spt_excel(st.session_state.spt_layers, st.session_state.project_info)
            st.download_button(
                label="📊 Unduh Laporan Soil Investigation 5-Sheets (.xlsx)",
                data=spt_xlsx,
                file_name=f"Soil_Investigation_Report_{st.session_state.project_info['name'].replace(' ', '_')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
    with col_btn4:
        if len(st.session_state.spt_layers) > 0:
            df_spt = pd.DataFrame(st.session_state.spt_layers)
            csv_spt = df_spt.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📄 Unduh CSV SPT",
                data=csv_spt,
                file_name="Bore_Log_SPT.csv",
                mime="text/csv",
                use_container_width=True
            )

    st.markdown("---")

    # HASIL REKAPITULASI ZONA PONDASI & GRAFIK TUNGGAL
    col_res1, col_res2 = st.columns([1.2, 1.3])

    with col_res1:
        st.markdown("#### 🎯 Rekapitulasi Parameter Fondasi Dangkal (0 - 3.0 m)")
        avg_params = compute_weighted_average_params(st.session_state.spt_layers, target_depth=3.0)
        
        # Pilihan Mode Kondisi Tegangan
        mode_spt_drain = st.radio(
            "Pilih Asumsi Analisis Tanah Dasar Fondasi:",
            [
                "Analisis Tegangan Total (Undrained: φ = 0° untuk Lempung Jenuh, c = cu)",
                "Analisis Tegangan Efektif (Drained: Sudut Geser Efektif φ' > 0°, c' ≈ 5-10 kPa)"
            ],
            index=0,
            key="mode_spt_drain"
        )
        use_effective = "Efektif" in mode_spt_drain

        final_c = round(avg_params.get("cu", avg_params["c"]), 1) if not use_effective else 10.0
        final_phi = round(avg_params["phi"], 1) if not use_effective else round(avg_params.get("phi_eff", 24.0), 1)

        st.html(f"""
        <div class="dark-card" style="border: 2px solid #3B82F6; background: rgba(15, 23, 42, 0.95);">
            <div style="font-size:0.85rem; font-weight:800; color:#60A5FA; text-transform:uppercase; letter-spacing:0.8px; margin-bottom:8px;">
                📐 RATA-RATA TERBOBOT KETEBALAN PADA ZONA TELAPAK (0 - {avg_params['actual_depth_evaluated']:.1f} m)
            </div>
            <div style="display:flex; justify-content:space-around; align-items:center; margin:16px 0;">
                <div style="text-align:center;">
                    <div style="font-size:0.75rem; color:#94A3B8;">Sudut Geser (φ)</div>
                    <div style="font-size:1.8rem; font-weight:800; color:#38BDF8;">{final_phi}°</div>
                    <div style="font-size:0.7rem; color:#94A3B8;">{"Undrained (φ=0)" if not use_effective else "Drained (φ' efektif)"}</div>
                </div>
                <div style="text-align:center; border-left:1px solid #334155; border-right:1px solid #334155; padding:0 20px;">
                    <div style="font-size:0.75rem; color:#94A3B8;">Kuat Geser / Kohesi (c)</div>
                    <div style="font-size:1.8rem; font-weight:800; color:#F472B6;">{final_c} <span style="font-size:0.9rem;">kPa</span></div>
                    <div style="font-size:0.7rem; color:#94A3B8;">Kuat Geser Undrained cu</div>
                </div>
                <div style="text-align:center;">
                    <div style="font-size:0.75rem; color:#94A3B8;">Berat Isi Basah (γ)</div>
                    <div style="font-size:1.8rem; font-weight:800; color:#34D399;">{avg_params['gamma']} <span style="font-size:0.9rem;">kN/m³</span></div>
                    <div style="font-size:0.7rem; color:#94A3B8;">γsat: {avg_params['gamma_sat']} kN/m³</div>
                </div>
            </div>
            <div style="font-size:0.85rem; color:#94A3B8; text-align:center; border-top:1px solid #334155; padding-top:8px;">
                Formasi Lapisan Dominan: <strong style="color:#F8FAFC;">{avg_params['summary']}</strong>
            </div>
        </div>
        """)

        # Panduan Ilmiah Tegangan Geser
        with st.expander("💡 Penjelasan Ilmiah: Mengapa Sudut Geser / Tegangan Geser Muncul 0° pada Bore Log?"):
            st.markdown(r"""
            **1. Apakah Tegangan Geser Tanah Memang 0?**  
            **TIDAK.** Tegangan geser / kuat geser tanah sama sekali TIDAK NOL. Nilai kuat geser tanah lempung dinyatakan oleh parameter **$c_u$ (undrained shear strength)** yang nilainya tertera pada tabel (misal 12.0 s/d 25.0 kPa). Nilai yang nol adalah **sudut geser dalam undrained ($\phi_u = 0^\circ$)** pada kondisi tanah lempung jenuh air jangka pendek (*kondisi $\phi = 0$ Skempton*).

            **2. Rumus Kuat Geser dari Nilai N-SPT:**
            - **Kuat Geser Undrained ($c_u$):**  
              $c_u \approx 6.25 \times N \text{ (kPa)}$ *(Terzaghi & Peck, 1967)* atau $c_u = f_1 \times N$ *(Stroud, 1974, dengan $f_1 \approx 4.5 - 5.0$)*.
            - **Sudut Geser Dalam Efektif ($\phi'$):**  
              Dalam tinjauan jangka panjang (*drained / tegangan efektif*), lempung selalu memiliki sudut gesekan butiran efektif:  
              $\phi' \approx 20^\circ - 32^\circ$ (korelasi Peck, Hanson, & Thornburn).  
              Untuk tanah pasir: $\phi' = 27.1 + 0.3 N_{60} - 0.00054 N_{60}^2$ *(Wolff, 1989)*.
            """)

        if st.button("🚀 Terapkan Parameter Hasil SPT Ini ke Perencanaan Pondasi", type="primary", use_container_width=True):
            st.session_state.soil_params = {
                "status": "Siap Digunakan (Hasil SPT)",
                "source": "Uji Penetrasi Standar (Boring SPT)",
                "soil_type": f"Hasil Boring SPT ({avg_params['summary']})",
                "cohesion": final_c,
                "cu": final_c,
                "friction_angle": final_phi,
                "phi_eff": round(avg_params.get("phi_eff", 24.0), 1),
                "unit_weight": avg_params["gamma"],
                "sat_unit_weight": avg_params["gamma_sat"],
                "water_table": mat_spt
            }
            st.success("✅ Parameter berhasil ditransfer ke Tab Perencanaan Pondasi!")

    with col_res2:
        st.markdown("#### 🖼️ Visualisasi Bawah Permukaan Tanah (2D & 3D)")
        tab_v_2d, tab_v_3d = st.tabs([
            "📈 Grafik 2D Terpadu (N-SPT & Stratigrafi)",
            "🌍 Model Blok 3D Bawah Permukaan"
        ])
        with tab_v_2d:
            fig_spt_unified = plot_single_unified_spt_chart(st.session_state.spt_layers, gw_depth=mat_spt)
            st.plotly_chart(fig_spt_unified, use_container_width=True)
        with tab_v_3d:
            st.caption("💡 **Model 3D Bawah Permukaan:** Putar 360°, zoom in/out, atau geser untuk memeriksa lapisan tanah dan penetrasi bor secara proporsional.")
            fig_spt_3d = plot_subsurface_block_3d(
                layers=st.session_state.spt_layers,
                gw_depth=mat_spt,
                borehole_id=st.session_state.project_info.get("borehole_id", "BH-01"),
                test_type="SPT"
            )
            st.plotly_chart(fig_spt_3d, use_container_width=True)


# =========================================================================
# TAB 2: UJI SONDIR (CPT BIKONUS 2.5 TON STANDAR SNI 2827:2008)
# =========================================================================
with tab_cpt:
    st.markdown("### 🧪 Pengolahan Data Sondir (Cone Penetration Test 2.5 Ton)")
    
    st.info(
        "💡 **Standar Penyelidikan Lapangan**: Sesuai SNI 2827:2008 & ASTM D3441 (Uji Penetrasi Konus Bikonus 2.5 Ton). "
        "Bikonus standar menggunakan luas penampang ujung $A_c = 10 \\text{ cm}^2$ dan luas selimut geser $A_g = 100 \\text{ cm}^2$. "
        "Dari manometer dibaca perlawanan konus ($q_c$) dan jumlah hambatan ($JH$). "
        "Sistem menghitung Hambatan Pelekat $HP = 2(JH - q_c)$, Total Friksi $JHP = \\sum HP$, Hambatan Setempat $HS = (JH - q_c)/10$, "
        "serta Rasio Gesekan $FR = (HS/q_c) \\times 100\\%$ untuk klasifikasi jenis tanah Robertson & Campanella (1986)."
    )

    c_cpt_top1, c_cpt_top2 = st.columns([1.5, 2.5])
    with c_cpt_top1:
        mat_cpt = st.number_input("Kedalaman Muka Air Tanah (MAT) Sondir (meter):", min_value=0.0, max_value=20.0, value=float(st.session_state.project_info.get("water_table_depth", 1.50)), step=0.25, key="mat_cpt_input")

    with c_cpt_top2:
        st.write("")
        st.write("")
        if st.button("📋 Muat Contoh Data Uji Sondir Lapangan (2.5 Ton)", use_container_width=True):
            st.session_state.cpt_raw_points = SAMPLE_SONDIR_2_5TON
            st.success("✅ Berhasil memuat 30 titik bacaan uji sondir lapangan!")
            st.rerun()

    # Form Cara Menambahkan Data Baru CPT
    with st.expander("➕ Cara Menambahkan Data Bacaan Sondir Baru", expanded=False):
        c_pt1, c_pt2, c_pt3, c_pt4 = st.columns([1.2, 1.5, 1.5, 1.8])
        last_z = st.session_state.cpt_raw_points[-1]["depth"] if st.session_state.cpt_raw_points else 0.0
        in_z = c_pt1.number_input("Kedalaman (m)", value=float(last_z + 0.20), step=0.20)
        in_qc = c_pt2.number_input("qc (kg/cm²)", min_value=0.0, max_value=300.0, value=15.0, step=1.0)
        in_jh = c_pt3.number_input("JH (Jumlah Hambatan, kg/cm²)", min_value=0.0, max_value=400.0, value=25.0, step=1.0)
        
        c_pt4.write("")
        c_pt4.write("")
        if c_pt4.button("➕ Tambah Titik Bacaan Ini"):
            st.session_state.cpt_raw_points.append({"depth": in_z, "qc": in_qc, "jh": in_jh})
            st.session_state.cpt_raw_points = sorted(st.session_state.cpt_raw_points, key=lambda x: x["depth"])
            st.rerun()

    # Hitung Tabel Lengkap Menggunakan Engine Bikonus 2.5 Ton
    processed_cpt = compute_cpt_table(st.session_state.cpt_raw_points)

    col_tbl_cpt, col_graph_cpt = st.columns([1.3, 1.2])

    with col_tbl_cpt:
        st.markdown("#### 📋 Tabel Hasil Uji Sondir Bikonus 2.5 Ton:")
        
        if len(processed_cpt) == 0:
            st.warning("⚠️ **Tabel Uji Sondir saat ini kosong.** Anda dapat menambahkan data bacaan manometer baru melalui formulir di atas, atau klik *'📋 Muat Contoh Data Uji Sondir Lapangan'*.")
        else:
            cpt_html = """
            <div class="geo-table-dark-container" style="max-height: 420px; overflow-y: auto;">
            <table class="geo-table-dark">
                <thead>
                    <tr>
                        <th>Kedalaman</th>
                        <th>qc (kg/cm²)</th>
                        <th>JH (kg/cm²)</th>
                        <th>HP (kg/cm)</th>
                        <th>JHP Total</th>
                        <th>Tegangan fs (kPa)</th>
                        <th>FR (%)</th>
                        <th>Kuat Geser cu (kPa)</th>
                        <th>Klasifikasi Robertson (1986)</th>
                    </tr>
                </thead>
                <tbody>
            """
            for pt in processed_cpt:
                fs_disp = pt.get('fs_kpa', round(pt.get('hs', 0.0) * 98.07, 1))
                cu_disp = pt.get('cu_kpa', round(max(10.0, (pt.get('qc', 0.0) * 98.07) / 16.0), 1))
                cpt_html += f"""
                <tr>
                    <td style="font-weight:700; color:#38BDF8;">{pt['depth']:.2f} m</td>
                    <td style="font-weight:750; color:#FBBF24;">{pt['qc']:.1f}</td>
                    <td>{pt['jh']:.1f}</td>
                    <td>{pt['hp']:.1f}</td>
                    <td style="color:#34D399; font-weight:700;">{pt['jhp']:.1f}</td>
                    <td style="color:#38BDF8; font-weight:700;">{fs_disp:.1f}</td>
                    <td style="color:#EC4899; font-weight:700;">{pt['fr']:.2f}%</td>
                    <td style="color:#F472B6; font-weight:700;">{cu_disp:.1f}</td>
                    <td style="font-size:0.8rem;"><span class="pill-status pill-safe">{pt['soil_type']}</span></td>
                </tr>
                """
            cpt_html += "</tbody></table></div>"
            st.html(cpt_html)

            # Tombol Aksi & Ekspor Excel/CSV untuk CPT
            col_cpt_b1, col_cpt_b2, col_cpt_b3, col_cpt_b4 = st.columns([1.4, 1.8, 1.8, 1.4])
            with col_cpt_b1:
                if st.button("🗑️ Hapus Titik Bawah", use_container_width=True):
                    st.session_state.cpt_raw_points.pop()
                    st.rerun()
            with col_cpt_b2:
                if st.button("⚠️ Kosongkan Tabel Sondir", use_container_width=True):
                    st.session_state.cpt_raw_points = []
                    st.rerun()
            with col_cpt_b3:
                cpt_xlsx = generate_cpt_excel(processed_cpt, st.session_state.project_info)
                st.download_button(
                    label="📊 Unduh Laporan Soil Investigation 5-Sheets (.xlsx)",
                    data=cpt_xlsx,
                    file_name=f"Soil_Investigation_Report_{st.session_state.project_info['name'].replace(' ', '_')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )
            with col_cpt_b4:
                df_cpt = pd.DataFrame(processed_cpt)
                csv_cpt = df_cpt.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📄 Unduh CSV Sondir",
                    data=csv_cpt,
                    file_name="Hasil_Uji_Sondir_CPT.csv",
                    mime="text/csv",
                    use_container_width=True
                )

        # Rata-rata Zona Dangkal (0 - 3m)
        shallow_cpt = [p for p in processed_cpt if p["depth"] <= 3.0]
        if shallow_cpt:
            avg_qc = np.mean([p["qc"] for p in shallow_cpt])
            avg_fr = np.mean([p["fr"] for p in shallow_cpt])
            avg_phi = np.mean([p.get("phi", 0.0) for p in shallow_cpt])
            avg_phi_eff = np.mean([p.get("phi_eff", 24.0) for p in shallow_cpt])
            avg_c = np.mean([p.get("c", 35.0) for p in shallow_cpt])
            avg_cu = np.mean([p.get("cu_kpa", avg_c) for p in shallow_cpt])
            avg_fs = np.mean([p.get("fs_kpa", 20.0) for p in shallow_cpt])
            avg_gamma = np.mean([p.get("gamma", 17.5) for p in shallow_cpt])
        else:
            avg_qc, avg_fr, avg_phi, avg_phi_eff, avg_c, avg_cu, avg_fs, avg_gamma = 15.0, 3.5, 0.0, 24.0, 40.0, 40.0, 25.0, 17.5

        mode_cpt_drain = st.radio(
            "Pilih Asumsi Analisis Tanah dari Data Sondir:",
            [
                "Analisis Tegangan Total (Undrained: φ = 0° untuk Lempung Jenuh, c = cu)",
                "Analisis Tegangan Efektif (Drained: Sudut Geser Efektif φ' > 0°, c' ≈ 5-10 kPa)"
            ],
            index=0,
            key="mode_cpt_drain"
        )
        use_eff_cpt = "Efektif" in mode_cpt_drain

        final_cpt_c = round(avg_cu, 1) if not use_eff_cpt else 10.0
        final_cpt_phi = round(avg_phi, 1) if not use_eff_cpt else round(avg_phi_eff, 1)

        st.html(f"""
        <div class="dark-card" style="border: 2px solid #06B6D4; margin-top:12px;">
            <div style="font-size:0.85rem; font-weight:800; color:#06B6D4; text-transform:uppercase;">
                🎯 RANGKUMAN SONDIR ZONA FONDASI DANGKAL (0 - 3.0 m)
            </div>
            <div style="display:flex; justify-content:space-between; margin-top:10px; flex-wrap:wrap; gap:8px;">
                <span>Rata-rata qc: <strong style="color:#FBBF24;">{avg_qc:.1f} kg/cm²</strong></span>
                <span>Tegangan Geser fs: <strong style="color:#38BDF8;">{avg_fs:.1f} kPa</strong></span>
                <span>Kuat Geser cu: <strong style="color:#F472B6;">{avg_cu:.1f} kPa</strong></span>
                <span>Rasio Gesek FR: <strong style="color:#EC4899;">{avg_fr:.2f}%</strong></span>
                <span>Estimasi φ: <strong style="color:#34D399;">{final_cpt_phi:.1f}°</strong></span>
            </div>
        </div>
        """)

        with st.expander("💡 Penjelasan Ilmiah: Tegangan Geser & Kuat Geser dari Uji Sondir (CPT)"):
            st.markdown(r"""
            **1. Apakah Nilai Geser dari Sondir Bisa Ditemukan?**  
            **BISA dan SANGAT JELAS.** Terdapat 2 parameter geser utama dari uji sondir:
            - **Tegangan Geser Selimut Konus ($f_s$ / Hambatan Setempat):**  
              Diukur langsung oleh selimut geser bikonus Begemann ($A_g = 100 \text{ cm}^2$):  
              $$f_s = \frac{JH - q_c}{10} \text{ (kg/cm}^2\text{)} \times 98.07 \text{ (kPa)}$$  
              Nilai ini menunjukkan gesekan geser langsung antara selimut konus baja dan butiran tanah.
            - **Kuat Geser Undrained Tanah ($c_u$):**  
              Dihitung menggunakan korelasi baku Robertson & Campanella (1986):  
              $$c_u = \frac{q_c \times 98.07}{N_k} \text{ (kPa)}$$  
              di mana faktor konus $N_k \approx 14 - 18$ (digunakan $N_k = 16$).
            - **Sudut Geser Efektif ($\phi'$):**  
              Untuk tanah berbutir/pasir, Robertson (1983) merumuskan $\phi' = \arctan[0.1 + 0.38 \log(q_c/\sigma'_{v0})]$ (berkisar antara $30^\circ - 42^\circ$).
            """)

        if st.button("🚀 Terapkan Parameter Hasil Sondir ke Perencanaan Pondasi", type="primary", use_container_width=True):
            st.session_state.soil_params = {
                "status": "Siap Digunakan (Hasil Sondir CPT)",
                "source": "Uji Sondir Bikonus 2.5 Ton (CPT)",
                "soil_type": f"Hasil Sondir (qc={avg_qc:.1f} kg/cm², FR={avg_fr:.2f}%)",
                "cohesion": final_cpt_c,
                "cu": round(avg_cu, 1),
                "friction_angle": final_cpt_phi,
                "phi_eff": round(avg_phi_eff, 1),
                "unit_weight": round(avg_gamma, 1),
                "sat_unit_weight": round(avg_gamma + 1.8, 1),
                "water_table": mat_cpt
            }
            st.success("✅ Parameter Sondir CPT berhasil ditransfer ke Tab Perencanaan Pondasi!")

    with col_graph_cpt:
        st.markdown("#### 🖼️ Visualisasi Penetrasi Sondir (2D & 3D)")
        tab_cpt_2d, tab_cpt_3d = st.tabs([
            "📈 Grafik 2D Terpadu (qc, JHP, & FR)",
            "🌍 Model Blok 3D Sondir Bawah Permukaan"
        ])
        with tab_cpt_2d:
            fig_cpt_single = plot_single_unified_cpt_chart(processed_cpt, gw_depth=mat_cpt)
            st.plotly_chart(fig_cpt_single, use_container_width=True)
        with tab_cpt_3d:
            st.caption("💡 **Model 3D Bawah Permukaan CPT:** Menampilkan variasi nilai tahanan konus qc dan klasifikasi tanah sepanjang penetrasi konus dalam ruang 3D.")
            fig_cpt_3d = plot_subsurface_block_3d(
                layers=None,
                gw_depth=mat_cpt,
                borehole_id="Titik Sondir S-01",
                test_type="CPT",
                cpt_points=processed_cpt
            )
            st.plotly_chart(fig_cpt_3d, use_container_width=True)

        # Kartu Legenda Keterangan Warna Lengkap
        st.html("""
        <div class="dark-card" style="border: 1px solid #334155; margin-top:8px; font-size:0.85rem; line-height:1.6;">
            <div style="font-weight:750; color:#38BDF8; margin-bottom:6px;">📖 Panduan & Legenda Warna Grafik:</div>
            <ul style="margin:0; padding-left:18px; color:#CBD5E1;">
                <li><strong style="color:#06B6D4;">🔵 Garis Biru Cyan:</strong> Tahanan Konus (qc, kg/cm²) — Bacaan ujung perlawanan tanah (skala sumbu bawah).</li>
                <li><strong style="color:#10B981;">🟢 Garis Hijau (Putus-putus):</strong> Total Friksi (JHP, kg/cm) — Akumulasi hambatan geser selimut konus (skala sumbu bawah).</li>
                <li><strong style="color:#F59E0B;">🟠 Garis Oranye:</strong> Rasio Gesekan (FR, %) — Rasio friksi selimut terhadap ujung (skala sumbu atas).</li>
                <li><strong style="color:#EF4444;">🔴 Garis Merah (Putus-putus):</strong> Batas Tanah Keras (qc ≥ 150 kg/cm²) — Kedalaman lapisan tanah pendukung fondasi.</li>
                <li><strong style="color:#38BDF8;">💧 Garis Biru Titik-titik:</strong> Posisi Muka Air Tanah (▽ MAT).</li>
            </ul>
        </div>
        """)


# =========================================================================
# TAB 3: MODE CEPAT PENGGUNA AWAM (TANPA UJI LAB / ESTIMASI LAPANGAN)
# =========================================================================
with tab_layman:
    st.markdown("### 🏡 Mode Cepat Pengguna Awam (Tanpa Uji Bor/Sondir — Estimasi Lapangan)")
    
    st.markdown("""
    <div class="dark-card" style="border: 2px solid #10B981; background: rgba(6, 78, 59, 0.15);">
        <h4 style="color:#34D399; margin-top:0;">👋 Panduan Sederhana untuk Pemula / Masyarakat Umum:</h4>
        <p style="color:#E2E8F0; line-height:1.6; margin-bottom:0;">
            Apakah Anda pemilik rumah, kontraktor pemula, atau perencana yang <strong>belum memiliki hasil uji bor (SPT) maupun sondir (CPT) dari laboratorium</strong>? 
            Jangan khawatir! Anda tetap dapat merencanakan pondasi secara aman dengan memilih <strong>kondisi fisik tanah yang tampak di lokasi tanah Anda</strong> di bawah ini. 
            Sistem TAPAK CERDAS akan memilihkan parameter tanah yang <em>aman dan konservatif</em> sesuai buku ajar Geoteknik & Fondasi.
        </p>
    </div>
    """, unsafe_allow_html=True)

    LAYMAN_PRESETS = [
        {
            "id": "sawah",
            "icon": "🌾",
            "title": "Tanah Lunak / Bekas Sawah / Rawa / Dekat Sungai",
            "desc": "Kondisi fisik: Tanah lembek, becek saat musim hujan, jejak kaki mudah amblas, tanah liat hitam atau abu-abu pekat.",
            "c": 20.0, "phi": 0.0, "gamma": 16.0, "gamma_sat": 17.5, "n_eq": "2 - 4",
            "recom": "Daya dukung rendah. Disarankan menggunakan pondasi telapak yang diperlebar (minimal 1.5 x 1.5 m) atau diberi lapisan perbaikan pasir/sirtu setebal 50 cm."
        },
        {
            "id": "pekarangan",
            "icon": "🏡",
            "title": "Tanah Pekarangan Biasa / Kebun / Pemukiman Standar (Rekomendasi Umum)",
            "desc": "Kondisi fisik: Tanah lempung sedang, cukup padat, mudah digali cangkul, permukaan kering tidak retak parah, kondisi tanah stabil.",
            "c": 35.0, "phi": 12.0, "gamma": 17.5, "gamma_sat": 19.0, "n_eq": "6 - 10",
            "recom": "Kondisi sangat ideal untuk rumah tinggal 1 s/d 3 lantai menggunakan pondasi telapak dangkal standar (1.2 x 1.2 m s/d 1.6 x 1.6 m)."
        },
        {
            "id": "bukit",
            "icon": "⛰️",
            "title": "Tanah Perbukitan / Lempung Keras / Tanah Padas",
            "desc": "Kondisi fisik: Tanah sangat padat, keras, sulit dicangkul (membutuhkan linggis), berwarna coklat kemerahan atau kekuningan.",
            "c": 80.0, "phi": 22.0, "gamma": 19.5, "gamma_sat": 21.0, "n_eq": "15 - 30",
            "recom": "Daya dukung tinggi. Pondasi telapak dengan dimensi kompak (1.0 x 1.0 m) sudah sangat aman menopang bangunan."
        },
        {
            "id": "pantai",
            "icon": "🏖️",
            "title": "Tanah Berpasir / Tepi Pantai / Aliran Pasir",
            "desc": "Kondisi fisik: Butiran pasir bersih, air cepat meresap, dinding galian mudah runtuh saat basah/kering.",
            "c": 0.0, "phi": 32.0, "gamma": 18.0, "gamma_sat": 19.5, "n_eq": "10 - 20",
            "recom": "Kohesi nol (butiran lepas), namun memiliki sudut geser baik. Pondasi dangkal aman asalkan dijaga dari gerusan aliran air."
        },
        {
            "id": "kerikil",
            "icon": "🪨",
            "title": "Tanah Berkerikil Padat / Sirtu / Padas Keras",
            "desc": "Kondisi fisik: Campuran kerikil, batu pecah, dan pasir padat. Sangat kokoh dan tidak berdeformasi.",
            "c": 0.0, "phi": 38.0, "gamma": 20.5, "gamma_sat": 22.0, "n_eq": "> 30",
            "recom": "Kapasitas dukung sangat tinggi. Sangat stabil untuk bangunan berat sekalipun."
        }
    ]

    pilihan_awam = st.radio(
        "Pilih Deskripsi Visual yang Paling Mirip dengan Lokasi Anda:",
        options=[f"{p['icon']} {p['title']}" for p in LAYMAN_PRESETS],
        index=1
    )

    selected_preset = next(p for p in LAYMAN_PRESETS if f"{p['icon']} {p['title']}" == pilihan_awam)

    st.html(f"""
    <div class="dark-card" style="border: 2px solid #38BDF8; margin-top:16px;">
        <div style="font-size:1.15rem; font-weight:800; color:#38BDF8; margin-bottom:6px;">
            {selected_preset['icon']} {selected_preset['title']}
        </div>
        <p style="color:#E2E8F0; font-size:0.95rem; margin-bottom:8px;">{selected_preset['desc']}</p>
        <div style="background:rgba(15, 23, 42, 0.8); padding:10px 14px; border-radius:8px; border-left:4px solid #10B981; margin:12px 0;">
            <strong style="color:#34D399;">💡 Rekomendasi Pondasi Lapangan:</strong>
            <span style="color:#CBD5E1; font-size:0.9rem;"> {selected_preset['recom']}</span>
        </div>
        <div style="display:flex; gap:30px; margin-top:14px; border-top:1px solid #334155; padding-top:10px;">
            <span>Kohesi c: <strong style="color:#F472B6;">{selected_preset['c']} kPa</strong></span>
            <span>Sudut Geser φ: <strong style="color:#38BDF8;">{selected_preset['phi']}°</strong></span>
            <span>Berat Isi Basah γ: <strong style="color:#34D399;">{selected_preset['gamma']} kN/m³</strong></span>
            <span>Ekuivalen N-SPT: <strong style="color:#FBBF24;">{selected_preset['n_eq']}</strong></span>
        </div>
    </div>
    """)

    if st.button("🚀 Terapkan Pilihan Tanah Ini & Lanjut ke Perencanaan Pondasi", type="primary", use_container_width=True):
        st.session_state.soil_params = {
            "status": "Siap Digunakan",
            "source": f"Mode Cepat Pengguna Awam ({selected_preset['title']})",
            "soil_type": selected_preset["title"],
            "cohesion": selected_preset["c"],
            "friction_angle": selected_preset["phi"],
            "unit_weight": selected_preset["gamma"],
            "sat_unit_weight": selected_preset["gamma_sat"],
            "water_table": float(st.session_state.project_info.get("water_table_depth", 1.50))
        }
        st.success(f"✅ Parameter '{selected_preset['title']}' berhasil disimpan! Silakan klik menu 'Perencanaan Pondasi' di sidebar sebelah kiri.")
