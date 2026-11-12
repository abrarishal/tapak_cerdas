"""
=============================================================================
TAPAK CERDAS - RIWAYAT PROYEK & PUSAT EKSPOR LAPORAN
=============================================================================
File: pages/3_Riwayat_Laporan.py
Deskripsi: Manajemen database proyek lokal (Simpan, Muat Kembali, Hapus),
           Kotak Masuk Klien (Data Pengguna Lain yang Telah Masuk),
           serta Panduan Berbagi Akses Online/LAN.
=============================================================================
"""

import streamlit as st
import pandas as pd
import os
import sys

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from database.db_manager import (
    load_all_projects,
    save_project,
    delete_project,
    load_client_submissions,
    SUBMISSIONS_EXCEL
)
from utils.excel_exporter import generate_excel_report, generate_csv_report
from modules.dxf_exporter import generate_foundation_dxf
from modules.bearing_capacity import calculate_terzaghi, calculate_meyerhof, calculate_vesic, calculate_hansen

# Konfigurasi Halaman
st.set_page_config(page_title="Riwayat & Laporan - TAPAK CERDAS", page_icon="📑", layout="wide")

# Muat CSS Dark
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
        st.button("🖨️ Cetak Laporan", type="primary", use_container_width=True)

# Sub-Navbar Horizontal Tabs Persis PDF
c_nav1, c_nav2, c_nav3, c_nav4 = st.columns(4)
with c_nav1:
    if st.button("🏠 Dashboard Utama", use_container_width=True):
        st.switch_page("app.py")
with c_nav2:
    if st.button("🔬 1. Korelasi N-SPT / CPT & Stratigrafi", use_container_width=True):
        st.switch_page("pages/1_Analisis_Tanah.py")
with c_nav3:
    if st.button("🏛️ 2. Analisis Beban & 4 Metode Fondasi", use_container_width=True):
        st.switch_page("pages/2_Perencanaan_Pondasi.py")
with c_nav4:
    st.button("📑 3. Riwayat / Masuk Klien", type="primary", use_container_width=True)

st.markdown("<div style='margin-bottom: 1rem;'></div>", unsafe_allow_html=True)

# Pastikan State Ada
if "project_info" not in st.session_state:
    st.session_state.project_info = {"name": "Proyek Gedung Contoh", "location": "Semarang", "water_table_depth": 1.5}
if "soil_params" not in st.session_state:
    st.session_state.soil_params = {"soil_type": "Lempung Sedang", "cohesion": 35.0, "friction_angle": 12.0, "unit_weight": 17.5, "sat_unit_weight": 19.0}
if "load_params" not in st.session_state:
    st.session_state.load_params = {"building_function": "Rumah Tinggal", "floors": 2, "floor_area": 100.0, "p_column": 320.0, "pu_column": 430.0}

tab_history, tab_inbox = st.tabs([
    "📁 1. Proyek Saya (Database & Ekspor Laporan)",
    "🔒 2. Kotak Masuk Klien (Khusus Pemilik Aplikasi)"
])

# =========================================================================
# TAB 1: PROYEK SAYA (SIMPAN, MUAT, DAN UNDUH LAPORAN)
# =========================================================================
with tab_history:
    col_main1, col_main2 = st.columns([1.2, 1.8])

    with col_main1:
        st.markdown("### 💾 Simpan Proyek Saat Ini")
        st.caption("Simpan seluruh data investigasi tanah, beban gedung, dan ukuran pondasi ke database lokal.")
        
        nama_proyek = st.text_input("Nama Proyek:", value=st.session_state.project_info.get("name", "Proyek Baru"))
        lokasi_proyek = st.text_input("Lokasi / Alamat:", value=st.session_state.project_info.get("location", "Semarang"))
        catatan_proyek = st.text_area("Catatan Tambahan Teknis:", value="Perencanaan awal pondasi telapak aman di 4 metode.")

        if st.button("💾 Simpan ke Database Riwayat", type="primary", use_container_width=True):
            st.session_state.project_info["name"] = nama_proyek
            st.session_state.project_info["location"] = lokasi_proyek
            
            save_data = {
                "name": nama_proyek,
                "location": lokasi_proyek,
                "notes": catatan_proyek,
                "soil_params": st.session_state.soil_params,
                "load_params": st.session_state.load_params,
                "water_table_depth": st.session_state.project_info.get("water_table_depth", 1.5)
            }
            save_project(save_data)
            st.success(f"✅ Proyek '{nama_proyek}' berhasil disimpan!")
            st.rerun()

    with col_main2:
        st.markdown("### 📥 Pusat Pengunduhan Berkas Laporan Resmi")
        st.caption("Unduh berkas Microsoft Excel lengkap yang berisi rincian data pembebanan SNI 1727:2020, data tanah, dan komparasi 4 metode.")
        
        soil = st.session_state.soil_params
        c_val = float(soil.get("cohesion", 35.0))
        phi_val = float(soil.get("friction_angle", 12.0))
        gam_val = float(soil.get("unit_weight", 17.5))
        gam_sat_val = float(soil.get("sat_unit_weight", gam_val + 1.5))
        mat_val = float(st.session_state.project_info.get("water_table_depth", 1.50))
        p_act = float(st.session_state.load_params.get("p_column", 350.0))
        
        # Dimensi default pondasi untuk laporan rekap
        b_val, l_val, df_val = 1.50, 1.50, 1.50
        sf_target = 3.0
        
        res_t = calculate_terzaghi(c_val, phi_val, gam_val, gam_sat_val, b_val, l_val, df_val, mat_val)
        res_m = calculate_meyerhof(c_val, phi_val, gam_val, gam_sat_val, b_val, l_val, df_val, mat_val)
        res_v = calculate_vesic(c_val, phi_val, gam_val, gam_sat_val, b_val, l_val, df_val, mat_val)
        res_h = calculate_hansen(c_val, phi_val, gam_val, gam_sat_val, b_val, l_val, df_val, mat_val)
        
        # Hitung tegangan kontak dan SF aktual
        hf = 0.40
        area = b_val * l_val
        q_kontak = (p_act / area) + (24.0 * hf) + (gam_val * (df_val - hf))
        
        comp_summary = []
        for res in [res_t, res_m, res_v, res_h]:
            qu = res["qu"]
            po = res["po"]
            qun = qu - po
            qall = (qun / sf_target) + po
            sf_act = qu / q_kontak if q_kontak > 0 else 99.0
            comp_summary.append({
                "metode": res["metode"],
                "Nc": res["Nc"],
                "Nq": res["Nq"],
                "Ngamma": res["Ngamma"],
                "qu": round(qu, 1),
                "qall": round(qall, 1),
                "q_kontak": round(q_kontak, 1),
                "sf_aktual": round(sf_act, 2),
                "status": "AMAN (OK)" if sf_act >= sf_target else "TIDAK AMAN"
            })
        
        ex_bytes = generate_excel_report(
            project_info=st.session_state.project_info,
            soil_params=soil,
            load_params=st.session_state.load_params,
            comp_results=comp_summary,
            selected_dim={"B": 1.5, "L": 1.5, "Df": 1.5, "SF": 3.0}
        )
        
        csv_txt = generate_csv_report(comp_summary, {"B": 1.5, "L": 1.5, "Df": 1.5})
        dxf_bytes = generate_foundation_dxf(
            B_m=1.5, L_m=1.5, hf_m=0.40, Df_m=1.5,
            project_info=st.session_state.project_info
        )

        col_dl1, col_dl2, col_dl3 = st.columns([1.5, 1.5, 1.0])
        with col_dl1:
            st.download_button(
                "📊 Unduh Laporan Lengkap Excel (.xlsx)",
                data=ex_bytes,
                file_name=f"Laporan_Geoteknik_{st.session_state.project_info.get('name', 'Pondasi').replace(' ', '_')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                type="primary",
                use_container_width=True,
                key="btn_dl_riwayat_excel"
            )
        with col_dl2:
            st.download_button(
                "📐 Unduh Gambar AutoCAD (.dxf)",
                data=dxf_bytes,
                file_name=f"Gambar_Kerja_{st.session_state.project_info.get('name', 'Pondasi').replace(' ', '_')}.dxf",
                mime="application/dxf",
                use_container_width=True,
                key="btn_dl_riwayat_cad_dxf"
            )
        with col_dl3:
            st.download_button(
                "📄 Unduh Ringkasan CSV (.csv)",
                data=csv_txt,
                file_name="Rekapitulasi_Komparasi_4_Metode.csv",
                mime="text/csv",
                use_container_width=True,
                key="btn_dl_riwayat_csv"
            )

    st.markdown("---")

    # DAFTAR RIWAYAT PROYEK TERSIMPAN
    st.markdown("### 🗄️ Daftar Riwayat Proyek yang Tersimpan:")
    saved_projs = load_all_projects()

    if not saved_projs:
        st.info("ℹ️ Belum ada proyek yang tersimpan di database lokal. Simpan proyek pertama Anda di panel sebelah kiri.")
    else:
        for p in saved_projs:
            with st.container():
                c_p1, c_p2, c_p3 = st.columns([3, 1, 1])
                with c_p1:
                    st.html(f"""
                    <div style="background:rgba(30, 41, 59, 0.7); padding:12px 18px; border-radius:10px; border-left:4px solid #38BDF8; margin-bottom:8px;">
                        <div style="font-weight:750; color:#F8FAFC; font-size:1.05rem;">{p.get('name')}</div>
                        <div style="font-size:0.85rem; color:#94A3B8;">Lokasi: {p.get('location')} | Disimpan: {p.get('saved_at', '-')}</div>
                        <div style="font-size:0.82rem; color:#60A5FA; margin-top:4px;">Catatan: {p.get('notes', '-')}</div>
                    </div>
                    """)
                with c_p2:
                    st.write("")
                    if st.button("📂 Muat Proyek", key=f"load_{p.get('name')}", use_container_width=True):
                        st.session_state.project_info["name"] = p.get("name")
                        st.session_state.project_info["location"] = p.get("location")
                        if "soil_params" in p:
                            st.session_state.soil_params = p["soil_params"]
                        if "load_params" in p:
                            st.session_state.load_params = p["load_params"]
                        st.success(f"✅ Proyek '{p.get('name')}' berhasil dimuat!")
                        st.rerun()
                with c_p3:
                    st.write("")
                    if st.button("🗑️ Hapus", key=f"del_{p.get('name')}", use_container_width=True):
                        delete_project(p.get("name"))
                        st.warning(f"Proyek '{p.get('name')}' telah dihapus.")
                        st.rerun()


# =========================================================================
# TAB 2: KOTAK MASUK KLIEN (KHUSUS PEMILIK APLIKASI - TERPROTEKSI PIN)
# =========================================================================
with tab_inbox:
    st.markdown("### 🔒 Kotak Masuk Klien & Rekapitulasi Data (Khusus Pemilik)")
    st.caption("Data pengajuan dari klien atau pengguna umum bersifat privat dan hanya dapat dibuka oleh pemilik aplikasi menggunakan PIN Keamanan.")

    if "admin_logged_in" not in st.session_state:
        st.session_state.admin_logged_in = False

    if not st.session_state.admin_logged_in:
        col_lock1, col_lock2, col_lock3 = st.columns([1, 2, 1])
        with col_lock2:
            st.html("""
            <div style="background: rgba(30, 41, 59, 0.85); border: 1px solid rgba(56, 189, 248, 0.3); border-radius: 14px; padding: 24px; text-align: center; margin-top: 15px; box-shadow: 0 8px 32px rgba(0,0,0,0.4);">
                <div style="font-size: 2.8rem; margin-bottom: 8px;">🔐</div>
                <h3 style="color: #38BDF8; margin: 0 0 8px 0;">Autentikasi Pemilik Aplikasi</h3>
                <p style="color: #94A3B8; font-size: 0.88rem; line-height: 1.5; margin-bottom: 16px;">
                    Untuk melindungi privasi nomor WhatsApp dan rancangan struktur klien Anda dari pengunjung umum, silakan masukkan PIN Admin di bawah ini.
                </p>
                <div style="display:inline-block; background:rgba(56, 189, 248, 0.1); border:1px dashed #38BDF8; border-radius:8px; padding:6px 14px; font-size:0.8rem; color:#7DD3FC; margin-bottom:15px;">
                    🔑 Default PIN Pemilik: <b>1234</b>
                </div>
            </div>
            """)
            pin_input = st.text_input("Masukkan PIN Keamanan Admin:", type="password", key="admin_pin_input")
            if st.button("🔓 Buka Akses Kotak Masuk Klien", type="primary", use_container_width=True):
                if pin_input == "1234":
                    st.session_state.admin_logged_in = True
                    st.success("✅ Autentikasi berhasil! Selamat datang, Pemilik Proyek.")
                    st.rerun()
                else:
                    st.error("❌ PIN yang Anda masukkan salah. Default PIN adalah: 1234")
    else:
        # Tampilan setelah login admin
        c_head1, c_head2 = st.columns([3, 1])
        with c_head1:
            st.html("""
            <div style="display:inline-flex; align-items:center; gap:8px; background:rgba(16, 185, 129, 0.15); border:1px solid #10B981; border-radius:8px; padding:6px 14px; color:#34D399; font-size:0.88rem; font-weight:600; margin-bottom:12px;">
                <span>🔓 Mode Pemilik Aktif — Akses Kotak Masuk Terbuka</span>
            </div>
            """)
        with c_head2:
            if st.button("🔒 Kunci Kembali", use_container_width=True):
                st.session_state.admin_logged_in = False
                st.rerun()

        client_subs = load_client_submissions()

        if not client_subs:
            st.info("ℹ️ Belum ada data pengajuan dari pengguna lain. Ketika pengguna lain mengisi di halaman 'Perencanaan Pondasi' dan menekan tombol 'Kirim Data', datanya akan langsung otomatis masuk ke sini dan tersimpan di berkas Excel master!")
        else:
            st.success(f"Ditemukan **{len(client_subs)} pengajuan desain** dari pengguna lain!")
            
            # Tombol Unduh Excel Rekapitulasi Master
            if os.path.exists(SUBMISSIONS_EXCEL):
                with open(SUBMISSIONS_EXCEL, "rb") as f_sub_ex:
                    st.download_button(
                        "📥 Unduh Seluruh Rekap Data Pengguna Masuk (.xlsx Master)",
                        data=f_sub_ex.read(),
                        file_name="Rekap_Data_Pengguna_Masuk.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        type="primary",
                        key="btn_dl_master_submissions"
                    )

            st.markdown("#### 📋 Tabel Pengajuan Desain dari Pengguna:")
            
            inbox_html = """
            <div class="geo-table-dark-container">
            <table class="geo-table-dark">
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Waktu Pengiriman</th>
                        <th>Nama Pengguna</th>
                        <th>WhatsApp</th>
                        <th>Proyek & Lokasi</th>
                        <th>Beban P (kN)</th>
                        <th>Dimensi (B x L x Df)</th>
                        <th>SF Terendah</th>
                        <th>Status Kelayakan</th>
                    </tr>
                </thead>
                <tbody>
            """
            for s in client_subs:
                status_badge = "pill-safe" if "AMAN" in s.get("status", "") else "pill-danger"
                inbox_html += f"""
                <tr>
                    <td style="font-weight:750; color:#38BDF8;">{s.get('id', '')}</td>
                    <td style="font-size:0.85rem; color:#94A3B8;">{s.get('submitted_at', '')}</td>
                    <td style="font-weight:700; color:#F8FAFC;">{s.get('client_name', '-')}</td>
                    <td style="color:#22C55E;">{s.get('client_wa', '-')}</td>
                    <td>{s.get('project_name', '')} ({s.get('location', '')})</td>
                    <td style="color:#FBBF24; font-weight:700;">{s.get('p_column', 0.0):.1f} kN</td>
                    <td>{s.get('width_b', 0.0)} x {s.get('length_l', 0.0)} x {s.get('depth_df', 0.0)} m</td>
                    <td style="font-weight:750;">{s.get('min_sf', 0.0):.2f}</td>
                    <td><span class="pill-status {status_badge}">{s.get('status', 'AMAN')}</span></td>
                </tr>
                """
            inbox_html += "</tbody></table></div>"
            st.html(inbox_html)

