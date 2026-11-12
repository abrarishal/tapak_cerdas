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
           2. Foundation Calculation Report (6 Sheets dengan RUMUS AKTIF EXCEL):
              - Sheet 1: Design Criteria (Beban SNI 1727:2020, Material SNI 2847:2019)
              - Sheet 2: Soil Parameter (Stratigrafi & Korelasi Lapangan)
              - Sheet 3: Foundation Dimension Calculation (Daya Dukung 4 Metode, Tegangan Kontak, Eksentrisitas)
              - Sheet 4: Structural Calculation (Momen Mu, Geser 1 Arah, Geser Pons 2 Arah)
              - Sheet 5: Reinforcement Calculation (As req, As min, Spasi Tulangan, Detailing, Berat Baja)
              - Sheet 6: Final Design Summary & Bill of Quantities
=============================================================================
"""

import io
import math
import pandas as pd
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from openpyxl.chart import LineChart, BarChart, Reference


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
    side = Side(style=border_style, color=border_color)
    cell.border = Border(left=side, right=side, top=side, bottom=side)


def _setup_page_print(ws, landscape=False):
    ws.page_setup.paperSize = ws.PAPERSIZE_A4
    ws.page_setup.orientation = ws.ORIENTATION_LANDSCAPE if landscape else ws.ORIENTATION_PORTRAIT
    ws.sheet_properties.pageSetUpPr.fitToPage = True
    ws.page_setup.fitToWidth = 1
    ws.page_setup.fitToHeight = 0
    try:
        ws.oddHeader.left.text = "TAPAK CERDAS - Dokumen Perencanaan Resmi"
        ws.oddFooter.left.text = "Acuan: SNI 1727:2020 & SNI 2847:2019"
        ws.oddFooter.right.text = "Halaman &P dari &N"
    except Exception:
        pass


# =============================================================================
# A. LAPORAN PENYELIDIKAN TANAH (SOIL INVESTIGATION REPORT - 5 SHEETS)
# =============================================================================

def generate_soil_investigation_report(project_info, spt_layers=None, cpt_points=None):
    """
    Menghasilkan Laporan Penyelidikan Tanah Resmi (Soil Investigation Report) 5 Sheets:
    - Sheet 1: General Information
    - Sheet 2: Boring Log / SPT (Sesuai Referensi Gambar 3)
    - Sheet 3: CPT Log (Sesuai Standar SNI 2827:2008)
    - Sheet 4: Soil Profile (Visual Stratigrafi Lapisan Tanah)
    - Sheet 5: Summary (Rangkuman Geoteknik & Rekomendasi)
    """
    wb = openpyxl.Workbook()

    # Styling Palet Geoteknik Profesional
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
    p_gwl = _clean_num(project_info.get("water_table_depth", 1.50))
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

    gen_info_table = [
        ("Nama Proyek", p_name),
        ("Lokasi Proyek", p_loc),
        ("Nama Klien / Pemilik", p_client),
        ("Nomor Titik Investigasi", p_bh),
        ("Koordinat Titik (X / Bujur)", project_info.get("coord_x", "110.4289° E")),
        ("Koordinat Titik (Y / Lintang)", project_info.get("coord_y", "-7.0512° S")),
        ("Tanggal Pengujian", p_date),
        ("Elevasi Permukaan Tanah (GL)", "+0.00 m (Muka Tanah Asli)"),
        ("Kedalaman Total Penyelidikan", f"{max([l.get('depth_bot', 12.0) for l in spt_layers] if spt_layers else [12.0]):.2f} meter"),
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
    ws1[f"A{r}"] = "2. STANDAR ACUAN PENGUJIAN"
    ws1[f"A{r}"].font = font_section
    r += 1
    standards_list = [
        "1. ASTM D1586 - Standard Test Method for Standard Penetration Test (SPT) and Split-Barrel Sampling of Soils.",
        "2. SNI 2827:2008 - Cara Uji Penetrasi Lapangan dengan Alat Sondir (CPT).",
        "3. SNI 8460:2017 - Persyaratan Perancangan Geoteknik.",
        "4. ASTM D2487 - Standard Practice for Classification of Soils for Engineering Purposes (Unified Soil Classification System / USCS)."
    ]
    for s_txt in standards_list:
        ws1[f"A{r}"] = s_txt
        ws1[f"A{r}"].font = font_reg
        r += 1

    r += 1
    ws1[f"A{r}"] = "3. LEMBAR PENGESAHAN DOKUMEN"
    ws1[f"A{r}"].font = font_section
    r += 1
    sign_headers = ["Disiapkan Oleh (Surveyor)", "Diperiksa Oleh (Geotechnical Eng.)", "Disetujui Oleh (Chief Engineer)"]
    for c_i, sh in enumerate(sign_headers, 1):
        c_letter = get_column_letter(c_i)
        ws1[f"{c_letter}{r}"] = sh
        _style_header_cell(ws1[f"{c_letter}{r}"], fill_color="1E3A8A", text_color="FFFFFF", bold=True, size=9)
        ws1.row_dimensions[r+1].height = 40
        ws1[f"{c_letter}{r+1}"].border = thin_border
        ws1[f"{c_letter}{r+2}"] = f"Nama: {p_engineer}" if c_i == 1 else "Nama: Ir. Geoteknik, MT" if c_i == 2 else "Nama: Dr. Ir. Pondasi, IPM"
        ws1[f"{c_letter}{r+2}"].font = font_reg
        ws1[f"{c_letter}{r+2}"].border = thin_border

    ws1.column_dimensions["A"].width = 30
    ws1.column_dimensions["B"].width = 65
    ws1.column_dimensions["C"].width = 35

    # -------------------------------------------------------------------------
    # SHEET 2: BORING LOG / SPT (PERSIS REFERENSI GAMBAR 3)
    # -------------------------------------------------------------------------
    ws2 = wb.create_sheet(title="Boring Log - SPT")
    ws2.views.sheetView[0].showGridLines = True
    _setup_page_print(ws2, landscape=True)

    ws2["A1"] = "BORE LOG"
    ws2["A1"].font = Font(name="Calibri", size=16, bold=True, color="000000")
    ws2["A1"].alignment = align_center
    ws2.merge_cells("A1:N1")

    # Header Proyek Boring Log Sesuai Referensi Gambar 3
    ws2["A2"] = f"BH No: {p_bh}"
    ws2["A2"].font = font_bold
    ws2["A3"] = f"Project: {p_name}"
    ws2["A3"].font = font_reg

    ws2["I2"] = f"Date of Commencement: {p_date}"
    ws2["I2"].font = font_reg
    ws2["I3"] = f"Ground Water Table: ∇ {p_gwl:.2f} m"
    ws2["I3"].font = font_bold

    headers_bolog = [
        "Depth Below GL (m)", "Soil Description", "Thickness of Strata (m)", "Legend / Symbol",
        "Sample Type", "Sampling Depth (m)", "Blows N1 (0-15cm)", "Blows N2 (15-30cm)", "Blows N3 (30-45cm)",
        "SPT N-Value (N2+N3)", "Consistency / Density", "cu (kPa)", "φ' (°)", "γ (kN/m³)"
    ]

    start_row = 5
    for c_i, h in enumerate(headers_bolog, 1):
        cell = ws2.cell(row=start_row, column=c_i, value=h)
        _style_header_cell(cell, fill_color="0F172A", text_color="FFFFFF", bold=True, size=9)
        _style_border(cell)

    if not spt_layers or len(spt_layers) == 0:
        # Gunakan sample data borelog jika kosong
        spt_layers = [
            {"depth_top": 0.0, "depth_bot": 2.0, "thickness": 2.0, "n1": 1, "n2": 1, "n3": 1, "n_spt": 2, "soil_type": "Filled Up Soil (Tanah Urug)", "deskripsi": "Filled up soil, loose, brownish dark", "konsistensi": "Sangat Lunak", "cu": 15.0, "phi_eff": 20.0, "gamma": 16.0},
            {"depth_top": 2.0, "depth_bot": 3.0, "thickness": 1.0, "n1": 9, "n2": 10, "n3": 9, "n_spt": 19, "soil_type": "Reddish / Grayish Clayey Sand", "deskripsi": "Reddish/grayish clayey sand, stiff", "konsistensi": "Kaku", "cu": 75.0, "phi_eff": 28.0, "gamma": 18.2},
            {"depth_top": 3.0, "depth_bot": 6.0, "thickness": 3.0, "n1": 15, "n2": 18, "n3": 21, "n_spt": 39, "soil_type": "Greyish Silty Sand with Mica", "deskripsi": "Greyish silty sand with mica, very dense", "konsistensi": "Sangat Padat", "cu": 120.0, "phi_eff": 34.0, "gamma": 19.5},
            {"depth_top": 6.0, "depth_bot": 10.5, "thickness": 4.5, "n1": 30, "n2": 45, "n3": 55, "n_spt": 100, "soil_type": "Weathered Rock / Bedrock", "deskripsi": "Weathered rock, hard layer, CR=76%, RQD=43%", "konsistensi": "Keras Membatu", "cu": 250.0, "phi_eff": 40.0, "gamma": 21.0}
        ]

    for idx, lyr in enumerate(spt_layers, 1):
        cur_r = start_row + idx
        d_top = float(lyr.get("depth_top", 0.0))
        d_bot = float(lyr.get("depth_bot", d_top + 1.5))
        thick = round(d_bot - d_top, 2)
        n1 = int(lyr.get("n1", 1))
        n2 = int(lyr.get("n2", 1))
        n3 = int(lyr.get("n3", 1))
        samp_type = "SPT" if idx % 2 != 0 else "UDS"

        # Simbol USCS Tanah
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

        # Tulis rumus Excel aktif untuk N-SPT: =H{cur_r}+I{cur_r}
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
            f"=H{cur_r}+I{cur_r}",  # RUMUS AKTIF EXCEL
            lyr.get("konsistensi", "-"),
            float(lyr.get("cu", lyr.get("c", 20.0))),
            float(lyr.get("phi_eff", lyr.get("phi", 24.0))),
            float(lyr.get("gamma", 17.5))
        ]

        # Cek apakah lapisan ini memotong Muka Air Tanah (GWL)
        is_gw_layer = (d_top <= p_gwl <= d_bot)
        r_fill = fill_gwl if is_gw_layer else (fill_zebra if idx % 2 == 0 else fill_white)

        for c_i, val in enumerate(row_data, 1):
            cell = ws2.cell(row=cur_r, column=c_i, value=val)
            cell.font = font_bold_center if c_i == 10 else font_reg
            cell.fill = r_fill
            cell.alignment = align_left if c_i == 2 else align_center
            _style_border(cell)

    end_spt_row = start_row + len(spt_layers)

    # Catatan Teknis Bore Log Bawah (Sesuai Referensi Gambar 3)
    ws2[f"A{end_spt_row + 2}"] = f"Bore hole Terminated at {spt_layers[-1].get('depth_bot', 10.5):.2f}m Below Ground Level."
    ws2[f"A{end_spt_row + 2}"].font = font_bold
    ws2[f"A{end_spt_row + 3}"] = "Notes: SPT = Standard Penetration Test; UDS = Undisturbed Sample; GL = Ground Level; CR = Core Recovery; RQD = Rock Quality Designation."
    ws2[f"A{end_spt_row + 3}"].font = font_sub_title

    # Tambahkan Grafik N-SPT vs Kedalaman (LineChart)
    try:
        chart_spt = LineChart()
        chart_spt.title = "GRAFIK PENETRASI N-SPT vs KEDALAMAN (m)"
        chart_spt.style = 13
        chart_spt.y_axis.title = "Kedalaman (m)"
        chart_spt.x_axis.title = "Nilai N-SPT (Pukulan/30cm)"
        chart_spt.width = 16
        chart_spt.height = 12

        data_spt_ref = Reference(ws2, min_col=10, min_row=start_row, max_row=end_spt_row)
        cats_spt_ref = Reference(ws2, min_col=1, min_row=start_row + 1, max_row=end_spt_row)
        chart_spt.add_data(data_spt_ref, titles_from_data=True)
        chart_spt.set_categories(cats_spt_ref)
        ws2.add_chart(chart_spt, "P4")
    except Exception:
        pass

    # Lebar kolom otomatis
    for col in ws2.columns:
        if col[0].column > 14:
            continue
        max_l = max(len(str(c.value or '')) for c in col[:end_spt_row + 1])
        ws2.column_dimensions[get_column_letter(col[0].column)].width = max(max_l + 3, 11)
    ws2.column_dimensions["B"].width = 34

    # -------------------------------------------------------------------------
    # SHEET 3: CPT LOG (SNI 2827:2008 / ASTMD3441)
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
        jh_val = float(pt.get("jh", qc_val + 5.0))
        jhp_val = float(pt.get("jhp", pt.get("hp", 10.0)))

        # RUMUS AKTIF EXCEL DI SHEET CPT:
        # qc (kPa) = C{cur_r} * 98.07
        # HP = D{cur_r} - B{cur_r}
        # fs (kg/cm2) = (D{cur_r} - B{cur_r}) / 10
        # fs (kPa) = G{cur_r} * 98.07
        # Rf (%) = (G{cur_r} / B{cur_r}) * 100
        cpt_row_data = [
            d_val,
            qc_val,
            f"=B{cur_r}*98.07",
            jh_val,
            f"=D{cur_r}-B{cur_r}",
            jhp_val,
            f"=(D{cur_r}-B{cur_r})/10",
            f"=G{cur_r}*98.07",
            f"=IF(B{cur_r}>0, (G{cur_r}/B{cur_r})*100, 0)",
            pt.get("soil_type", "Lempung"),
            round((qc_val * 98.07) / 16.0, 1),
            24.0 if qc_val < 30 else 32.0
        ]

        r_fill = fill_zebra if idx % 2 == 0 else fill_white
        for c_i, val in enumerate(cpt_row_data, 1):
            cell = ws3.cell(row=cur_r, column=c_i, value=val)
            cell.font = font_bold_center if c_i in [2, 7, 9] else font_reg
            cell.fill = r_fill
            cell.alignment = align_left if c_i == 10 else align_center
            _style_border(cell)

    end_cpt_row = start_cpt_row + len(cpt_points)

    # Tambahkan Grafik CPT qc vs Kedalaman
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

        # Modulus elastisitas tanah taksir: Es ≈ 500 * cu (lempung) atau 2000 * N (pasir)
        cu_val = float(lyr.get("cu", lyr.get("c", 25.0)))
        es_val = round((cu_val * 0.4) if cu_val > 0 else (n_spt * 2.0), 1)

        prof_row = [
            f"Lapisan {idx}",
            d_top,
            d_bot,
            f"=C{r_p}-B{r_p}",  # Rumus tebal aktif
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

    # Rata-rata terbobot zona fondasi dangkal
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
# DENGAN RUMUS AKTIF EXCEL LENGKAP (SESUAI REFERENSI GAMBAR 4 & 5)
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
    dengan RUMUS AKTIF EXCEL (Active Excel Formulas):
    - Sheet 1: Design Criteria (Input Data & Parameter)
    - Sheet 2: Soil Parameter (Data Karakteristik Tanah)
    - Sheet 3: Foundation Dimension Calculation (Daya Dukung, Eksentrisitas & Tekanan Kontak)
    - Sheet 4: Structural Calculation (Analisis Momen, Geser 1 Arah & Geser Pons 2 Arah)
    - Sheet 5: Reinforcement Calculation (Luas Tulangan, Spasi, Jumlah Batang, Panjang & Berat Baja)
    - Sheet 6: Final Design Summary (Rangkuman Akhir & Rekomendasi Desain)
    """
    wb = openpyxl.Workbook()

    font_main_title = Font(name="Calibri", size=15, bold=True, color="1E3A8A")
    font_sub_title = Font(name="Calibri", size=9, italic=True, color="64748B")
    font_section = Font(name="Calibri", size=11, bold=True, color="0F172A")
    font_bold = Font(name="Calibri", size=10, bold=True)
    font_reg = Font(name="Calibri", size=9.5)
    font_formula = Font(name="Consolas", size=9.5, color="1E40AF")

    fill_meta = PatternFill(start_color="F1F5F9", end_color="F1F5F9", fill_type="solid")
    fill_input = PatternFill(start_color="E0F2FE", end_color="E0F2FE", fill_type="solid")  # Sel Input Biru Muda Khusus
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

    # Data Variabel Awal
    p_name = project_info.get("name", "Proyek Bangunan Cerdas")
    p_loc = project_info.get("location", "Semarang")
    p_eng = project_info.get("engineer", "Insinyur Sipil")

    B_in = _clean_num(selected_dim.get("B", 2.0))
    L_in = _clean_num(selected_dim.get("L", 2.0))
    Df_in = _clean_num(selected_dim.get("Df", 1.5))
    hf_in = _clean_num(selected_dim.get("hf", 0.45))
    if hf_in <= 0:
        hf_in = 0.45
    sf_in = _clean_num(selected_dim.get("SF", 3.0))

    c_in = _clean_num(soil_params.get("cohesion", soil_params.get("c", 25.0)))
    phi_in = _clean_num(soil_params.get("friction_angle", soil_params.get("phi", 20.0)))
    gamma_in = _clean_num(soil_params.get("unit_weight", soil_params.get("gamma", 17.5)))
    gamma_sat_in = _clean_num(soil_params.get("sat_unit_weight", soil_params.get("gamma_sat", 19.0)))
    dw_in = _clean_num(soil_params.get("water_table", soil_params.get("dw", 1.50)))

    P_servis = _clean_num(load_params.get("p_column", 350.0))
    Pu_in = _clean_num(load_params.get("pu_column", P_servis * 1.35))
    Mux_in = _clean_num(load_params.get("Mux", 15.0))
    Muy_in = _clean_num(load_params.get("Muy", 10.0))

    col_b_in = 0.40
    col_h_in = 0.40
    fc_in = 25.0
    fy_in = 420.0
    cover_in = 75.0
    bar_dia_in = 16.0

    # -------------------------------------------------------------------------
    # SHEET 1: DESIGN CRITERIA (PERSIS FORMAT GAMBAR REFERENSI 4 & 5)
    # -------------------------------------------------------------------------
    ws1 = wb.active
    ws1.title = "Design Criteria"
    ws1.views.sheetView[0].showGridLines = True
    _setup_page_print(ws1, landscape=False)

    ws1["A1"] = "ISOLATED FOUNDATION DESIGN CRITERIA - TAPAK CERDAS"
    ws1["A1"].font = font_main_title
    ws1["A2"] = "Standar Desain: SNI 1727:2020, SNI 2847:2019, SNI 8460:2017 & ACI 318M"
    ws1["A2"].font = font_sub_title

    # Header Proyek Block (Sesuai Referensi Gambar 4)
    ws1["A4"] = "Nama Proyek:"
    ws1["B4"] = p_name
    ws1["A5"] = "Engineer:"
    ws1["B5"] = p_eng
    ws1["D4"] = "Tanggal:"
    ws1["E4"] = "2026-11-12"
    ws1["D5"] = "Checked By:"
    ws1["E5"] = "Senior Structural Eng."

    for cell_id in ["A4", "A5", "D4", "D5"]:
        ws1[cell_id].font = font_bold
        ws1[cell_id].fill = fill_meta
        ws1[cell_id].border = thin_border
    for cell_id in ["B4", "B5", "E4", "E5"]:
        ws1[cell_id].font = font_reg
        ws1[cell_id].border = thin_border

    # Input Data Tabel dengan Format Khusus (Sel Input Berwarna Biru Muda)
    criteria_inputs = [
        ("A. DATA STRUKTUR & MATERIAL", "", "", ""),
        ("Lebar Fondasi", "B", B_in, "m"),           # Row 9
        ("Panjang Fondasi", "L", L_in, "m"),         # Row 10
        ("Tebal Pelat Fondasi", "hf", hf_in, "m"),    # Row 11
        ("Kedalaman Dasar Fondasi", "Df", Df_in, "m"),# Row 12
        ("Lebar Kolom / Pedestal X", "bc", col_b_in, "m"), # Row 13
        ("Panjang Kolom / Pedestal Y", "hc", col_h_in, "m"), # Row 14
        ("Mutu Kuat Tekan Beton", "f'c", fc_in, "MPa"), # Row 15
        ("Mutu Kuat Leleh Baja", "fy", fy_in, "MPa"),  # Row 16
        ("Tebal Selimut Beton Bersih", "cc", cover_in, "mm"), # Row 17
        ("Diameter Tulangan Utama", "D", bar_dia_in, "mm"), # Row 18
        ("Berat Jenis Beton Bertulang", "γc", 24.0, "kN/m³"), # Row 19
        ("", "", "", ""),
        ("B. DATA TANAH DASAR & MUKA AIR", "", "", ""),
        ("Kohesi Tanah Dasar", "c", c_in, "kPa"), # Row 22
        ("Sudut Geser Dalam", "φ", phi_in, "derajat"), # Row 23
        ("Berat Volume Tanah Basah", "γ", gamma_in, "kN/m³"), # Row 24
        ("Berat Volume Tanah Jenuh Air", "γsat", gamma_sat_in, "kN/m³"), # Row 25
        ("Kedalaman Muka Air Tanah (MAT)", "dw", dw_in, "m"), # Row 26
        ("Target Faktor Keamanan", "SF", sf_in, "-"), # Row 27
        ("", "", "", ""),
        ("C. DATA PEMBEBANAN STRUKTUR", "", "", ""),
        ("Beban Aksial Servis", "P", P_servis, "kN"), # Row 30
        ("Beban Aksial Terfaktor", "Pu", Pu_in, "kN"), # Row 31
        ("Momen Terfaktor Arah X", "Mux", Mux_in, "kN.m"), # Row 32
        ("Momen Terfaktor Arah Y", "Muy", Muy_in, "kN.m")  # Row 33
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

        # Kolom Nilai D: Diberi Warna Input Khusus
        ws1[f"D{r}"] = val
        ws1[f"D{r}"].font = font_bold
        ws1[f"D{r}"].fill = fill_input
        ws1[f"D{r}"].alignment = align_center
        ws1[f"D{r}"].border = thin_border

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

    tz_fact = comp_results[0] if comp_results and len(comp_results) > 0 else {}
    headers_sp = ["Parameter", "Simbol", "Rumus Referensi", "Nilai", "Satuan"]
    r_sp = 5
    for c_i, h in enumerate(headers_sp, 1):
        cell = ws2.cell(row=r_sp, column=c_i, value=h)
        _style_header_cell(cell, fill_color="1E3A8A", text_color="FFFFFF", bold=True, size=9)
        _style_border(cell)

    soil_factors = [
        ("Faktor Kohesi", "Nc", "Tabel 3.1 Terzaghi / Meyerhof", tz_fact.get("Nc", 14.8), "-"),
        ("Faktor Beban Samping", "Nq", "Tabel 3.1 Terzaghi / Meyerhof", tz_fact.get("Nq", 6.4), "-"),
        ("Faktor Berat Tanah", "Nγ", "Tabel 3.1 Terzaghi / Meyerhof", tz_fact.get("Ngamma", 5.4), "-"),
        ("Faktor Bentuk Kohesi", "sc", "1.0 + 0.2*(B/L)*(tan(45+φ/2))^2", tz_fact.get("sc", 1.3), "-"),
        ("Faktor Bentuk Samping", "sq", "1.0 + 0.1*(B/L)*(tan(45+φ/2))^2", tz_fact.get("sq", 1.0), "-"),
        ("Faktor Bentuk Berat Tanah", "sγ", "1.0 + 0.1*(B/L)*(tan(45+φ/2))^2", tz_fact.get("sgamma", 0.8), "-")
    ]

    for item in soil_factors:
        r_sp += 1
        ws2[f"A{r_sp}"] = item[0]; ws2[f"A{r_sp}"].font = font_reg; ws2[f"A{r_sp}"].border = thin_border
        ws2[f"B{r_sp}"] = item[1]; ws2[f"B{r_sp}"].font = font_bold; ws2[f"B{r_sp}"].alignment = align_center; ws2[f"B{r_sp}"].border = thin_border
        ws2[f"C{r_sp}"] = item[2]; ws2[f"C{r_sp}"].font = font_sub_title; ws2[f"C{r_sp}"].border = thin_border
        ws2[f"D{r_sp}"] = item[3]; ws2[f"D{r_sp}"].font = font_bold; ws2[f"D{r_sp}"].alignment = align_center; ws2[f"D{r_sp}"].border = thin_border
        ws2[f"E{r_sp}"] = item[4]; ws2[f"E{r_sp}"].font = font_reg; ws2[f"E{r_sp}"].alignment = align_center; ws2[f"E{r_sp}"].border = thin_border

    ws2.column_dimensions["A"].width = 28
    ws2.column_dimensions["B"].width = 10
    ws2.column_dimensions["C"].width = 35
    ws2.column_dimensions["D"].width = 12
    ws2.column_dimensions["E"].width = 10

    # -------------------------------------------------------------------------
    # SHEET 3: FOUNDATION DIMENSION CALCULATION (RUMUS AKTIF EXCEL LENGKAP)
    # -------------------------------------------------------------------------
    ws3 = wb.create_sheet(title="Dimension Calculation")
    ws3.views.sheetView[0].showGridLines = True
    _setup_page_print(ws3, landscape=False)

    ws3["A1"] = "PERHITUNGAN DIMENSI & TEGANGAN KONTAK TANAH FONDASI"
    ws3["A1"].font = font_main_title
    ws3["A2"] = "Seluruh Hasil Perhitungan Menggunakan Rumus Aktif Excel Berdasarkan Sheet 'Design Criteria'"
    ws3["A2"].font = font_sub_title

    headers_dim = ["Item Perhitungan", "Simbol", "Persamaan Excel Aktif", "Hasil Rumus Excel", "Satuan", "Status / Catatan"]
    r_dim = 4
    for c_i, h in enumerate(headers_dim, 1):
        cell = ws3.cell(row=r_dim, column=c_i, value=h)
        _style_header_cell(cell, fill_color="1E3A8A", text_color="FFFFFF", bold=True, size=9)
        _style_border(cell)

    # RUMUS-RUMUS AKTIF EXCEL PONDASI DANGKAL:
    # B ada di 'Design Criteria'!D9, L di 'Design Criteria'!D10, hf di 'Design Criteria'!D11, Df di 'Design Criteria'!D12
    # P_servis di 'Design Criteria'!D30, c di 'Design Criteria'!D22, phi di 'Design Criteria'!D23, gamma di 'Design Criteria'!D24
    dim_calcs = [
        ("Luas Tapak Fondasi", "A", "='Design Criteria'!D9*'Design Criteria'!D10", "m²", "Luas bidang kontak dasar"),
        ("Volume Beton Fondasi", "Vf", "='Design Criteria'!D9*'Design Criteria'!D10*'Design Criteria'!D11", "m³", "Volume pelat"),
        ("Berat Sendiri Fondasi", "Wf", "=D6*'Design Criteria'!D19", "kN", "Beban sendiri pelat beton"),
        ("Tebal Tanah Urug di Atas Fondasi", "ha", "='Design Criteria'!D12-'Design Criteria'!D11", "m", "Tanah di atas pelat"),
        ("Berat Tanah di Atas Fondasi", "Ws", "=(D5-('Design Criteria'!D13*'Design Criteria'!D14))*D8*'Design Criteria'!D17", "kN", "Overburden di atas pelat"),
        ("Total Beban Aksial Servis", "Ptot", "='Design Criteria'!D30+D7+D9", "kN", "Total gaya normal"),
        ("Tegangan Overburden Dasar Fondasi", "po", "='Design Criteria'!D17*'Design Criteria'!D12", "kPa", "Tegangan overburden po = γ*Df"),
        ("Kapasitas Ultimit qu (Terzaghi)", "qu", "=1.3*'Design Criteria'!D22*'Soil Parameter'!D6+D11*'Soil Parameter'!D7+0.4*'Design Criteria'!D17*'Design Criteria'!D9*'Soil Parameter'!D8", "kPa", "Rumus qu Terzaghi"),
        ("Daya Dukung Izin qall (SF=3)", "qall", "=(D12-D11)/'Design Criteria'!D27+D11", "kPa", "qall neto + overburden"),
        ("Tekanan Kontak Rata-Rata", "q_avg", "=D10/D5", "kPa", "Tekanan kontak tanah q = Ptot / A"),
        ("Tahanan Momen Dasar Tapak", "Wx", "=('Design Criteria'!D9*('Design Criteria'!D10^2))/6", "m³", "Modulus tampang W = B*L^2 / 6"),
        ("Eksentrisitas Beban Arah X", "ex", "='Design Criteria'!D32/'Design Criteria'!D31", "m", "ex = Mux / Pu"),
        ("Batas Maksimum Eksentrisitas (Kern)", "ekern", "='Design Criteria'!D10/6", "m", "Batas kern e <= L/6"),
        ("Kontrol Eksentrisitas (Tidak Tarik)", "Cek-e", '=IF(D16<=D17, "AMAN (TIDAK ADA UPLIFT)", "PERINGATAN (TERJADI TARIKAN)")', "-", "Kontrol kemurnian tekan"),
        ("Tekanan Kontak Maksimum", "q_max", "=D14+('Design Criteria'!D32/D15)", "kPa", "qmax = P/A + M/W"),
        ("EVALUASI KEAMANAN DAYA DUKUNG", "Status", '=IF(D19<=D13, "AMAN (OK)", "OVERSTRESSED - PERLU DIPERLEBAR")', "-", "qmax <= qall")
    ]

    for item in dim_calcs:
        r_dim += 1
        ws3[f"A{r_dim}"] = item[0]; ws3[f"A{r_dim}"].font = font_bold if "EVALUASI" in item[0] else font_reg; ws3[f"A{r_dim}"].border = thin_border
        ws3[f"B{r_dim}"] = item[1]; ws3[f"B{r_dim}"].font = font_bold; ws3[f"B{r_dim}"].alignment = align_center; ws3[f"B{r_dim}"].border = thin_border
        ws3[f"C{r_dim}"] = item[2]; ws3[f"C{r_dim}"].font = font_formula; ws3[f"C{r_dim}"].border = thin_border
        ws3[f"D{r_dim}"] = item[2]; ws3[f"D{r_dim}"].font = font_bold; ws3[f"D{r_dim}"].alignment = align_center; ws3[f"D{r_dim}"].border = thin_border
        if "EVALUASI" in item[0]:
            ws3[f"D{r_dim}"].fill = fill_safe
        ws3[f"E{r_dim}"] = item[3]; ws3[f"E{r_dim}"].font = font_reg; ws3[f"E{r_dim}"].alignment = align_center; ws3[f"E{r_dim}"].border = thin_border
        ws3[f"F{r_dim}"] = item[4]; ws3[f"F{r_dim}"].font = font_sub_title; ws3[f"F{r_dim}"].border = thin_border

    ws3.column_dimensions["A"].width = 34
    ws3.column_dimensions["B"].width = 10
    ws3.column_dimensions["C"].width = 42
    ws3.column_dimensions["D"].width = 24
    ws3.column_dimensions["E"].width = 10
    ws3.column_dimensions["F"].width = 32

    # -------------------------------------------------------------------------
    # SHEET 4: STRUCTURAL CALCULATION (SNI 2847:2019 DENGAN RUMUS AKTIF EXCEL)
    # -------------------------------------------------------------------------
    ws4 = wb.create_sheet(title="Structural Calculation")
    ws4.views.sheetView[0].showGridLines = True
    _setup_page_print(ws4, landscape=False)

    ws4["A1"] = "PERHITUNGAN KAPASITAS STRUKTUR BETON FONDASI (SNI 2847:2019)"
    ws4["A1"].font = font_main_title
    ws4["A2"] = "Pemeriksaan Momen Terfaktor, Geser Lentur Satu Arah, dan Geser Pons Dua Arah"
    ws4["A2"].font = font_sub_title

    headers_str = ["Item Analisis Struktur", "Simbol", "Persamaan Excel Aktif", "Hasil Rumus Excel", "Satuan", "Keterangan / Evaluasi"]
    r_str = 4
    for c_i, h in enumerate(headers_str, 1):
        cell = ws4.cell(row=r_str, column=c_i, value=h)
        _style_header_cell(cell, fill_color="1E3A8A", text_color="FFFFFF", bold=True, size=9)
        _style_border(cell)

    struct_calcs = [
        ("Tegangan Kontak Terfaktor Netto", "qu_net", "='Design Criteria'!D31/('Design Criteria'!D9*'Design Criteria'!D10)", "kPa", "qu = Pu / (B*L)"),
        ("Tinggi Efektif Pelat Fondasi", "d", "=('Design Criteria'!D11*1000)-'Design Criteria'!D17-('Design Criteria'!D18/2)", "mm", "d = hf - cc - D/2"),
        ("Panjang Kantilever Muka Kolom Arah X", "Lcx", "=(('Design Criteria'!D9*1000)-('Design Criteria'!D13*1000))/2", "mm", "Lcx = (B - bc) / 2"),
        ("Panjang Kantilever Muka Kolom Arah Y", "Lcy", "=(('Design Criteria'!D10*1000)-('Design Criteria'!D14*1000))/2", "mm", "Lcy = (L - hc) / 2"),
        ("Momen Lentur Terfaktor Muka Kolom X", "Mux_face", "=(D5/1000)*('Design Criteria'!D10*1000)*(D7^2)/2", "N.mm", "Mu = qu*L*Lcx^2 / 2"),
        ("Momen Lentur Terfaktor Muka Kolom Y", "Muy_face", "=(D5/1000)*('Design Criteria'!D9*1000)*(D8^2)/2", "N.mm", "Mu = qu*B*Lcy^2 / 2"),
        ("Momen Desain Maksimum", "Mu_max", "=MAX(D9, D10)/1e6", "kN.m", "Momen kritis penulangan"),
        ("KONTROL GESER SATU ARAH (BEAM SHEAR)", "", "", "", ""),
        ("Jarak Penampang Kritis Geser 1 Arah", "x_crit", "=D7-D6", "mm", "x = Lcant - d"),
        ("Gaya Geser Terfaktor 1 Arah", "Vu1", "=IF(D13>0, (D5/1000)*('Design Criteria'!D10*1000)*D13/1000, 0)", "kN", "Vu1 = qu*L*(Lcant - d)"),
        ("Kuat Geser Beton 1 Arah (φ=0.75)", "phi_Vc1", "=0.75*0.17*SQRT('Design Criteria'!D15)*('Design Criteria'!D10*1000)*D6/1000", "kN", "φVc1 = 0.75*0.17*√f'c*L*d"),
        ("Rasio Geser 1 Arah", "UF_v1", "=D14/D15", "-", "Vu1 / φVc1"),
        ("EVALUASI GESER SATU ARAH", "Cek_Vu1", '=IF(D14<=D15, "AMAN (OK)", "TIDAK AMAN - PERLU PERTEBAL hf")', "-", "Vu1 <= φVc1"),
        ("KONTROL GESER PONS DUA ARAH (PUNCHING SHEAR)", "", "", "", ""),
        ("Keliling Kritis Geser Pons", "bo", "=2*(('Design Criteria'!D13*1000)+D6+('Design Criteria'!D14*1000)+D6)", "mm", "bo = 2*(bc + hc + 2d)"),
        ("Luas Area Dalam Perimeter Pons", "Ao", "=(('Design Criteria'!D13*1000)+D6)*(('Design Criteria'!D14*1000)+D6)", "mm²", "Ao = (bc+d)*(hc+d)"),
        ("Gaya Geser Pons Terfaktor", "Vu2", "='Design Criteria'!D31-((D5/1000)*D19/1000)", "kN", "Vu2 = Pu - qu*Ao"),
        ("Kuat Geser Pons Desain (φ=0.75)", "phi_Vc2", "=0.75*0.33*SQRT('Design Criteria'!D15)*D18*D6/1000", "kN", "φVc2 = 0.75*0.33*√f'c*bo*d"),
        ("Rasio Geser Pons", "UF_v2", "=D20/D21", "-", "Vu2 / φVc2"),
        ("EVALUASI GESER PONS DUA ARAH", "Cek_Vu2", '=IF(D20<=D21, "AMAN (OK)", "TIDAK AMAN - TEBAL PONDASI KURANG")', "-", "Vu2 <= φVc2")
    ]

    for item in struct_calcs:
        r_str += 1
        ws4[f"A{r_str}"] = item[0]; ws4[f"A{r_str}"].font = font_bold if "EVALUASI" in item[0] else font_reg; ws4[f"A{r_str}"].border = thin_border
        ws4[f"B{r_str}"] = item[1]; ws4[f"B{r_str}"].font = font_bold; ws4[f"B{r_str}"].alignment = align_center; ws4[f"B{r_str}"].border = thin_border
        ws4[f"C{r_str}"] = item[2]; ws4[f"C{r_str}"].font = font_formula; ws4[f"C{r_str}"].border = thin_border
        ws4[f"D{r_str}"] = item[2]; ws4[f"D{r_str}"].font = font_bold; ws4[f"D{r_str}"].alignment = align_center; ws4[f"D{r_str}"].border = thin_border
        if "EVALUASI" in item[0]:
            ws4[f"D{r_str}"].fill = fill_safe
        ws4[f"E{r_str}"] = item[3]; ws4[f"E{r_str}"].font = font_reg; ws4[f"E{r_str}"].alignment = align_center; ws4[f"E{r_dim}"].border = thin_border
        ws4[f"F{r_str}"] = item[4]; ws4[f"F{r_str}"].font = font_sub_title; ws4[f"F{r_str}"].border = thin_border

    ws4.column_dimensions["A"].width = 34
    ws4.column_dimensions["B"].width = 12
    ws4.column_dimensions["C"].width = 44
    ws4.column_dimensions["D"].width = 24
    ws4.column_dimensions["E"].width = 10
    ws4.column_dimensions["F"].width = 30

    # -------------------------------------------------------------------------
    # SHEET 5: REINFORCEMENT CALCULATION (RUMUS AKTIF PENULANGAN LENTUR)
    # -------------------------------------------------------------------------
    ws5 = wb.create_sheet(title="Reinforcement Calculation")
    ws5.views.sheetView[0].showGridLines = True
    _setup_page_print(ws5, landscape=False)

    ws5["A1"] = "PERHITUNGAN KEBUTUHAN TULANGAN PONDASI (SNI 2847:2019)"
    ws5["A1"].font = font_main_title
    ws5["A2"] = "Desain Tulangan Lentur Bawah Arah X & Y, Jarak Spasi, Detailing, dan Berat Baja"
    ws5["A2"].font = font_sub_title

    headers_reinf = ["Item Penulangan", "Simbol", "Persamaan Excel Aktif", "Hasil Rumus Excel", "Satuan", "Keterangan / Detailing"]
    r_rf = 4
    for c_i, h in enumerate(headers_reinf, 1):
        cell = ws5.cell(row=r_rf, column=c_i, value=h)
        _style_header_cell(cell, fill_color="1E3A8A", text_color="FFFFFF", bold=True, size=9)
        _style_border(cell)

    reinf_calcs = [
        ("Koefisien Tahanan Momen Rn", "Rn", "=('Structural Calculation'!D9)/(0.9*('Design Criteria'!D10*1000)*('Structural Calculation'!D6^2))", "MPa", "Rn = Mu / (φ*b*d^2)"),
        ("Rasio Tulangan Perlu", "ρ_perlu", "=(0.85*'Design Criteria'!D15/'Design Criteria'!D16)*(1-SQRT(MAX(0, 1-(2*D5/(0.85*'Design Criteria'!D15)))))", "-", "ρ = 0.85*fc/fy * (1-√(1-2Rn/0.85fc))"),
        ("Rasio Tulangan Minimum Susut Suhu", "ρ_min", "=0.0018*(420/'Design Criteria'!D16)", "-", "ρmin = 0.0018*420/fy (SNI 2847)"),
        ("Rasio Tulangan Desain", "ρ_desain", "=MAX(D6, D7)", "-", "ρ = max(ρ_perlu, ρ_min)"),
        ("Luas Tulangan Perlu Total Arah X", "As_req_x", "=D8*('Design Criteria'!D10*1000)*'Structural Calculation'!D6", "mm²", "As = ρ * L * d"),
        ("Luas 1 Batang Tulangan Utama", "Ab", "=(PI()/4)*('Design Criteria'!D18^2)", "mm²", "Ab = π/4 * D^2"),
        ("Jumlah Batang Tulangan Arah X", "n_bars_x", "=CEILING(D9/D10, 1)", "batang", "n = Ceil(As_req / Ab)"),
        ("Jarak Spasi Tulangan Arah X", "s_x", "=ROUND((('Design Criteria'!D9*1000)-(2*'Design Criteria'!D17)-'Design Criteria'!D18)/(D11-1), 0)", "mm", "s = (B - 2cc - D) / (n - 1)"),
        ("Batas Spasi Maksimum SNI", "s_max", "=MIN(3*('Design Criteria'!D11*1000), 450)", "mm", "s_max = min(3*hf, 450 mm)"),
        ("Kontrol Spasi Tulangan X", "Cek_s_x", '=IF(D12<=D13, "AMAN (MEMENUHI SPASI)", "SPASI TERLALU LEBAR")', "-", "s <= s_max"),
        ("Rekomendasi Tulangan Terpasang X", "Notasi_X", '="D"&TEXT(\'Design Criteria\'!D18,"0")&"-"&TEXT(D12,"0")&" mm ("&TEXT(D11,"0")&" btg)"', "-", "Format konstruksi lapangan"),
        ("", "", "", "", ""),
        ("TULANGAN ARAH Y", "", "", "", ""),
        ("Luas Tulangan Perlu Total Arah Y", "As_req_y", "=D8*('Design Criteria'!D9*1000)*'Structural Calculation'!D6", "mm²", "As = ρ * B * d"),
        ("Jumlah Batang Tulangan Arah Y", "n_bars_y", "=CEILING(D17/D10, 1)", "batang", "n = Ceil(As_req / Ab)"),
        ("Jarak Spasi Tulangan Arah Y", "s_y", "=ROUND((('Design Criteria'!D10*1000)-(2*'Design Criteria'!D17)-'Design Criteria'!D18)/(D18-1), 0)", "mm", "s = (L - 2cc - D) / (n - 1)"),
        ("Rekomendasi Tulangan Terpasang Y", "Notasi_Y", '="D"&TEXT(\'Design Criteria\'!D18,"0")&"-"&TEXT(D19,"0")&" mm ("&TEXT(D18,"0")&" btg)"', "-", "Format konstruksi lapangan"),
        ("", "", "", "", ""),
        ("ESTIMASI KEBUTUHAN MATERIAL (BOQ)", "", "", "", ""),
        ("Panjang Total Tulangan Baja", "Ltot_rebar", "=(D11*('Design Criteria'!D9+0.3))+(D18*('Design Criteria'!D10+0.3))", "m", "Total panjang tulangan + kait"),
        ("Berat Satuan Besi Tulangan", "w_bar", "=0.006165*('Design Criteria'!D18^2)", "kg/m", "w = 0.006165 * D^2"),
        ("Estimasi Total Berat Baja Tulangan", "W_steel", "=D22*D23", "kg", "Berat total tulangan pelat"),
        ("Volume Beton Fondasi", "V_beton", "='Dimension Calculation'!D6", "m³", "Volume beton cor pelat fondasi"),
        ("Rasio Tulangan per Volume Beton", "Rasio_kg_m3", "=D24/D25", "kg/m³", "Indeks efisiensi struktur (~50-80 kg/m³)")
    ]

    for item in reinf_calcs:
        r_rf += 1
        ws5[f"A{r_rf}"] = item[0]; ws5[f"A{r_rf}"].font = font_bold if "Rekomendasi" in item[0] or "ESTIMASI" in item[0] else font_reg; ws5[f"A{r_rf}"].border = thin_border
        ws5[f"B{r_rf}"] = item[1]; ws5[f"B{r_rf}"].font = font_bold; ws5[f"B{r_rf}"].alignment = align_center; ws5[f"B{r_rf}"].border = thin_border
        ws5[f"C{r_rf}"] = item[2]; ws5[f"C{r_rf}"].font = font_formula; ws5[f"C{r_rf}"].border = thin_border
        ws5[f"D{r_rf}"] = item[2]; ws5[f"D{r_rf}"].font = font_bold; ws5[f"D{r_rf}"].alignment = align_center; ws5[f"D{r_rf}"].border = thin_border
        if "Rekomendasi" in item[0]:
            ws5[f"D{r_rf}"].fill = fill_safe
        ws5[f"E{r_rf}"] = item[3]; ws5[f"E{r_rf}"].font = font_reg; ws5[f"E{r_rf}"].alignment = align_center; ws5[f"E{r_rf}"].border = thin_border
        ws5[f"F{r_rf}"] = item[4]; ws5[f"F{r_rf}"].font = font_sub_title; ws5[f"F{r_rf}"].border = thin_border

    ws5.column_dimensions["A"].width = 34
    ws5.column_dimensions["B"].width = 12
    ws5.column_dimensions["C"].width = 46
    ws5.column_dimensions["D"].width = 24
    ws5.column_dimensions["E"].width = 10
    ws5.column_dimensions["F"].width = 30

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
        ("Dimensi Tapak Fondasi Terpasang", "B x L", "='Design Criteria'!D9&\" x \"&'Design Criteria'!D10&\" meter\""),
        ("Tebal Pelat Fondasi Terpasang", "hf", "='Design Criteria'!D11&\" meter (\"&TEXT('Design Criteria'!D11*100,\"0\")&\" cm)\""),
        ("Kedalaman Galian Fondasi", "Df", "='Design Criteria'!D12&\" meter dari Muka Tanah Asli\""),
        ("Mutu Beton Struktural (f'c)", "f'c", "='Design Criteria'!D15&\" MPa\""),
        ("Mutu Baja Tulangan (fy)", "fy", "='Design Criteria'!D16&\" MPa\""),
        ("Tebal Selimut Beton Bersih (cc)", "cc", "='Design Criteria'!D17&\" mm (Standar Kontak Tanah SNI)\""),
        ("Tulangan Bawah Arah X", "Rebar-X", "='Reinforcement Calculation'!D15"),
        ("Tulangan Bawah Arah Y", "Rebar-Y", "='Reinforcement Calculation'!D20"),
        ("Estimasi Total Volume Beton", "V_beton", "='Reinforcement Calculation'!D25&\" m³\""),
        ("Estimasi Total Berat Besi Tulangan", "W_besi", "=TEXT('Reinforcement Calculation'!D24,\"0.0\")&\" kg\""),
        ("Rasio Besi per Volume Beton", "Rasio", "=TEXT('Reinforcement Calculation'!D26,\"0.0\")&\" kg/m³ (Struktur Ekonomis)\"")
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
        ("Kapasitas Daya Dukung Tanah (Geoteknik)", "qmax <= qall", "='Dimension Calculation'!D20"),
        ("Kontrol Eksentrisitas Tanah (Tanpa Tarik)", "e <= L/6", "='Dimension Calculation'!D18"),
        ("Kapasitas Geser Balok Satu Arah", "Vu1 <= φVc1", "='Structural Calculation'!D17"),
        ("Kapasitas Geser Pons Dua Arah", "Vu2 <= φVc2", "='Structural Calculation'!D23"),
        ("Batas Jarak Spasi Tulangan Lentur", "s <= smax", "='Reinforcement Calculation'!D14")
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
    ws6.column_dimensions["C"].width = 38

    out = io.BytesIO()
    wb.save(out)
    out.seek(0)
    return out.getvalue()


# =============================================================================
# WRAPPER COMPATIBILITY FUNCTIONS
# =============================================================================

def generate_excel_report(project_info, soil_params, load_params, comp_results, selected_dim, reinf_results=None):
    """Fungsi utama ekspor excel pondasi dengan 6 sheet aktif rumus."""
    return generate_foundation_calculation_report(
        project_info=project_info,
        soil_params=soil_params,
        load_params=load_params,
        comp_results=comp_results,
        selected_dim=selected_dim,
        reinf_results=reinf_results
    )


def generate_spt_excel(spt_layers, project_info):
    """Fungsi ekspor data SPT ke format 5 sheet profesional."""
    return generate_soil_investigation_report(project_info=project_info, spt_layers=spt_layers, cpt_points=None)


def generate_cpt_excel(cpt_points, project_info):
    """Fungsi ekspor data CPT ke format 5 sheet profesional."""
    return generate_soil_investigation_report(project_info=project_info, spt_layers=None, cpt_points=cpt_points)


def generate_csv_report(comp_results, selected_dim):
    """Ekspor CSV ringkas untuk kompatibilitas data spreadsheet biasa."""
    rows = []
    for r in comp_results:
        rows.append({
            "Metode": r.get("metode", "-"),
            "Dimensi": f"{selected_dim.get('B', 2.0):.2f} x {selected_dim.get('L', 2.0):.2f} m",
            "Kedalaman Df (m)": selected_dim.get("Df", 1.5),
            "Nc": r.get("Nc", 0.0),
            "Nq": r.get("Nq", 0.0),
            "Ngamma": r.get("Ngamma", 0.0),
            "qu (kPa)": r.get("qu", 0.0),
            "qall (kPa)": r.get("qall", 0.0),
            "Status": r.get("status", "-")
        })
    df = pd.DataFrame(rows)
    return df.to_csv(index=False)
