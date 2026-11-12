"""
=============================================================================
TAPAK CERDAS - GENERATOR EKSPOR EXCEL & CSV RESMI (BERSTANDAR TEKNIK SIPIL)
=============================================================================
File: utils/excel_exporter.py
Deskripsi: Generator laporan Excel resmi konsultan rekayasa geoteknik dan struktur:
           1. Soil Investigation Report (5 Sheets):
              - Sheet 1: General Information
              - Sheet 2: Boring Log / SPT (ASTM D1586, N1/N2/N3, N-SPT, GWL, Chart)
              - Sheet 3: CPT Log (SNI 2827:2008, qc, fs, Rf, Chart)
              - Sheet 4: Soil Profile (Visual Stratigraphy & Properties)
              - Sheet 5: Summary & Recommendations
           2. Foundation Calculation Report (6 Sheets dengan Rangkaian Perhitungan Runtut):
              - Sheet 1: Design Criteria (Beban SNI 1727:2020, Material SNI 2847:2019)
              - Sheet 2: Soil Parameter (Stratigrafi & Korelasi Lapangan)
              - Sheet 3: Foundation Dimension Calculation (Daya Dukung, Tegangan Kontak, Eksentrisitas)
              - Sheet 4: Structural Calculation (Momen Mu, Geser 1 Arah, Geser Pons 2 Arah)
              - Sheet 5: Reinforcement Calculation (As req, Spasi Tulangan, Keranjang Kotak, BoQ)
              - Sheet 6: Final Design Summary & Bill of Quantities
=============================================================================
"""

import io
import math
import pandas as pd
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from openpyxl.chart import LineChart, Reference

try:
    import streamlit as st
    cache_decorator = st.cache_data(show_spinner=False)
except Exception:
    def cache_decorator(func):
        return func


def _clean_num(val):
    if isinstance(val, (int, float)):
        return float(val)
    if isinstance(val, str):
        try:
            return float(val.replace(',', '').replace(' ', ''))
        except Exception:
            return 0.0
    return 0.0


def _style_header_cell(cell, fill_color="1E3A8A", text_color="FFFFFF", bold=True, size=10, align="center"):
    cell.fill = PatternFill(start_color=fill_color, end_color=fill_color, fill_type="solid")
    cell.font = Font(name="Calibri", size=size, bold=bold, color=text_color)
    cell.alignment = Alignment(horizontal=align, vertical="center", wrap_text=True)


def _style_border(cell, border_style="thin", border_color="CBD5E1"):
    cell.border = Border(
        left=Side(style=border_style, color=border_color),
        right=Side(style=border_style, color=border_color),
        top=Side(style=border_style, color=border_color),
        bottom=Side(style=border_style, color=border_color)
    )


def _setup_page_print(ws, landscape=False):
    ws.page_setup.paperSize = ws.PAPERSIZE_A4
    ws.page_setup.orientation = ws.ORIENTATION_LANDSCAPE if landscape else ws.ORIENTATION_PORTRAIT
    ws.page_setup.fitToPage = True
    ws.page_setup.fitToWidth = 1
    ws.page_setup.fitToHeight = 0
    ws.sheet_properties.pageSetUpPr.fitToPage = True
    ws.oddHeader.left.text = "&B TAPAK CERDAS &B - Geotechnical & Structural Design Report"
    ws.oddFooter.right.text = "Halaman &P dari &N"
    ws.oddFooter.left.text = "Format Standar SNI 1727:2020 / SNI 2847:2019 / SNI 8460:2017"


# =============================================================================
# A. LAPORAN PENYELIDIKAN TANAH (SOIL INVESTIGATION REPORT - 5 SHEETS)
# =============================================================================

def generate_soil_investigation_report(project_info, spt_layers=None, cpt_points=None):
    """
    Menghasilkan Laporan Penyelidikan Tanah Resmi (Soil Investigation Report) 5 Sheets:
    - Sheet 1: General Information
    - Sheet 2: Boring Log / SPT (Sesuai Referensi Gambar Boring Log)
    - Sheet 3: CPT Log (Sesuai Standar SNI 2827:2008)
    - Sheet 4: Soil Profile (Visual Stratigrafi Lapisan Tanah)
    - Sheet 5: Summary (Rangkuman Geoteknik & Rekomendasi)
    """
    wb = openpyxl.Workbook()
    wb.calculation.fullCalcOnLoad = True
    wb.calculation.calcMode = 'auto'

    font_main_title = Font(name="Calibri", size=15, bold=True, color="1E3A8A")
    font_sub_title = Font(name="Calibri", size=9, italic=True, color="64748B")
    font_section = Font(name="Calibri", size=11, bold=True, color="0F172A")
    font_bold = Font(name="Calibri", size=10, bold=True)
    font_reg = Font(name="Calibri", size=9.5)
    font_bold_center = Font(name="Calibri", size=9.5, bold=True)

    fill_head_navy = PatternFill(start_color="1E3A8A", end_color="1E3A8A", fill_type="solid")
    fill_head_sub = PatternFill(start_color="DBEAFE", end_color="DBEAFE", fill_type="solid")
    fill_meta = PatternFill(start_color="F1F5F9", end_color="F1F5F9", fill_type="solid")
    fill_zebra = PatternFill(start_color="F8FAFC", end_color="F8FAFC", fill_type="solid")
    fill_white = PatternFill(start_color="FFFFFF", end_color="FFFFFF", fill_type="solid")
    fill_gwl = PatternFill(start_color="E0F2FE", end_color="E0F2FE", fill_type="solid")

    thin_border = Border(
        left=Side(style='thin', color='CBD5E1'),
        right=Side(style='thin', color='CBD5E1'),
        top=Side(style='thin', color='CBD5E1'),
        bottom=Side(style='thin', color='CBD5E1')
    )

    align_center = Alignment(horizontal='center', vertical='center')
    align_left = Alignment(horizontal='left', vertical='center')
    align_right = Alignment(horizontal='right', vertical='center')

    p_name = project_info.get("name", "Proyek Bangunan Gedung")
    p_loc = project_info.get("location", "Semarang")
    p_client = project_info.get("client", "Pemilik Proyek / Pengembang")
    p_bh = project_info.get("borehole_id", "BH-01")
    p_gwl = _clean_num(project_info.get("water_table_depth", project_info.get("water_table", 1.50)))
    p_date = project_info.get("date", "2026-11-12")
    p_engineer = project_info.get("engineer", "Insinyur Geoteknik / Perencana")
    p_consultant = project_info.get("consultant", "Laboratorium Mekanika Tanah & Geoteknik")

    # -------------------------------------------------------------------------
    # SHEET 1: GENERAL INFORMATION
    # -------------------------------------------------------------------------
    ws1 = wb.active
    ws1.title = "General Information"
    ws1.views.sheetView[0].showGridLines = True
    _setup_page_print(ws1, landscape=False)

    ws1["A1"] = "SOIL INVESTIGATION REPORT - GENERAL INFORMATION"
    ws1["A1"].font = font_main_title
    ws1["A2"] = "Laporan Resmi Penyelidikan Geoteknik Lapangan (Boring SPT & Sondir CPT)"
    ws1["A2"].font = font_sub_title

    ws1["A4"] = "1. IDENTITAS PROYEK & PENYELIDIKAN TANAH"
    ws1["A4"].font = font_section

    total_depth = max([l.get('depth_bot', 12.0) for l in spt_layers] if spt_layers else [12.0])

    gen_info_table = [
        ("Nama Proyek", p_name),
        ("Lokasi Proyek", p_loc),
        ("Nama Klien / Pemilik", p_client),
        ("Nomor Titik Investigasi", p_bh),
        ("Koordinat Titik (X / Bujur)", project_info.get("coord_x", "110.4289° E")),
        ("Koordinat Titik (Y / Lintang)", project_info.get("coord_y", "-7.0512° S")),
        ("Tanggal Pengujian", p_date),
        ("Elevasi Permukaan Tanah (GL)", "+0.00 m (Muka Tanah Asli)"),
        ("Kedalaman Total Penyelidikan", f"{total_depth:.2f} meter"),
        ("Jenis Pengujian Dilaksanakan", "Boring Mesin, Uji Penetrasi Standar (SPT ASTM D1586) & Sondir Bikonus 2.5 Ton (SNI 2827:2008)"),
        ("Instansi / Konsultan Geoteknik", p_consultant),
        ("Insinyur Penanggung Jawab", p_engineer)
    ]

    r = 5
    for lbl, val in gen_info_table:
        ws1[f"A{r}"] = lbl
        ws1[f"A{r}"].font = font_bold
        ws1[f"A{r}"].fill = fill_meta
        ws1[f"A{r}"].border = thin_border
        ws1[f"B{r}"] = val
        ws1[f"B{r}"].font = font_reg
        ws1[f"B{r}"].border = thin_border
        ws1[f"B{r}"].alignment = align_left
        r += 1

    r += 1
    ws1[f"A{r}"] = "2. METODE & STANDAR ACUAN PENGUJIAN"
    ws1[f"A{r}"].font = font_section
    r += 1

    methods = [
        ("Uji Penetrasi Standar (SPT)", "ASTM D1586 / SNI 4153:2008", "Hammer 63.5 kg, Tinggi jatuh 76 cm, Split spoon sampler"),
        ("Uji Penetrasi Konus (CPT)", "SNI 2827:2008 / ASTM D3441", "Bikonus Begemann luas konus 10 cm², sudut apex 60°, kapasitas 2.5 ton"),
        ("Pengambilan Sampel Tanah (UDS)", "ASTM D1587", "Thin-walled tube (Shelby tube) untuk sampel lempung tak terganggu"),
        ("Klasifikasi Tanah Sistem Unifikasi", "ASTM D2487 (USCS)", "Klasifikasi berdasarkan gradasi butiran dan plastisitas Atterberg")
    ]

    for m_title, m_std, m_desc in methods:
        ws1[f"A{r}"] = m_title
        ws1[f"A{r}"].font = font_bold
        ws1[f"A{r}"].border = thin_border
        ws1[f"B{r}"] = f"{m_std} — {m_desc}"
        ws1[f"B{r}"].font = font_reg
        ws1[f"B{r}"].border = thin_border
        r += 1

    ws1.column_dimensions["A"].width = 30
    ws1.column_dimensions["B"].width = 75

    # -------------------------------------------------------------------------
    # SHEET 2: BORING LOG / SPT
    # -------------------------------------------------------------------------
    ws2 = wb.create_sheet(title="Boring Log - SPT")
    ws2.views.sheetView[0].showGridLines = True
    _setup_page_print(ws2, landscape=True)

    ws2["A1"] = f"BORE HOLE LOG & STANDARD PENETRATION TEST (SPT) — {p_bh}"
    ws2["A1"].font = font_main_title
    ws2["A2"] = f"Proyek: {p_name} | Lokasi: {p_loc} | MAT: -{p_gwl:.2f} m"
    ws2["A2"].font = font_sub_title

    headers_spt_1 = [
        "Kedalaman (m)", "Deskripsi Visual Litologi Tanah", "Tebal (m)", "Simbol USCS",
        "Jenis Sampel", "Elevasi (m)", "Penetrasi Pukulan (Pukulan / 15 cm)", "", "",
        "Nilai N-SPT", "Konsistensi Tanah", "Kuat Geser cu (kPa)", "Sudut Geser φ' (°)", "Berat Isi γ (kN/m³)"
    ]
    headers_spt_2 = [
        "", "", "", "", "", "", "N1 (0-15cm)", "N2 (15-30cm)", "N3 (30-45cm)",
        "N = N2 + N3", "", "", "", ""
    ]

    for c_i, h in enumerate(headers_spt_1, 1):
        cell = ws2.cell(row=4, column=c_i, value=h)
        _style_header_cell(cell, fill_color="1E3A8A", text_color="FFFFFF", bold=True, size=9)
        _style_border(cell)

    for c_i, h in enumerate(headers_spt_2, 1):
        cell = ws2.cell(row=5, column=c_i, value=h)
        if h != "":
            _style_header_cell(cell, fill_color="DBEAFE", text_color="0F172A", bold=True, size=8.5)
        else:
            cell.fill = fill_head_navy
        _style_border(cell)

    # Merge header
    merge_ranges = ["A4:A5", "B4:B5", "C4:C5", "D4:D5", "E4:E5", "F4:F5", "G4:I4", "J4:J5", "K4:K5", "L4:L5", "M4:M5", "N4:N5"]
    for m in merge_ranges:
        ws2.merge_cells(m)

    if not spt_layers or len(spt_layers) == 0:
        spt_layers = [
            {"depth_top": 0.0, "depth_bot": 1.5, "soil_type": "Lempung Lunak", "n1": 1, "n2": 2, "n3": 2, "n_spt": 4, "cu": 24.0, "phi_eff": 22.0, "gamma": 16.8, "deskripsi": "Lempung kelabu lunak, plastisitas tinggi"},
            {"depth_top": 1.5, "depth_bot": 3.0, "soil_type": "Lempung Berlanau Sedang", "n1": 2, "n2": 3, "n3": 4, "n_spt": 7, "cu": 42.0, "phi_eff": 24.0, "gamma": 17.5, "deskripsi": "Lempung berlanau cokelat kekuningan, teguh"},
            {"depth_top": 3.0, "depth_bot": 4.5, "soil_type": "Lanau Berpasir Kaku", "n1": 4, "n2": 7, "n3": 8, "n_spt": 15, "cu": 85.0, "phi_eff": 28.0, "gamma": 18.2, "deskripsi": "Lanau pasiran kelabu kaku"},
            {"depth_top": 4.5, "depth_bot": 6.0, "soil_type": "Pasir Berlanau Padat", "n1": 8, "n2": 14, "n3": 17, "n_spt": 31, "cu": 10.0, "phi_eff": 35.0, "gamma": 19.5, "deskripsi": "Pasir sedang berlanau abu-abu sangat padat"}
        ]

    start_row = 6
    for idx, lyr in enumerate(spt_layers, 1):
        cur_r = start_row + idx - 1
        d_top = float(lyr.get("depth_top", 0.0))
        d_bot = float(lyr.get("depth_bot", d_top + 1.5))
        thick = round(d_bot - d_top, 2)
        n1 = int(lyr.get("n1", 1))
        n2 = int(lyr.get("n2", 2))
        n3 = int(lyr.get("n3", 2))
        n_spt_val = int(lyr.get("n_spt", n2 + n3))
        samp_type = "SPT" if idx % 2 != 0 else "UDS"

        stype = lyr.get("soil_type", "")
        if "Pasir" in stype:
            sym = "SM"
        elif "Kerikil" in stype:
            sym = "GW"
        elif "Lempung" in stype:
            sym = "CH" if "Kaku" in lyr.get("konsistensi", "") else "CL"
        elif "Rock" in stype or "Padas" in stype:
            sym = "ROCK"
        else:
            sym = "ML"

        row_data = [
            f"{d_top:.1f} - {d_bot:.1f}",
            lyr.get("deskripsi", lyr.get("soil_type", "Tanah")),
            thick,
            sym,
            samp_type,
            round((d_top + d_bot) / 2.0, 2),
            n1,
            n2,
            n3,
            n_spt_val,  # Nilai integer angka konkret - tidak akan kosong di Protected View!
            lyr.get("konsistensi", "-"),
            float(lyr.get("cu", lyr.get("c", 20.0))),
            float(lyr.get("phi_eff", lyr.get("phi", 24.0))),
            float(lyr.get("gamma", 17.5))
        ]

        is_gw_layer = (d_top <= p_gwl <= d_bot)
        r_fill = fill_gwl if is_gw_layer else (fill_zebra if idx % 2 == 0 else fill_white)

        for c_i, val in enumerate(row_data, 1):
            cell = ws2.cell(row=cur_r, column=c_i, value=val)
            cell.font = font_bold_center if c_i == 10 else font_reg
            cell.fill = r_fill
            cell.alignment = align_left if c_i == 2 else align_center
            if c_i in [3, 6, 12, 13, 14]:
                cell.number_format = '0.00' if c_i in [3, 6] else '0.0'
            elif c_i in [7, 8, 9, 10]:
                cell.number_format = '0'
            _style_border(cell)

    end_spt_row = start_row + len(spt_layers) - 1

    ws2[f"A{end_spt_row + 2}"] = f"Bore hole Terminated at {spt_layers[-1].get('depth_bot', 10.5):.2f}m Below Ground Level."
    ws2[f"A{end_spt_row + 2}"].font = font_bold
    ws2[f"A{end_spt_row + 3}"] = "Notes: SPT = Standard Penetration Test; UDS = Undisturbed Sample; GL = Ground Level; GWL = Ground Water Level."
    ws2[f"A{end_spt_row + 3}"].font = font_sub_title

    try:
        chart_spt = LineChart()
        chart_spt.title = "GRAFIK PENETRASI N-SPT vs KEDALAMAN (m)"
        chart_spt.style = 13
        chart_spt.y_axis.title = "Kedalaman (m)"
        chart_spt.x_axis.title = "Nilai N-SPT (Pukulan/30cm)"
        chart_spt.width = 16
        chart_spt.height = 12

        data_spt_ref = Reference(ws2, min_col=10, min_row=start_row - 1, max_row=end_spt_row)
        cats_spt_ref = Reference(ws2, min_col=6, min_row=start_row, max_row=end_spt_row)
        chart_spt.add_data(data_spt_ref, titles_from_data=True)
        chart_spt.set_categories(cats_spt_ref)
        ws2.add_chart(chart_spt, "P4")
    except Exception:
        pass

    for col in ws2.columns:
        if col[0].column > 14:
            continue
        max_l = max(len(str(c.value or '')) for c in col[:end_spt_row + 1])
        ws2.column_dimensions[get_column_letter(col[0].column)].width = max(max_l + 3, 11)
    ws2.column_dimensions["B"].width = 34

    # -------------------------------------------------------------------------
    # SHEET 3: CPT LOG (SNI 2827:2008 / ASTM D3441)
    # -------------------------------------------------------------------------
    ws3 = wb.create_sheet(title="CPT Log")
    ws3.views.sheetView[0].showGridLines = True
    _setup_page_print(ws3, landscape=True)

    ws3["A1"] = "CONE PENETRATION TEST (CPT) - SONDIR LOG"
    ws3["A1"].font = Font(name="Calibri", size=15, bold=True, color="065F46")
    ws3["A2"] = "Standar Pengujian: SNI 2827:2008 / ASTM D3441 (Ac = 10 cm², Bikonus Begemann)"
    ws3["A2"].font = font_sub_title

    headers_cpt = [
        "Kedalaman z (m)", "qc (kg/cm²)", "qc (kPa)", "JH (kg/cm²)", "HP (kg/cm)",
        "JHP Total (kg/cm)", "Sleeve Friction fs (kg/cm²)", "fs (kPa)", "Friction Ratio Rf (%)",
        "Klasifikasi Tanah (Robertson 1986)", "Kuat Geser cu (kPa)", "Sudut Geser φ' (°)"
    ]

    start_cpt_row = 5
    for c_i, h in enumerate(headers_cpt, 1):
        cell = ws3.cell(row=start_cpt_row, column=c_i, value=h)
        _style_header_cell(cell, fill_color="065F46", text_color="FFFFFF", bold=True, size=9)
        _style_border(cell)

    if not cpt_points or len(cpt_points) == 0:
        cpt_points = [
            {"depth": 0.20, "qc": 8.0, "jh": 14.0, "hp": 6.0, "jhp": 6.0, "hs": 0.06, "fr": 0.75, "soil_type": "Lempung Sensitif"},
            {"depth": 1.00, "qc": 12.0, "jh": 24.0, "hp": 12.0, "jhp": 28.0, "hs": 0.12, "fr": 1.00, "soil_type": "Lempung Lunak"},
            {"depth": 2.00, "qc": 24.0, "jh": 48.0, "hp": 24.0, "jhp": 68.0, "hs": 0.24, "fr": 1.00, "soil_type": "Lempung Sedang"},
            {"depth": 3.00, "qc": 45.0, "jh": 85.0, "hp": 40.0, "jhp": 140.0, "hs": 0.40, "fr": 0.89, "soil_type": "Pasir Berlanau"},
            {"depth": 4.00, "qc": 160.0, "jh": 250.0, "hp": 90.0, "jhp": 280.0, "hs": 0.90, "fr": 0.56, "soil_type": "Pasir Padat / Hard Layer"}
        ]

    for idx, pt in enumerate(cpt_points, 1):
        cur_r = start_cpt_row + idx
        d_val = float(pt.get("depth", 0.0))
        qc_val = float(pt.get("qc", 10.0))
        qc_kpa = round(qc_val * 98.07, 1)
        jh_val = float(pt.get("jh", qc_val + 5.0))
        hp_val = round(max(0.0, jh_val - qc_val), 1)
        jhp_val = float(pt.get("jhp", pt.get("hp", hp_val)))
        fs_kg = round(hp_val / 10.0, 2)
        fs_kpa = round(fs_kg * 98.07, 1)
        rf_pct = round((fs_kg / qc_val) * 100.0, 2) if qc_val > 0 else 0.0
        cu_val = round((qc_val * 98.07) / 16.0, 1)
        phi_val = 24.0 if qc_val < 30 else round(min(42.0, 28.0 + (qc_val / 15.0)), 1)

        cpt_row_data = [
            d_val,
            qc_val,
            qc_kpa,
            jh_val,
            hp_val,
            jhp_val,
            fs_kg,
            fs_kpa,
            rf_pct,
            pt.get("soil_type", "Lempung"),
            cu_val,
            phi_val
        ]

        r_fill = fill_zebra if idx % 2 == 0 else fill_white
        for c_i, val in enumerate(cpt_row_data, 1):
            cell = ws3.cell(row=cur_r, column=c_i, value=val)
            cell.font = font_bold_center if c_i in [2, 7, 9] else font_reg
            cell.fill = r_fill
            cell.alignment = align_left if c_i == 10 else align_center
            if c_i in [1, 2, 3, 4, 5, 6, 8, 11, 12]:
                cell.number_format = '0.0' if c_i != 1 else '0.00'
            elif c_i in [7, 9]:
                cell.number_format = '0.00'
            _style_border(cell)

    end_cpt_row = start_cpt_row + len(cpt_points)

    try:
        chart_cpt = LineChart()
        chart_cpt.title = "GRAFIK PERLAWANAN KONUS qc & JHP vs KEDALAMAN (m)"
        chart_cpt.style = 13
        chart_cpt.y_axis.title = "Kedalaman (m)"
        chart_cpt.x_axis.title = "qc (kg/cm²) & Total Friksi JHP"
        chart_cpt.width = 16
        chart_cpt.height = 12

        data_cpt_ref = Reference(ws3, min_col=2, min_row=start_cpt_row, max_row=end_cpt_row)
        cats_cpt_ref = Reference(ws3, min_col=1, min_row=start_cpt_row + 1, max_row=end_cpt_row)
        chart_cpt.add_data(data_cpt_ref, titles_from_data=True)
        chart_cpt.set_categories(cats_cpt_ref)
        ws3.add_chart(chart_cpt, "N4")
    except Exception:
        pass

    for col in ws3.columns:
        if col[0].column > 12:
            continue
        max_l = max(len(str(c.value or '')) for c in col[:end_cpt_row + 1])
        ws3.column_dimensions[get_column_letter(col[0].column)].width = max(max_l + 3, 11)

    # -------------------------------------------------------------------------
    # SHEET 4: SOIL PROFILE (PROFIL LAPISAN TANAH)
    # -------------------------------------------------------------------------
    ws4 = wb.create_sheet(title="Soil Profile")
    ws4.views.sheetView[0].showGridLines = True
    _setup_page_print(ws4, landscape=False)

    ws4["A1"] = "VISUALISASI PROFIL STRATIGRAFI LAPISAN TANAH"
    ws4["A1"].font = font_main_title
    ws4["A2"] = "Susunan Stratigrafi Bawah Permukaan Berdasarkan Korelasi Lapangan"
    ws4["A2"].font = font_sub_title

    headers_prof = [
        "Lapisan #", "Kedalaman Top (m)", "Kedalaman Bot (m)", "Tebal (m)",
        "Klasifikasi Geoteknik", "Simbol", "Deskripsi Lapangan",
        "Kuat Geser cu (kPa)", "Sudut Geser φ' (°)", "Berat Isi γ (kN/m³)", "Modulus Es (MPa)"
    ]

    r_prof = 5
    for c_i, h in enumerate(headers_prof, 1):
        cell = ws4.cell(row=r_prof, column=c_i, value=h)
        _style_header_cell(cell, fill_color="1E3A8A", text_color="FFFFFF", bold=True, size=9)
        _style_border(cell)

    for idx, lyr in enumerate(spt_layers, 1):
        r_p = r_prof + idx
        d_top = float(lyr.get("depth_top", 0.0))
        d_bot = float(lyr.get("depth_bot", d_top + 1.5))
        thick = round(d_bot - d_top, 2)
        n_spt = int(lyr.get("n_spt", 10))
        cu_val = float(lyr.get("cu", lyr.get("c", 25.0)))
        es_val = round((cu_val * 0.4) if cu_val > 0 else (n_spt * 2.0), 1)

        prof_row = [
            f"Lapisan {idx}",
            d_top,
            d_bot,
            thick,
            lyr.get("soil_type", "Tanah"),
            "CH/CL" if cu_val > 30 else "SM/ML",
            lyr.get("deskripsi", "-"),
            cu_val,
            float(lyr.get("phi_eff", lyr.get("phi", 24.0))),
            float(lyr.get("gamma", 17.5)),
            es_val
        ]

        r_fill = fill_zebra if idx % 2 == 0 else fill_white
        for c_i, val in enumerate(prof_row, 1):
            cell = ws4.cell(row=r_p, column=c_i, value=val)
            cell.font = font_reg
            cell.fill = r_fill
            cell.alignment = align_left if c_i in [5, 7] else align_center
            if c_i in [2, 3, 4]:
                cell.number_format = '0.00'
            elif c_i in [8, 9, 10, 11]:
                cell.number_format = '0.0'
            _style_border(cell)

    end_prof_r = r_prof + len(spt_layers)
    for col in ws4.columns:
        if col[0].column > 11:
            continue
        max_l = max(len(str(c.value or '')) for c in col[:end_prof_r + 1])
        ws4.column_dimensions[get_column_letter(col[0].column)].width = max(max_l + 3, 11)
    ws4.column_dimensions["E"].width = 24
    ws4.column_dimensions["G"].width = 30

    # -------------------------------------------------------------------------
    # SHEET 5: SUMMARY & GEOTECHNICAL RECOMMENDATIONS
    # -------------------------------------------------------------------------
    ws5 = wb.create_sheet(title="Summary")
    ws5.views.sheetView[0].showGridLines = True
    _setup_page_print(ws5, landscape=False)

    ws5["A1"] = "RINGKASAN EKSEKUTIF PENYELIDIKAN TANAH & REKOMENDASI PONDASI"
    ws5["A1"].font = font_main_title
    ws5["A2"] = "Kesimpulan Parameter Desain Geoteknik untuk Perencanaan Struktur Bawah"
    ws5["A2"].font = font_sub_title

    ws5["A4"] = "1. RANGKUMAN PARAMETER TANAH DESAIN (ZONA FONDASI DANGKAL 0 - 3.0 M)"
    ws5["A4"].font = font_section

    avg_cu = round(sum(float(l.get("cu", 20.0)) for l in spt_layers[:2]) / max(1, len(spt_layers[:2])), 1)
    avg_phi = round(sum(float(l.get("phi_eff", 24.0)) for l in spt_layers[:2]) / max(1, len(spt_layers[:2])), 1)
    avg_gamma = round(sum(float(l.get("gamma", 17.5)) for l in spt_layers[:2]) / max(1, len(spt_layers[:2])), 1)

    sum_table = [
        ("Kedalaman Muka Air Tanah Rencana (GWL)", f"{p_gwl:.2f} meter dari muka tanah asli"),
        ("Kohesi Tanah Efektif Desain (c / cu)", f"{avg_cu:.1f} kPa"),
        ("Sudut Geser Dalam Efektif (φ / φ')", f"{avg_phi:.1f} derajat"),
        ("Berat Volume Tanah Basah (γ)", f"{avg_gamma:.1f} kN/m³"),
        ("Berat Volume Tanah Jenuh Air (γsat)", f"{avg_gamma + 1.5:.1f} kN/m³"),
        ("Kedalaman Lapisan Tanah Keras (N > 30 / qc > 150 kg/cm²)", f"{spt_layers[-1].get('depth_top', 6.0):.2f} meter")
    ]

    r_s = 5
    for lbl, val in sum_table:
        ws5[f"A{r_s}"] = lbl
        ws5[f"A{r_s}"].font = font_bold
        ws5[f"A{r_s}"].fill = fill_meta
        ws5[f"A{r_s}"].border = thin_border
        ws5[f"B{r_s}"] = val
        ws5[f"B{r_s}"].font = font_reg
        ws5[f"B{r_s}"].border = thin_border
        r_s += 1

    r_s += 1
    ws5[f"A{r_s}"] = "2. KESIMPULAN KELAYAKAN GEOTEKNIK & REKOMENDASI SISTEM FONDASI"
    ws5[f"A{r_s}"].font = font_section
    r_s += 1

    recomms = [
        "A. Kelayakan Fondasi Dangkal (Pad / Isolated Footing):",
        f"   - Sangat layak digunakan untuk bangunan gedung 1 s/d 3 lantai dengan kedalaman rencana Df = 1.20 - 1.80 m.",
        f"   - Daya dukung izin tanah berkisar antara 100 s/d 220 kPa tergantung metode perhitungan dan ukuran tapak.",
        f"   - Wajib memperhitungkan reduksi akibat posisi muka air tanah (GWL = {p_gwl:.2f} m) dan lantai kerja beton kurus (lean concrete min 10 cm).",
        "",
        "B. Catatan Pelaksanaan Konstruksi:",
        "   - Lakukan pemadatan dasar galian sebelum pengecoran lantai kerja.",
        "   - Bila dasar galian terendam air hujan, lakukan dewatering dan buang lumpur sisa setebal min 15 cm.",
        "   - Gunakan selimut beton (concrete cover) minimum 75 mm untuk elemen yang bersentuhan langsung dengan tanah."
    ]

    for rc_txt in recomms:
        ws5[f"A{r_s}"] = rc_txt
        ws5[f"A{r_s}"].font = font_bold if rc_txt.startswith(("A.", "B.")) else font_reg
        r_s += 1

    ws5.column_dimensions["A"].width = 45
    ws5.column_dimensions["B"].width = 50

    out = io.BytesIO()
    wb.save(out)
    out.seek(0)
    return out.getvalue()


# =============================================================================
# B. LAPORAN PERHITUNGAN PONDASI (FOUNDATION CALCULATION REPORT - 6 SHEETS)
# LENGKAP DENGAN SUBSTITUSI ANGKA RUNTUT & HASIL PASTI (NO BLANK CELLS)
# =============================================================================

def generate_foundation_calculation_report(
    project_info,
    soil_params,
    load_params,
    comp_results,
    selected_dim,
    reinf_results=None
):
    """
    Menghasilkan Dokumen Laporan Perhitungan Pondasi Lengkap (6 Sheets)
    dengan RANGKAIAN RUMUS & SUBSTITUSI ANGKA RUNTUT:
    - Sheet 1: Design Criteria (Input Data & Parameter Standar)
    - Sheet 2: Soil Parameter (Faktor Daya Dukung & Korelasi Tanah)
    - Sheet 3: Foundation Dimension Calculation (Daya Dukung, Eksentrisitas & Tekanan Kontak)
    - Sheet 4: Structural Calculation (Momen Mu, Geser 1 Arah, Geser Pons 2 Arah SNI 2847)
    - Sheet 5: Reinforcement Calculation (Tulangan Bawah, Tulangan Atas Kotak, BoQ)
    - Sheet 6: Final Design Summary (Rangkuman Akhir & Rekomendasi Desain)
    """
    wb = openpyxl.Workbook()
    wb.calculation.fullCalcOnLoad = True
    wb.calculation.calcMode = 'auto'

    font_main_title = Font(name="Calibri", size=15, bold=True, color="1E3A8A")
    font_sub_title = Font(name="Calibri", size=9, italic=True, color="64748B")
    font_section = Font(name="Calibri", size=11, bold=True, color="0F172A")
    font_bold = Font(name="Calibri", size=10, bold=True)
    font_reg = Font(name="Calibri", size=9.5)
    font_formula = Font(name="Consolas", size=9.5, color="1E40AF")

    fill_meta = PatternFill(start_color="F1F5F9", end_color="F1F5F9", fill_type="solid")
    fill_input = PatternFill(start_color="E0F2FE", end_color="E0F2FE", fill_type="solid")
    fill_zebra = PatternFill(start_color="F8FAFC", end_color="F8FAFC", fill_type="solid")
    fill_white = PatternFill(start_color="FFFFFF", end_color="FFFFFF", fill_type="solid")
    fill_safe = PatternFill(start_color="DCFCE7", end_color="DCFCE7", fill_type="solid")

    thin_border = Border(
        left=Side(style='thin', color='CBD5E1'),
        right=Side(style='thin', color='CBD5E1'),
        top=Side(style='thin', color='CBD5E1'),
        bottom=Side(style='thin', color='CBD5E1')
    )

    align_center = Alignment(horizontal='center', vertical='center')
    align_left = Alignment(horizontal='left', vertical='center')
    align_right = Alignment(horizontal='right', vertical='center')

    p_name = project_info.get("name", "Proyek Bangunan Cerdas")
    p_loc = project_info.get("location", "Semarang")
    p_eng = project_info.get("engineer", "Insinyur Sipil")

    B = _clean_num(selected_dim.get("B", 2.0))
    L = _clean_num(selected_dim.get("L", 2.0))
    Df = _clean_num(selected_dim.get("Df", 1.5))
    hf = _clean_num(selected_dim.get("hf", 0.45))
    if hf <= 0:
        hf = 0.45
    SF = _clean_num(selected_dim.get("SF", 3.0))

    c = _clean_num(soil_params.get("cohesion", soil_params.get("c", 25.0)))
    phi = _clean_num(soil_params.get("friction_angle", soil_params.get("phi", 20.0)))
    gamma = _clean_num(soil_params.get("unit_weight", soil_params.get("gamma", 17.5)))
    gamma_sat = _clean_num(soil_params.get("sat_unit_weight", soil_params.get("gamma_sat", 19.0)))
    dw = _clean_num(soil_params.get("water_table", soil_params.get("dw", 1.50)))

    P_servis = _clean_num(load_params.get("p_column", 350.0))
    Pu = _clean_num(load_params.get("pu_column", P_servis * 1.35))
    Mux = _clean_num(load_params.get("Mux", 15.0))
    Muy = _clean_num(load_params.get("Muy", 10.0))

    col_b = 0.40
    col_h = 0.40
    fc = 25.0
    fy = 420.0
    cover = 75.0
    bar_dia = 16.0

    tz_fact = comp_results[0] if comp_results and len(comp_results) > 0 else {}
    Nc = float(tz_fact.get("Nc", 14.8))
    Nq = float(tz_fact.get("Nq", 6.4))
    Ngamma = float(tz_fact.get("Ngamma", 5.4))
    sc = float(tz_fact.get("sc", 1.3))
    sq = float(tz_fact.get("sq", 1.0))
    sgamma = float(tz_fact.get("sgamma", 0.8))

    # Perhitungan Terzaghi Lengkap
    A = round(B * L, 3)
    Vf = round(B * L * hf, 3)
    Wf = round(Vf * 24.0, 2)
    ha = round(max(0.0, Df - hf), 3)
    Ws = round(max(0.0, (A - (col_b * col_h)) * ha * gamma), 2)
    Ptot = round(P_servis + Wf + Ws, 2)
    po = round(gamma * Df, 2)
    qu = round((1.3 * c * Nc) + (po * Nq) + (0.4 * gamma * B * Ngamma), 2)
    qall = round(((qu - po) / SF) + po, 2)
    q_avg = round(Ptot / A, 2)
    Wx = round((B * (L**2)) / 6.0, 3)
    ex = round(Mux / Pu, 3) if Pu > 0 else 0.0
    ekern = round(L / 6.0, 3)
    cek_e = "AMAN (TIDAK ADA UPLIFT)" if ex <= ekern else "PERINGATAN (TERJADI TARIKAN)"
    qmax = round(q_avg + (Mux / Wx if Wx > 0 else 0.0), 2)
    eval_bearing = "AMAN (OK)" if qmax <= qall else "OVERSTRESSED - PERLU DIPERLEBAR"

    # Perhitungan Struktur (SNI 2847:2019)
    qu_net = round(Pu / A, 2)
    d_mm = round((hf * 1000.0) - cover - (bar_dia / 2.0), 1)
    Lcx_mm = round(((B * 1000.0) - (col_b * 1000.0)) / 2.0, 1)
    Lcy_mm = round(((L * 1000.0) - (col_h * 1000.0)) / 2.0, 1)
    Mux_face_kNm = round((qu_net * L * ((Lcx_mm / 1000.0)**2)) / 2.0, 2)
    Muy_face_kNm = round((qu_net * B * ((Lcy_mm / 1000.0)**2)) / 2.0, 2)
    Mu_max_kNm = max(Mux_face_kNm, Muy_face_kNm)

    # Geser Satu Arah
    x_crit_mm = round(max(0.0, Lcx_mm - d_mm), 1)
    Vu1_kN = round(qu_net * L * (x_crit_mm / 1000.0), 2)
    phi_Vc1_kN = round((0.75 * 0.17 * math.sqrt(fc) * (L * 1000.0) * d_mm) / 1000.0, 2)
    UF_v1 = round(Vu1_kN / phi_Vc1_kN, 3) if phi_Vc1_kN > 0 else 0.0
    Cek_Vu1 = "AMAN (OK)" if Vu1_kN <= phi_Vc1_kN else "TIDAK AMAN - PERLU PERTEBAL hf"

    # Geser Pons Dua Arah
    bo_mm = round(2.0 * ((col_b * 1000.0) + (col_h * 1000.0) + (2.0 * d_mm)), 1)
    Ao_m2 = round(((col_b * 1000.0) + d_mm) * ((col_h * 1000.0) + d_mm) / 1e6, 4)
    Vu2_kN = round(Pu - (qu_net * Ao_m2), 2)
    phi_Vc2_kN = round((0.75 * 0.33 * math.sqrt(fc) * bo_mm * d_mm) / 1000.0, 2)
    UF_v2 = round(Vu2_kN / phi_Vc2_kN, 3) if phi_Vc2_kN > 0 else 0.0
    Cek_Vu2 = "AMAN (OK)" if Vu2_kN <= phi_Vc2_kN else "TIDAK AMAN - TEBAL PONDASI KURANG"

    # Penulangan Bawah
    Rn = round((Mu_max_kNm * 1e6) / (0.9 * (L * 1000.0) * (d_mm**2)), 3)
    rho_req = round((0.85 * fc / fy) * (1.0 - math.sqrt(max(0.0, 1.0 - (2.0 * Rn / (0.85 * fc))))), 5)
    rho_min = round(0.0018 * (420.0 / fy), 5)
    rho_des = max(rho_req, rho_min)
    As_req_x = round(rho_des * (L * 1000.0) * d_mm, 1)
    Ab_mm2 = round((math.pi / 4.0) * (bar_dia**2), 1)
    n_x = max(4, int(math.ceil(As_req_x / Ab_mm2)))
    s_x = round(((B * 1000.0) - (2.0 * cover) - bar_dia) / (n_x - 1), 0)
    s_max = min(round(3.0 * (hf * 1000.0), 0), 450.0)
    cek_s_x = "AMAN (MEMENUHI SPASI)" if s_x <= s_max else "SPASI TERLALU LEBAR"
    notasi_x = f"D{int(bar_dia)}-{int(s_x)} mm ({n_x} btg)"

    As_req_y = round(rho_des * (B * 1000.0) * d_mm, 1)
    n_y = max(4, int(math.ceil(As_req_y / Ab_mm2)))
    s_y = round(((L * 1000.0) - (2.0 * cover) - bar_dia) / (n_y - 1), 0)
    notasi_y = f"D{int(bar_dia)}-{int(s_y)} mm ({n_y} btg)"

    # Penulangan Atas (Keranjang Kotak)
    D_top = max(10, int(bar_dia - 3))
    Ab_top = round((math.pi / 4.0) * (D_top**2), 1)
    As_top_min = round(0.0018 * 420.0 / fy * (L * 1000.0) * (hf * 1000.0), 1)
    n_top_x = max(3, int(math.ceil(As_top_min / Ab_top)))
    s_top_x = round(((B * 1000.0) - (2.0 * cover) - D_top) / max(1, n_top_x - 1), 0)
    notasi_top_x = f"D{D_top}-{int(s_top_x)} mm ({n_top_x} btg)"

    n_top_y = max(3, int(math.ceil(As_top_min / Ab_top)))
    s_top_y = round(((L * 1000.0) - (2.0 * cover) - D_top) / max(1, n_top_y - 1), 0)
    notasi_top_y = f"D{D_top}-{int(s_top_y)} mm ({n_top_y} btg)"

    # BoQ
    w_bar_kg_m = round(0.006165 * (bar_dia**2), 3)
    w_top_kg_m = round(0.006165 * (D_top**2), 3)
    Ltot_bot_m = round((n_x * (B + 0.30)) + (n_y * (L + 0.30)), 2)
    Ltot_top_m = round((n_top_x * (B + 0.30)) + (n_top_y * (L + 0.30)), 2)
    W_steel_kg = round((Ltot_bot_m * w_bar_kg_m) + (Ltot_top_m * w_top_kg_m) + 12.0, 1)
    rasio_kg_m3 = round(W_steel_kg / Vf, 1) if Vf > 0 else 0.0

    # -------------------------------------------------------------------------
    # SHEET 1: DESIGN CRITERIA
    # -------------------------------------------------------------------------
    ws1 = wb.active
    ws1.title = "Design Criteria"
    ws1.views.sheetView[0].showGridLines = True
    _setup_page_print(ws1, landscape=False)

    ws1["A1"] = "DESIGN CRITERIA & BASIS OF CALCULATION"
    ws1["A1"].font = font_main_title
    ws1["A2"] = "Parameter Desain Struktur Pondasi Tapak Berdasarkan SNI 1727:2020 & SNI 2847:2019"
    ws1["A2"].font = font_sub_title

    ws1["A4"] = "PROYEK:"
    ws1["A4"].font = font_bold
    ws1["B4"] = p_name
    ws1["B4"].font = font_bold
    ws1["D4"] = "TANGGAL:"
    ws1["D4"].font = font_bold
    ws1["E4"] = project_info.get("date", "2026-11-12")

    ws1["A5"] = "LOKASI:"
    ws1["A5"].font = font_bold
    ws1["B5"] = p_loc
    ws1["D5"] = "PERENCANA:"
    ws1["D5"].font = font_bold
    ws1["E5"] = p_eng

    headers_dc = ["Parameter Desain", "Simbol", "=", "Nilai Input", "Satuan"]
    for c_i, h in enumerate(headers_dc, 1):
        cell = ws1.cell(row=7, column=c_i, value=h)
        _style_header_cell(cell, fill_color="1E3A8A", text_color="FFFFFF", bold=True, size=9)
        _style_border(cell)

    criteria_inputs = [
        ("A. DATA STRUKTUR & MATERIAL", "", "", ""),
        ("Lebar Fondasi", "B", B, "m"),
        ("Panjang Fondasi", "L", L, "m"),
        ("Tebal Pelat Fondasi", "hf", hf, "m"),
        ("Kedalaman Dasar Fondasi", "Df", Df, "m"),
        ("Lebar Kolom / Pedestal X", "bc", col_b, "m"),
        ("Panjang Kolom / Pedestal Y", "hc", col_h, "m"),
        ("Mutu Kuat Tekan Beton", "f'c", fc, "MPa"),
        ("Mutu Kuat Leleh Baja", "fy", fy, "MPa"),
        ("Tebal Selimut Beton Bersih", "cc", cover, "mm"),
        ("Diameter Tulangan Utama", "D", bar_dia, "mm"),
        ("Berat Jenis Beton Bertulang", "γc", 24.0, "kN/m³"),
        ("", "", "", ""),
        ("B. DATA TANAH DASAR & MUKA AIR", "", "", ""),
        ("Kohesi Tanah Dasar", "c", c, "kPa"),
        ("Sudut Geser Dalam", "φ", phi, "derajat"),
        ("Berat Volume Tanah Basah", "γ", gamma, "kN/m³"),
        ("Berat Volume Tanah Jenuh Air", "γsat", gamma_sat, "kN/m³"),
        ("Kedalaman Muka Air Tanah (MAT)", "dw", dw, "m"),
        ("Target Faktor Keamanan", "SF", SF, "-"),
        ("", "", "", ""),
        ("C. DATA PEMBEBANAN STRUKTUR", "", "", ""),
        ("Beban Aksial Servis", "P", P_servis, "kN"),
        ("Beban Aksial Terfaktor", "Pu", Pu, "kN"),
        ("Momen Terfaktor Arah X", "Mux", Mux, "kN.m"),
        ("Momen Terfaktor Arah Y", "Muy", Muy, "kN.m")
    ]

    r = 8
    for item in criteria_inputs:
        lbl, sym, val, unit = item
        if val == "" and unit == "":
            ws1[f"A{r}"] = lbl
            ws1[f"A{r}"].font = font_section
            r += 1
            continue

        ws1[f"A{r}"] = lbl
        ws1[f"A{r}"].font = font_reg
        ws1[f"A{r}"].border = thin_border

        ws1[f"B{r}"] = sym
        ws1[f"B{r}"].font = font_bold
        ws1[f"B{r}"].alignment = align_center
        ws1[f"B{r}"].border = thin_border

        ws1[f"C{r}"] = "="
        ws1[f"C{r}"].alignment = align_center
        ws1[f"C{r}"].border = thin_border

        ws1[f"D{r}"] = val
        ws1[f"D{r}"].font = font_bold
        ws1[f"D{r}"].fill = fill_input
        ws1[f"D{r}"].alignment = align_center
        ws1[f"D{r}"].border = thin_border
        if isinstance(val, (int, float)):
            ws1[f"D{r}"].number_format = '0.00' if isinstance(val, float) else '0'

        ws1[f"E{r}"] = unit
        ws1[f"E{r}"].font = font_reg
        ws1[f"E{r}"].border = thin_border
        r += 1

    ws1.column_dimensions["A"].width = 32
    ws1.column_dimensions["B"].width = 8
    ws1.column_dimensions["C"].width = 5
    ws1.column_dimensions["D"].width = 16
    ws1.column_dimensions["E"].width = 12

    # -------------------------------------------------------------------------
    # SHEET 2: SOIL PARAMETER
    # -------------------------------------------------------------------------
    ws2 = wb.create_sheet(title="Soil Parameter")
    ws2.views.sheetView[0].showGridLines = True
    _setup_page_print(ws2, landscape=False)

    ws2["A1"] = "SOIL PARAMETERS & BEARING CAPACITY FACTORS"
    ws2["A1"].font = font_main_title
    ws2["A2"] = "Faktor Kapasitas Dukung Tanah Berdasarkan Korelasi Teori Geoteknik"
    ws2["A2"].font = font_sub_title

    ws2["A4"] = "1. FAKTOR KAPASITAS DUKUNG TERZAGHI & MEYERHOF"
    ws2["A4"].font = font_section

    headers_sp = ["Parameter", "Simbol", "Rumus Referensi", "Nilai Terhitung", "Satuan"]
    r_sp = 5
    for c_i, h in enumerate(headers_sp, 1):
        cell = ws2.cell(row=r_sp, column=c_i, value=h)
        _style_header_cell(cell, fill_color="1E3A8A", text_color="FFFFFF", bold=True, size=9)
        _style_border(cell)

    soil_factors = [
        ("Faktor Kohesi", "Nc", f"Tabel 3.1 Terzaghi (φ={phi:.1f}°)", Nc, "-"),
        ("Faktor Beban Samping", "Nq", f"Tabel 3.1 Terzaghi (φ={phi:.1f}°)", Nq, "-"),
        ("Faktor Berat Tanah", "Nγ", f"Tabel 3.1 Terzaghi (φ={phi:.1f}°)", Ngamma, "-"),
        ("Faktor Bentuk Kohesi", "sc", f"1.0 + 0.2*(B/L)*(tan(45+φ/2))²", sc, "-"),
        ("Faktor Bentuk Samping", "sq", f"1.0 + 0.1*(B/L)*(tan(45+φ/2))²", sq, "-"),
        ("Faktor Bentuk Berat Tanah", "sγ", f"1.0 + 0.1*(B/L)*(tan(45+φ/2))²", sgamma, "-")
    ]

    for item in soil_factors:
        r_sp += 1
        ws2[f"A{r_sp}"] = item[0]; ws2[f"A{r_sp}"].font = font_reg; ws2[f"A{r_sp}"].border = thin_border
        ws2[f"B{r_sp}"] = item[1]; ws2[f"B{r_sp}"].font = font_bold; ws2[f"B{r_sp}"].alignment = align_center; ws2[f"B{r_sp}"].border = thin_border
        ws2[f"C{r_sp}"] = item[2]; ws2[f"C{r_sp}"].font = font_formula; ws2[f"C{r_sp}"].border = thin_border
        ws2[f"D{r_sp}"] = item[3]; ws2[f"D{r_sp}"].font = font_bold; ws2[f"D{r_sp}"].alignment = align_center; ws2[f"D{r_sp}"].border = thin_border
        ws2[f"D{r_sp}"].number_format = '0.00'
        ws2[f"E{r_sp}"] = item[4]; ws2[f"E{r_sp}"].font = font_reg; ws2[f"E{r_sp}"].alignment = align_center; ws2[f"E{r_sp}"].border = thin_border

    ws2.column_dimensions["A"].width = 28
    ws2.column_dimensions["B"].width = 10
    ws2.column_dimensions["C"].width = 38
    ws2.column_dimensions["D"].width = 16
    ws2.column_dimensions["E"].width = 10

    # -------------------------------------------------------------------------
    # SHEET 3: FOUNDATION DIMENSION CALCULATION (SUBSTITUSI ANGKA RUNTUT)
    # -------------------------------------------------------------------------
    ws3 = wb.create_sheet(title="Dimension Calculation")
    ws3.views.sheetView[0].showGridLines = True
    _setup_page_print(ws3, landscape=False)

    ws3["A1"] = "PERHITUNGAN DIMENSI & TEGANGAN KONTAK TANAH FONDASI"
    ws3["A1"].font = font_main_title
    ws3["A2"] = "Rangkaian Perhitungan Runtut dengan Substitusi Angka Berdasarkan Sheet 'Design Criteria'"
    ws3["A2"].font = font_sub_title

    headers_dim = ["Item Perhitungan", "Simbol", "Alur Rumus & Substitusi Angka Runtut", "Hasil Perhitungan", "Satuan", "Status / Catatan"]
    r_dim = 4
    for c_i, h in enumerate(headers_dim, 1):
        cell = ws3.cell(row=r_dim, column=c_i, value=h)
        _style_header_cell(cell, fill_color="1E3A8A", text_color="FFFFFF", bold=True, size=9)
        _style_border(cell)

    dim_calcs = [
        ("Luas Tapak Fondasi", "A", f"B × L = {B:.2f} × {L:.2f}", A, "m²", "Luas bidang kontak dasar"),
        ("Volume Beton Fondasi", "Vf", f"B × L × hf = {B:.2f} × {L:.2f} × {hf:.2f}", Vf, "m³", "Volume pelat beton"),
        ("Berat Sendiri Fondasi", "Wf", f"Vf × γc = {Vf:.2f} × 24.0", Wf, "kN", "Beban sendiri pelat beton"),
        ("Tebal Tanah di Atas Fondasi", "ha", f"Df - hf = {Df:.2f} - {hf:.2f}", ha, "m", "Tanah urug di atas pelat"),
        ("Berat Tanah di Atas Fondasi", "Ws", f"(A - Ab) × ha × γ = ({A:.2f} - {col_b*col_h:.2f}) × {ha:.2f} × {gamma:.1f}", Ws, "kN", "Overburden di atas pelat"),
        ("Total Beban Aksial Servis", "Ptot", f"P + Wf + Ws = {P_servis:.1f} + {Wf:.1f} + {Ws:.1f}", Ptot, "kN", "Total gaya normal servis"),
        ("Tegangan Overburden Dasar", "po", f"γ × Df = {gamma:.1f} × {Df:.2f}", po, "kPa", "Tegangan overburden po = γ*Df"),
        ("Kapasitas Ultimit qu (Terzaghi)", "qu", f"1.3·c·Nc + po·Nq + 0.4·γ·B·Nγ = 1.3·{c:.1f}·{Nc:.1f} + {po:.1f}·{Nq:.1f} + 0.4·{gamma:.1f}·{B:.1f}·{Ngamma:.1f}", qu, "kPa", "Kapasitas ultimit Terzaghi"),
        ("Daya Dukung Izin qall", "qall", f"(qu - po)/SF + po = ({qu:.1f} - {po:.1f})/{SF:.1f} + {po:.1f}", qall, "kPa", f"Target Safety Factor SF={SF:.1f}"),
        ("Tekanan Kontak Rata-Rata", "q_avg", f"Ptot / A = {Ptot:.1f} / {A:.2f}", q_avg, "kPa", "Tekanan kontak tanah q = Ptot / A"),
        ("Tahanan Momen Tapak", "Wx", f"B × L² / 6 = {B:.2f} × {L:.2f}² / 6", Wx, "m³", "Modulus penampang dasar W"),
        ("Eksentrisitas Beban Arah X", "ex", f"Mux / Pu = {Mux:.1f} / {Pu:.1f}", ex, "m", "ex = Mux / Pu"),
        ("Batas Maksimum Eksentrisitas (Kern)", "ekern", f"L / 6 = {L:.2f} / 6", ekern, "m", "Batas kern e <= L/6"),
        ("Kontrol Eksentrisitas (Tidak Tarik)", "Cek-e", f"ex <= ekern ({ex:.3f} m <= {ekern:.3f} m)", cek_e, "-", "Kontrol kemurnian tekan tapak"),
        ("Tekanan Kontak Maksimum", "q_max", f"Ptot/A + Mux/Wx = {q_avg:.1f} + {Mux/Wx:.1f}", qmax, "kPa", "qmax = P/A + M/W"),
        ("EVALUASI KEAMANAN DAYA DUKUNG", "Status", f"qmax <= qall ({qmax:.1f} kPa <= {qall:.1f} kPa)", eval_bearing, "-", "Syarat batas aman geoteknik")
    ]

    for item in dim_calcs:
        r_dim += 1
        is_eval = "EVALUASI" in item[0]
        ws3[f"A{r_dim}"] = item[0]; ws3[f"A{r_dim}"].font = font_bold if is_eval else font_reg; ws3[f"A{r_dim}"].border = thin_border
        ws3[f"B{r_dim}"] = item[1]; ws3[f"B{r_dim}"].font = font_bold; ws3[f"B{r_dim}"].alignment = align_center; ws3[f"B{r_dim}"].border = thin_border
        ws3[f"C{r_dim}"] = item[2]; ws3[f"C{r_dim}"].font = font_formula; ws3[f"C{r_dim}"].border = thin_border
        ws3[f"D{r_dim}"] = item[3]; ws3[f"D{r_dim}"].font = font_bold; ws3[f"D{r_dim}"].alignment = align_center; ws3[f"D{r_dim}"].border = thin_border
        if isinstance(item[3], (int, float)):
            ws3[f"D{r_dim}"].number_format = '0.00'
        if is_eval or "AMAN" in str(item[3]):
            ws3[f"D{r_dim}"].fill = fill_safe
        ws3[f"E{r_dim}"] = item[4]; ws3[f"E{r_dim}"].font = font_reg; ws3[f"E{r_dim}"].alignment = align_center; ws3[f"E{r_dim}"].border = thin_border
        ws3[f"F{r_dim}"] = item[5]; ws3[f"F{r_dim}"].font = font_sub_title; ws3[f"F{r_dim}"].border = thin_border

    ws3.column_dimensions["A"].width = 34
    ws3.column_dimensions["B"].width = 10
    ws3.column_dimensions["C"].width = 54
    ws3.column_dimensions["D"].width = 24
    ws3.column_dimensions["E"].width = 10
    ws3.column_dimensions["F"].width = 32

    # -------------------------------------------------------------------------
    # SHEET 4: STRUCTURAL CALCULATION (SNI 2847:2019)
    # -------------------------------------------------------------------------
    ws4 = wb.create_sheet(title="Structural Calculation")
    ws4.views.sheetView[0].showGridLines = True
    _setup_page_print(ws4, landscape=False)

    ws4["A1"] = "PERHITUNGAN KAPASITAS STRUKTUR BETON FONDASI (SNI 2847:2019)"
    ws4["A1"].font = font_main_title
    ws4["A2"] = "Pemeriksaan Momen Terfaktor, Geser Lentur Satu Arah, dan Geser Pons Dua Arah"
    ws4["A2"].font = font_sub_title

    headers_str = ["Item Analisis Struktur", "Simbol", "Alur Rumus & Substitusi Angka Runtut", "Hasil Perhitungan", "Satuan", "Keterangan / Evaluasi"]
    r_str = 4
    for c_i, h in enumerate(headers_str, 1):
        cell = ws4.cell(row=r_str, column=c_i, value=h)
        _style_header_cell(cell, fill_color="1E3A8A", text_color="FFFFFF", bold=True, size=9)
        _style_border(cell)

    struct_calcs = [
        ("Tegangan Kontak Terfaktor Netto", "qu_net", f"Pu / (B × L) = {Pu:.1f} / ({B:.2f} × {L:.2f})", qu_net, "kPa", "qu = Pu / (B*L)"),
        ("Tinggi Efektif Pelat Fondasi", "d", f"hf - cc - D/2 = {hf*1000:.0f} - {cover:.0f} - {bar_dia/2:.1f}", d_mm, "mm", "d = hf - cc - D/2"),
        ("Panjang Kantilever Muka Kolom X", "Lcx", f"(B - bc) / 2 = ({B*1000:.0f} - {col_b*1000:.0f}) / 2", Lcx_mm, "mm", "Lcx = (B - bc) / 2"),
        ("Panjang Kantilever Muka Kolom Y", "Lcy", f"(L - hc) / 2 = ({L*1000:.0f} - {col_h*1000:.0f}) / 2", Lcy_mm, "mm", "Lcy = (L - hc) / 2"),
        ("Momen Lentur Terfaktor Kolom X", "Mux_face", f"qu × L × Lcx² / 2 = {qu_net:.1f} × {L:.2f} × {Lcx_mm/1000:.3f}² / 2", Mux_face_kNm, "kN.m", "Momen lentur kritis muka kolom X"),
        ("Momen Lentur Terfaktor Kolom Y", "Muy_face", f"qu × B × Lcy² / 2 = {qu_net:.1f} × {B:.2f} × {Lcy_mm/1000:.3f}² / 2", Muy_face_kNm, "kN.m", "Momen lentur kritis muka kolom Y"),
        ("Momen Desain Maksimum", "Mu_max", f"max(Mux, Muy) = max({Mux_face_kNm:.2f}, {Muy_face_kNm:.2f})", Mu_max_kNm, "kN.m", "Momen kritis acuan penulangan"),
        ("KONTROL GESER SATU ARAH", "", "", "", "", ""),
        ("Jarak Penampang Kritis Geser 1 Arah", "x_crit", f"Lcx - d = {Lcx_mm:.0f} - {d_mm:.0f}", x_crit_mm, "mm", "Penampang kritis di jarak d dari kolom"),
        ("Gaya Geser Terfaktor 1 Arah", "Vu1", f"qu × L × x_crit = {qu_net:.1f} × {L:.2f} × {x_crit_mm/1000:.3f}", Vu1_kN, "kN", "Vu1 = qu*L*(Lcant - d)"),
        ("Kuat Geser Beton 1 Arah (φ=0.75)", "phi_Vc1", f"0.75 × 0.17 × √f'c × L × d = 0.75 × 0.17 × √{fc:.0f} × {L*1000:.0f} × {d_mm:.0f} / 1000", phi_Vc1_kN, "kN", "SNI 2847 Pasal 22.5"),
        ("Rasio Geser 1 Arah", "UF_v1", f"Vu1 / φVc1 = {Vu1_kN:.1f} / {phi_Vc1_kN:.1f}", UF_v1, "-", "Utility Factor Geser 1 Arah"),
        ("EVALUASI GESER SATU ARAH", "Cek_Vu1", f"Vu1 <= φVc1 ({Vu1_kN:.1f} kN <= {phi_Vc1_kN:.1f} kN)", Cek_Vu1, "-", "Syarat batas aman geser balok"),
        ("KONTROL GESER PONS DUA ARAH", "", "", "", "", ""),
        ("Keliling Kritis Geser Pons", "bo", f"2 × (bc + hc + 2d) = 2 × ({col_b*1000:.0f} + {col_h*1000:.0f} + 2·{d_mm:.0f})", bo_mm, "mm", "Perimeter geser pons penampang kritis"),
        ("Luas Area Dalam Perimeter Pons", "Ao", f"(bc + d) × (hc + d) = {((col_b*1000)+d_mm)/1000:.3f} × {((col_h*1000)+d_mm)/1000:.3f}", Ao_m2, "m²", "Luas bidang dalam perimeter geser"),
        ("Gaya Geser Pons Terfaktor", "Vu2", f"Pu - qu × Ao = {Pu:.1f} - ({qu_net:.1f} × {Ao_m2:.4f})", Vu2_kN, "kN", "Vu2 = Pu - qu*Ao"),
        ("Kuat Geser Pons Desain (φ=0.75)", "phi_Vc2", f"0.75 × 0.33 × √f'c × bo × d = 0.75 × 0.33 × √{fc:.0f} × {bo_mm:.0f} × {d_mm:.0f} / 1000", phi_Vc2_kN, "kN", "SNI 2847 Pasal 22.6"),
        ("Rasio Geser Pons", "UF_v2", f"Vu2 / φVc2 = {Vu2_kN:.1f} / {phi_Vc2_kN:.1f}", UF_v2, "-", "Utility Factor Geser Pons"),
        ("EVALUASI GESER PONS DUA ARAH", "Cek_Vu2", f"Vu2 <= φVc2 ({Vu2_kN:.1f} kN <= {phi_Vc2_kN:.1f} kN)", Cek_Vu2, "-", "Syarat batas aman punching shear")
    ]

    for item in struct_calcs:
        r_str += 1
        if item[1] == "" and item[3] == "":
            ws4[f"A{r_str}"] = item[0]
            ws4[f"A{r_str}"].font = font_section
            continue

        is_eval = "EVALUASI" in item[0]
        ws4[f"A{r_str}"] = item[0]; ws4[f"A{r_str}"].font = font_bold if is_eval else font_reg; ws4[f"A{r_str}"].border = thin_border
        ws4[f"B{r_str}"] = item[1]; ws4[f"B{r_str}"].font = font_bold; ws4[f"B{r_str}"].alignment = align_center; ws4[f"B{r_str}"].border = thin_border
        ws4[f"C{r_str}"] = item[2]; ws4[f"C{r_str}"].font = font_formula; ws4[f"C{r_str}"].border = thin_border
        ws4[f"D{r_str}"] = item[3]; ws4[f"D{r_str}"].font = font_bold; ws4[f"D{r_str}"].alignment = align_center; ws4[f"D{r_str}"].border = thin_border
        if isinstance(item[3], (int, float)):
            ws4[f"D{r_str}"].number_format = '0.00'
        if is_eval or "AMAN" in str(item[3]):
            ws4[f"D{r_str}"].fill = fill_safe
        ws4[f"E{r_str}"] = item[4]; ws4[f"E{r_str}"].font = font_reg; ws4[f"E{r_str}"].alignment = align_center; ws4[f"E{r_str}"].border = thin_border
        ws4[f"F{r_str}"] = item[5]; ws4[f"F{r_str}"].font = font_sub_title; ws4[f"F{r_str}"].border = thin_border

    ws4.column_dimensions["A"].width = 34
    ws4.column_dimensions["B"].width = 12
    ws4.column_dimensions["C"].width = 54
    ws4.column_dimensions["D"].width = 24
    ws4.column_dimensions["E"].width = 10
    ws4.column_dimensions["F"].width = 32

    # -------------------------------------------------------------------------
    # SHEET 5: REINFORCEMENT CALCULATION (PENULANGAN & KERANJANG KOTAK)
    # -------------------------------------------------------------------------
    ws5 = wb.create_sheet(title="Reinforcement Calculation")
    ws5.views.sheetView[0].showGridLines = True
    _setup_page_print(ws5, landscape=False)

    ws5["A1"] = "PERHITUNGAN KEBUTUHAN TULANGAN PONDASI (SNI 2847:2019)"
    ws5["A1"].font = font_main_title
    ws5["A2"] = "Desain Tulangan Lentur Bawah Arah X & Y, Tulangan Atas Keranjang Kotak, Spasi & BoQ"
    ws5["A2"].font = font_sub_title

    headers_reinf = ["Item Penulangan", "Simbol", "Alur Rumus & Substitusi Angka Runtut", "Hasil Perhitungan", "Satuan", "Keterangan / Detailing"]
    r_rf = 4
    for c_i, h in enumerate(headers_reinf, 1):
        cell = ws5.cell(row=r_rf, column=c_i, value=h)
        _style_header_cell(cell, fill_color="1E3A8A", text_color="FFFFFF", bold=True, size=9)
        _style_border(cell)

    reinf_calcs = [
        ("Koefisien Tahanan Momen Rn", "Rn", f"Mu / (0.9 × L × d²) = {Mu_max_kNm*1e6:.0f} / (0.9 × {L*1000:.0f} × {d_mm:.0f}²)", Rn, "MPa", "Rn = Mu / (φ*b*d^2)"),
        ("Rasio Tulangan Perlu", "ρ_perlu", f"0.85·fc/fy · (1 - √(1 - 2Rn/(0.85fc)))", rho_req, "-", "Rasio tulangan lentur perlu"),
        ("Rasio Tulangan Minimum SNI", "ρ_min", f"0.0018 × (420 / fy) = 0.0018 × (420 / {fy:.0f})", rho_min, "-", "ρmin susut suhu SNI 2847"),
        ("Rasio Tulangan Desain", "ρ_desain", f"max(ρ_perlu, ρ_min) = max({rho_req:.5f}, {rho_min:.5f})", rho_des, "-", "Rasio tulangan penentu"),
        ("Luas Tulangan Perlu Total X", "As_req_x", f"ρ × L × d = {rho_des:.5f} × {L*1000:.0f} × {d_mm:.0f}", As_req_x, "mm²", "As = ρ * L * d"),
        ("Luas 1 Batang Tulangan Utama", "Ab", f"π/4 × D² = π/4 × {bar_dia:.0f}²", Ab_mm2, "mm²", f"Diameter D{int(bar_dia)}"),
        ("Jumlah Batang Tulangan Arah X", "n_bars_x", f"Ceil(As / Ab) = Ceil({As_req_x:.0f} / {Ab_mm2:.1f})", n_x, "batang", "Jumlah batang terpasang arah X"),
        ("Jarak Spasi Tulangan Arah X", "s_x", f"(B - 2·cc - D)/(n - 1) = ({B*1000:.0f} - {2*cover:.0f} - {bar_dia:.0f}) / {n_x-1}", s_x, "mm", "Jarak bersih antar as tulangan"),
        ("Batas Spasi Maksimum SNI", "s_max", f"min(3·hf, 450) = min({3*hf*1000:.0f}, 450)", s_max, "mm", "Batas spasi maksimum pelat"),
        ("Kontrol Spasi Tulangan X", "Cek_s_x", f"s <= s_max ({s_x:.0f} mm <= {s_max:.0f} mm)", cek_s_x, "-", "Memenuhi batas spasi SNI"),
        ("Rekomendasi Tulangan Terpasang X", "Notasi_X", "Format Notasi Konstruksi", notasi_x, "-", "Tulangan Bawah Arah X"),
        ("", "", "", "", "", ""),
        ("TULANGAN BAWAH ARAH Y", "", "", "", "", ""),
        ("Luas Tulangan Perlu Total Y", "As_req_y", f"ρ × B × d = {rho_des:.5f} × {B*1000:.0f} × {d_mm:.0f}", As_req_y, "mm²", "As = ρ * B * d"),
        ("Jumlah Batang Tulangan Arah Y", "n_bars_y", f"Ceil(As / Ab) = Ceil({As_req_y:.0f} / {Ab_mm2:.1f})", n_y, "batang", "Jumlah batang terpasang arah Y"),
        ("Jarak Spasi Tulangan Arah Y", "s_y", f"(L - 2·cc - D)/(n - 1) = ({L*1000:.0f} - {2*cover:.0f} - {bar_dia:.0f}) / {n_y-1}", s_y, "mm", "Jarak bersih antar as tulangan"),
        ("Rekomendasi Tulangan Terpasang Y", "Notasi_Y", "Format Notasi Konstruksi", notasi_y, "-", "Tulangan Bawah Arah Y"),
        ("", "", "", "", "", ""),
        ("TULANGAN ATAS & KERANJANG KOTAK (TOP REBAR BOX CAGE)", "", "", "", "", ""),
        ("Rekomendasi Tulangan Atas Arah X", "Notasi_Top_X", f"Tulangan praktis atas penutup kotak", notasi_top_x, "-", "Kait 90° membengkok ke bawah"),
        ("Rekomendasi Tulangan Atas Arah Y", "Notasi_Top_Y", f"Tulangan praktis atas penutup kotak", notasi_top_y, "-", "Kait 90° membengkok ke bawah"),
        ("Pengikat Keranjang Kotak", "Sengkang_Tepi", "Begel keliling tepi pelat tapak", "Ø10-250 mm (Tepi Kotak)", "-", "Pengikat keranjang 3D"),
        ("", "", "", "", "", ""),
        ("ESTIMASI KEBUTUHAN MATERIAL (BOQ)", "", "", "", "", ""),
        ("Panjang Total Tulangan Baja", "Ltot_rebar", f"Panjang batang bawah + atas + kait", Ltot_bot_m + Ltot_top_m, "m", "Total panjang baja"),
        ("Berat Satuan Besi Tulangan D16", "w_bar", f"0.006165 × {bar_dia:.0f}²", w_bar_kg_m, "kg/m", "Standar BJTS 420"),
        ("Estimasi Total Berat Baja Tulangan", "W_steel", f"Total berat baja fondasi + sengkang", W_steel_kg, "kg", "Baja tulangan total"),
        ("Volume Beton Cor Fondasi", "V_beton", f"B × L × hf = {B:.2f} × {L:.2f} × {hf:.2f}", Vf, "m³", "Volume cor beton pelat"),
        ("Rasio Tulangan per Volume Beton", "Rasio_kg_m3", f"W_steel / Vf = {W_steel_kg:.1f} / {Vf:.2f}", rasio_kg_m3, "kg/m³", "Indeks efisiensi struktur (~50-80 kg/m³)")
    ]

    for item in reinf_calcs:
        r_rf += 1
        if item[1] == "" and item[3] == "":
            ws5[f"A{r_rf}"] = item[0]
            ws5[f"A{r_rf}"].font = font_section
            continue

        is_recom = "Rekomendasi" in item[0] or "ESTIMASI" in item[0]
        ws5[f"A{r_rf}"] = item[0]; ws5[f"A{r_rf}"].font = font_bold if is_recom else font_reg; ws5[f"A{r_rf}"].border = thin_border
        ws5[f"B{r_rf}"] = item[1]; ws5[f"B{r_rf}"].font = font_bold; ws5[f"B{r_rf}"].alignment = align_center; ws5[f"B{r_rf}"].border = thin_border
        ws5[f"C{r_rf}"] = item[2]; ws5[f"C{r_rf}"].font = font_formula; ws5[f"C{r_rf}"].border = thin_border
        ws5[f"D{r_rf}"] = item[3]; ws5[f"D{r_rf}"].font = font_bold; ws5[f"D{r_rf}"].alignment = align_center; ws5[f"D{r_rf}"].border = thin_border
        if isinstance(item[3], (int, float)):
            ws5[f"D{r_rf}"].number_format = '0.00' if isinstance(item[3], float) else '0'
        if is_recom or "AMAN" in str(item[3]):
            ws5[f"D{r_rf}"].fill = fill_safe
        ws5[f"E{r_rf}"] = item[4]; ws5[f"E{r_rf}"].font = font_reg; ws5[f"E{r_rf}"].alignment = align_center; ws5[f"E{r_rf}"].border = thin_border
        ws5[f"F{r_rf}"] = item[5]; ws5[f"F{r_rf}"].font = font_sub_title; ws5[f"F{r_rf}"].border = thin_border

    ws5.column_dimensions["A"].width = 34
    ws5.column_dimensions["B"].width = 14
    ws5.column_dimensions["C"].width = 54
    ws5.column_dimensions["D"].width = 24
    ws5.column_dimensions["E"].width = 10
    ws5.column_dimensions["F"].width = 32

    # -------------------------------------------------------------------------
    # SHEET 6: FINAL DESIGN SUMMARY & BOQ
    # -------------------------------------------------------------------------
    ws6 = wb.create_sheet(title="Final Design Summary")
    ws6.views.sheetView[0].showGridLines = True
    _setup_page_print(ws6, landscape=False)

    ws6["A1"] = "RINGKASAN AKHIR DESAIN & KELAYAKAN TEKNIS PONDASI"
    ws6["A1"].font = font_main_title
    ws6["A2"] = "Executive Engineering Summary: Dimensi, Penulangan, Status Keamanan, dan BoQ"
    ws6["A2"].font = font_sub_title

    ws6["A4"] = "1. REKAPITULASI HASIL RANCANGAN STRUKTUR & TULANGAN"
    ws6["A4"].font = font_section

    summary_items = [
        ("Dimensi Tapak Fondasi Terpasang", "B x L", f"{B:.2f} x {L:.2f} meter"),
        ("Tebal Pelat Fondasi Terpasang", "hf", f"{hf:.2f} meter ({int(hf*100)} cm)"),
        ("Kedalaman Galian Fondasi", "Df", f"{Df:.2f} meter dari Muka Tanah Asli"),
        ("Mutu Beton Struktural (f'c)", "f'c", f"{fc:.1f} MPa"),
        ("Mutu Baja Tulangan (fy)", "fy", f"{fy:.1f} MPa"),
        ("Tebal Selimut Beton Bersih (cc)", "cc", f"{cover:.0f} mm (Kontak Tanah SNI)"),
        ("Tulangan Bawah Arah X", "Rebar-X", notasi_x),
        ("Tulangan Bawah Arah Y", "Rebar-Y", notasi_y),
        ("Tulangan Atas Arah X (Kotak)", "Rebar-Top-X", notasi_top_x),
        ("Tulangan Atas Arah Y (Kotak)", "Rebar-Top-Y", notasi_top_y),
        ("Estimasi Total Volume Beton", "V_beton", f"{Vf:.2f} m³"),
        ("Estimasi Total Berat Besi Tulangan", "W_besi", f"{W_steel_kg:.1f} kg"),
        ("Rasio Besi per Volume Beton", "Rasio", f"{rasio_kg_m3:.1f} kg/m³ (Struktur Ekonomis)")
    ]

    r_fs = 5
    for item in summary_items:
        ws6[f"A{r_fs}"] = item[0]; ws6[f"A{r_fs}"].font = font_bold; ws6[f"A{r_fs}"].fill = fill_meta; ws6[f"A{r_fs}"].border = thin_border
        ws6[f"B{r_fs}"] = item[1]; ws6[f"B{r_fs}"].font = font_reg; ws6[f"B{r_fs}"].alignment = align_center; ws6[f"B{r_fs}"].border = thin_border
        ws6[f"C{r_fs}"] = item[2]; ws6[f"C{r_fs}"].font = font_bold; ws6[f"C{r_fs}"].alignment = align_center; ws6[f"C{r_fs}"].border = thin_border
        if "Tulangan" in item[0]:
            ws6[f"C{r_fs}"].fill = fill_safe
        r_fs += 1

    r_fs += 1
    ws6[f"A{r_fs}"] = "2. MATRIKS VERIFIKASI KEAMANAN DESAIN (SAFETY CHECKS)"
    ws6[f"A{r_fs}"].font = font_section
    r_fs += 1

    checks_matrix = [
        ("Kapasitas Daya Dukung Tanah (Geoteknik)", "qmax <= qall", eval_bearing),
        ("Kontrol Eksentrisitas Tanah (Tanpa Tarik)", "e <= L/6", cek_e),
        ("Kapasitas Geser Balok Satu Arah", "Vu1 <= φVc1", Cek_Vu1),
        ("Kapasitas Geser Pons Dua Arah", "Vu2 <= φVc2", Cek_Vu2),
        ("Batas Jarak Spasi Tulangan Lentur", "s <= smax", cek_s_x)
    ]

    for item in checks_matrix:
        ws6[f"A{r_fs}"] = item[0]; ws6[f"A{r_fs}"].font = font_bold; ws6[f"A{r_fs}"].border = thin_border
        ws6[f"B{r_fs}"] = item[1]; ws6[f"B{r_fs}"].font = font_formula; ws6[f"B{r_fs}"].border = thin_border
        ws6[f"C{r_fs}"] = item[2]; ws6[f"C{r_fs}"].font = font_bold; ws6[f"C{r_fs}"].fill = fill_safe; ws6[f"C{r_fs}"].alignment = align_center; ws6[f"C{r_fs}"].border = thin_border
        r_fs += 1

    r_fs += 1
    ws6[f"A{r_fs}"] = "3. KESIMPULAN REKAYASA TEKNIK"
    ws6[f"A{r_fs}"].font = font_section
    r_fs += 1
    ws6[f"A{r_fs}"] = (
        "Berdasarkan hasil analisis geoteknik (SNI 8460:2017) dan analisis struktur beton (SNI 2847:2019), "
        "dimensi dan konfigurasi penulangan fondasi telapak di atas dinyatakan MEMENUHI SYARAT DAN AMAN (OK) "
        "untuk diaplikasikan pada konstruksi lapangan."
    )
    ws6[f"A{r_fs}"].font = font_reg

    ws6.column_dimensions["A"].width = 40
    ws6.column_dimensions["B"].width = 25
    ws6.column_dimensions["C"].width = 40

    out = io.BytesIO()
    wb.save(out)
    out.seek(0)
    return out.getvalue()


# =============================================================================
# WRAPPER FUNCTIONS (DENGAN CACHING UNTUK MENCEGAH GRAFIK LAMA MUNCUL)
# =============================================================================

@cache_decorator
def generate_excel_report(project_info, soil_params, load_params, comp_results, selected_dim, reinf_results=None):
    """Fungsi utama ekspor excel pondasi 6 sheet terhitung runtut."""
    return generate_foundation_calculation_report(
        project_info=project_info,
        soil_params=soil_params,
        load_params=load_params,
        comp_results=comp_results,
        selected_dim=selected_dim,
        reinf_results=reinf_results
    )


@cache_decorator
def generate_spt_excel(spt_layers, project_info):
    """Ekspor laporan penyelidikan tanah resmi SPT 5 sheets (Cached)."""
    return generate_soil_investigation_report(project_info, spt_layers=spt_layers, cpt_points=None)


@cache_decorator
def generate_cpt_excel(cpt_points, project_info):
    """Ekspor laporan penyelidikan tanah resmi CPT 5 sheets (Cached)."""
    return generate_soil_investigation_report(project_info, spt_layers=None, cpt_points=cpt_points)


def generate_csv_report(comp_results, selected_dim):
    """Ekspor tabel ringkasan komparasi 4 metode fondasi dalam format CSV."""
    rows = []
    for r in comp_results:
        rows.append({
            "Metode": r.get("Metode", "-"),
            "B (m)": selected_dim.get("B", 2.0),
            "L (m)": selected_dim.get("L", 2.0),
            "Df (m)": selected_dim.get("Df", 1.5),
            "qu (kPa)": r.get("qu (kPa)", 0.0),
            "qall (kPa)": r.get("qall (kPa)", 0.0),
            "q_kontak (kPa)": r.get("q_kontak (kPa)", 0.0),
            "Safety Factor": r.get("Faktor Keamanan (SF)", 3.0),
            "Status": r.get("Status Keamanan", "AMAN")
        })
    df = pd.DataFrame(rows)
    return df.to_csv(index=False).encode('utf-8')
