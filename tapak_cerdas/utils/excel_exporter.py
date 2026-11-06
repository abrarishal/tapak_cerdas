"""
=============================================================================
TAPAK CERDAS - GENERATOR EKSPOR EXCEL & CSV RESMI
=============================================================================
File: utils/excel_exporter.py
Deskripsi: Mengekspor rekapitulasi data proyek, pembebanan SNI 1727:2020,
           data tanah, komparasi perhitungan 4 metode (Terzaghi, Meyerhof,
           Vesic, Hansen), serta rekomendasi pondasi ke format .xlsx & .csv.
=============================================================================
"""

import io
import pandas as pd
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

def _clean_num(val):
    if isinstance(val, (int, float)):
        return float(val)
    if isinstance(val, str):
        try:
            return float(val.replace(',', '').replace(' ', ''))
        except Exception:
            return 0.0
    return 0.0

def generate_excel_report(project_info, soil_params, load_params, comp_results, selected_dim):
    """
    Menghasilkan berkas Excel (.xlsx) multihalaman yang rapi, profesional,
    dan berstandar rekayasa teknik sipil.
    """
    wb = openpyxl.Workbook()
    
    # Style Definitions
    font_title = Font(name="Calibri", size=16, bold=True, color="1E3A8A")
    font_section = Font(name="Calibri", size=12, bold=True, color="0F172A")
    font_header = Font(name="Calibri", size=10, bold=True, color="FFFFFF")
    font_regular = Font(name="Calibri", size=10)
    font_bold = Font(name="Calibri", size=10, bold=True)
    
    fill_header = PatternFill(start_color="1E3A8A", end_color="1E3A8A", fill_type="solid")
    fill_sub_header = PatternFill(start_color="3B82F6", end_color="3B82F6", fill_type="solid")
    fill_zebra = PatternFill(start_color="F8FAFC", end_color="F8FAFC", fill_type="solid")
    fill_safe = PatternFill(start_color="DCFCE7", end_color="DCFCE7", fill_type="solid")
    fill_danger = PatternFill(start_color="FEE2E2", end_color="FEE2E2", fill_type="solid")
    
    font_safe = Font(name="Calibri", size=10, bold=True, color="15803D")
    font_danger = Font(name="Calibri", size=10, bold=True, color="B91C1C")
    
    thin_border = Border(
        left=Side(style='thin', color='CBD5E1'),
        right=Side(style='thin', color='CBD5E1'),
        top=Side(style='thin', color='CBD5E1'),
        bottom=Side(style='thin', color='CBD5E1')
    )
    
    align_center = Alignment(horizontal='center', vertical='center')
    align_left = Alignment(horizontal='left', vertical='center')
    align_right = Alignment(horizontal='right', vertical='center')

    # ==========================================
    # SHEET 1: RINGKASAN & PEMBEBANAN BANGUNAN
    # ==========================================
    ws1 = wb.active
    ws1.title = "Ringkasan & Beban SNI"
    
    ws1["A1"] = "LAPORAN PERENCANAAN AWAL PONDASI TELAPAK - TAPAK CERDAS"
    ws1["A1"].font = font_title
    
    ws1["A3"] = "1. IDENTITAS PROYEK & KONDISI TANAH"
    ws1["A3"].font = font_section
    
    meta_data = [
        ("Nama Proyek", project_info.get("name", "-")),
        ("Lokasi Proyek", project_info.get("location", "-")),
        ("Jenis Tanah Dasar", soil_params.get("soil_type", "-")),
        ("Kohesi Tanah (c)", f"{soil_params.get('cohesion', 0.0)} kPa"),
        ("Sudut Geser Dalam (φ)", f"{soil_params.get('friction_angle', 0.0)}°"),
        ("Berat Isi Tanah (γ)", f"{soil_params.get('unit_weight', 17.5)} kN/m³"),
        ("Muka Air Tanah (dw)", f"{project_info.get('water_table_depth', 1.5)} m dari muka tanah")
    ]
    
    r = 4
    for label, val in meta_data:
        ws1[f"A{r}"] = label
        ws1[f"A{r}"].font = font_bold
        ws1[f"B{r}"] = val
        ws1[f"B{r}"].font = font_regular
        r += 1
        
    r += 1
    ws1[f"A{r}"] = "2. ESTIMASI BEBAN GEDUNG (SNI 1727:2020)"
    ws1[f"A{r}"].font = font_section
    r += 1
    
    load_data = [
        ("Fungsi Bangunan", load_params.get("building_function", "-")),
        ("Jumlah Lantai", f"{load_params.get('floors', 1)} Lantai"),
        ("Luas Lantai per Lantai", f"{load_params.get('floor_area', 100.0)} m²"),
        ("Estimasi Beban Mati (DL)", f"{load_params.get('dead_load_unit', 7.85)} kN/m²"),
        ("Beban Hidup SNI (LL)", f"{load_params.get('live_load_unit', 1.92)} kN/m²"),
        ("Beban Kolom Rencana (P)", f"{load_params.get('p_column', 0.0):,.1f} kN (~{load_params.get('p_column', 0.0)/9.81:,.1f} Ton)"),
        ("Beban Kolom Terfaktor (Pu)", f"{load_params.get('pu_column', 0.0):,.1f} kN (Kombinasi 1.2D + 1.6L)")
    ]
    
    for label, val in load_data:
        ws1[f"A{r}"] = label
        ws1[f"A{r}"].font = font_bold
        ws1[f"B{r}"] = val
        ws1[f"B{r}"].font = font_regular
        r += 1

    # ==========================================
    # SHEET 2: KOMPARASI 4 METODE DAYA DUKUNG
    # ==========================================
    ws2 = wb.create_sheet(title="Komparasi 4 Metode")
    
    ws2["A1"] = "HASIL KOMPARASI PERHITUNGAN DAYA DUKUNG 4 METODE GEOTEKNIK"
    ws2["A1"].font = font_title
    
    dim_str = f"Dimensi Rencana: B = {selected_dim['B']:.2f} m | L = {selected_dim['L']:.2f} m | Df = {selected_dim['Df']:.2f} m | Target SF = {selected_dim['SF']}"
    ws2["A2"] = dim_str
    ws2["A2"].font = font_bold
    
    headers = [
        "Metode Geoteknik", "Nc", "Nq", "Nγ", 
        "qu Ultimit (kPa)", "qall Izin (kPa)", 
        "q Kontak (kPa)", "SF Aktual", "Status Evaluasi"
    ]
    
    row_idx = 4
    for col_idx, h in enumerate(headers, 1):
        cell = ws2.cell(row=row_idx, column=col_idx, value=h)
        cell.font = font_header
        cell.fill = fill_header
        cell.alignment = align_center
        cell.border = thin_border
        
    for res in comp_results:
        row_idx += 1
        is_safe = ("AMAN" in res["status"] or "OK" in res["status"])
        
        row_values = [
            res.get("metode", "-"),
            res.get("Nc", 0.0),
            res.get("Nq", 0.0),
            res.get("Ngamma", 0.0),
            f"{_clean_num(res.get('qu', 0.0)):.1f}",
            f"{_clean_num(res.get('qall', 0.0)):.1f}",
            f"{_clean_num(res.get('q_kontak', 0.0)):.1f}",
            f"{_clean_num(res.get('sf_aktual', 0.0)):.2f}",
            "AMAN (Lolos)" if is_safe else "OVERSTRESSED"
        ]
        
        for col_idx, val in enumerate(row_values, 1):
            cell = ws2.cell(row=row_idx, column=col_idx, value=val)
            cell.font = font_regular
            cell.border = thin_border
            cell.alignment = align_left if col_idx == 1 else align_center
            
            # Format status khusus
            if col_idx == 9:
                cell.fill = fill_safe if is_safe else fill_danger
                cell.font = font_safe if is_safe else font_danger

    # Auto-adjust column width
    for ws in [ws1, ws2]:
        for col in ws.columns:
            max_len = max(len(str(cell.value or '')) for cell in col)
            col_letter = get_column_letter(col[0].column)
            ws.column_dimensions[col_letter].width = max(max_len + 3, 14)

    # Save to buffer
    output = io.BytesIO()
    wb.save(output)
    output.seek(0)
    return output.getvalue()


def generate_csv_report(comp_results, selected_dim):
    """
    Menghasilkan data teks CSV ringkasan 4 metode.
    """
    df = pd.DataFrame(comp_results)
    df["B (m)"] = selected_dim["B"]
    df["L (m)"] = selected_dim["L"]
    df["Df (m)"] = selected_dim["Df"]
    return df.to_csv(index=False)


def generate_spt_excel(spt_layers, project_info):
    """
    Mengekspor data penyelidikan SPT dan formasi lapisan tanah ke format Excel resmi.
    """
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Bore Log SPT"
    
    font_title = Font(name="Calibri", size=14, bold=True, color="1E3A8A")
    font_header = Font(name="Calibri", size=10, bold=True, color="FFFFFF")
    font_bold = Font(name="Calibri", size=10, bold=True)
    font_reg = Font(name="Calibri", size=10)
    fill_header = PatternFill(start_color="1E3A8A", end_color="1E3A8A", fill_type="solid")
    thin_border = Border(
        left=Side(style='thin', color='CBD5E1'),
        right=Side(style='thin', color='CBD5E1'),
        top=Side(style='thin', color='CBD5E1'),
        bottom=Side(style='thin', color='CBD5E1')
    )
    align_center = Alignment(horizontal='center', vertical='center')
    align_left = Alignment(horizontal='left', vertical='center')
    
    ws["A1"] = "BORE LOG - PENYELIDIKAN TANAH BORING & N-SPT (ASTM D1586)"
    ws["A1"].font = font_title
    
    ws["A3"] = "Nama Proyek:"
    ws["B3"] = project_info.get("name", "Proyek Bangunan")
    ws["A4"] = "Lokasi:"
    ws["B4"] = project_info.get("location", "Semarang")
    ws["A5"] = "Titik Bor:"
    ws["B5"] = project_info.get("borehole_id", "BH-01")
    ws["A6"] = "Muka Air Tanah (MAT):"
    ws["B6"] = f"{float(project_info.get('water_table_depth', 1.5)):.2f} meter"
    
    for r in range(3, 7):
        ws[f"A{r}"].font = font_bold
        ws[f"B{r}"].font = font_reg
        
    headers = [
        "No", "Kedalaman (m)", "Tebal (m)", "N1 (15cm)", "N2 (15cm)", "N3 (15cm)",
        "N-SPT (N2+N3)", "Konsistensi", "Tipe Tanah", "Deskripsi Lapangan",
        "Kohesi c (kPa)", "Sudut Geser φ (°)", "Berat Isi γ (kN/m³)"
    ]
    
    start_row = 8
    for col_idx, h in enumerate(headers, 1):
        cell = ws.cell(row=start_row, column=col_idx, value=h)
        cell.font = font_header
        cell.fill = fill_header
        cell.alignment = align_center
        cell.border = thin_border
        
    for idx, lyr in enumerate(spt_layers, 1):
        r_num = start_row + idx
        thick = round(lyr.get("depth_bot", 0.0) - lyr.get("depth_top", 0.0), 2)
        row_vals = [
            idx,
            lyr.get("interval_str", f"{lyr.get('depth_top', 0):.2f} - {lyr.get('depth_bot', 0):.2f} m"),
            thick,
            lyr.get("n1", 0),
            lyr.get("n2", 0),
            lyr.get("n3", 0),
            lyr.get("n_spt", 0),
            lyr.get("konsistensi", "-"),
            lyr.get("soil_type", "Tanah"),
            lyr.get("deskripsi", "-"),
            lyr.get("c", 0.0),
            lyr.get("phi", 0.0),
            lyr.get("gamma", 17.5)
        ]
        for c_idx, v in enumerate(row_vals, 1):
            cell = ws.cell(row=r_num, column=c_idx, value=v)
            cell.font = font_reg
            cell.border = thin_border
            cell.alignment = align_left if c_idx in [2, 9, 10] else align_center
            
    for col in ws.columns:
        max_len = max(len(str(c.value or '')) for c in col)
        col_letter = get_column_letter(col[0].column)
        ws.column_dimensions[col_letter].width = max(max_len + 3, 11)
        
    out = io.BytesIO()
    wb.save(out)
    out.seek(0)
    return out.getvalue()


def generate_cpt_excel(cpt_points, project_info):
    """
    Mengekspor data uji sondir CPT bikonus 2.5 ton ke format Excel resmi.
    """
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Hasil Uji Sondir CPT"
    
    font_title = Font(name="Calibri", size=14, bold=True, color="065F46")
    font_header = Font(name="Calibri", size=10, bold=True, color="FFFFFF")
    font_bold = Font(name="Calibri", size=10, bold=True)
    font_reg = Font(name="Calibri", size=10)
    fill_header = PatternFill(start_color="065F46", end_color="065F46", fill_type="solid")
    thin_border = Border(
        left=Side(style='thin', color='CBD5E1'),
        right=Side(style='thin', color='CBD5E1'),
        top=Side(style='thin', color='CBD5E1'),
        bottom=Side(style='thin', color='CBD5E1')
    )
    align_center = Alignment(horizontal='center', vertical='center')
    align_left = Alignment(horizontal='left', vertical='center')
    
    ws["A1"] = "HASIL UJI PENETRASI KONUS / SONDIR (CPT BIKONUS 2.5 TON)"
    ws["A1"].font = font_title
    
    ws["A3"] = "Nama Proyek:"
    ws["B3"] = project_info.get("name", "Proyek Bangunan")
    ws["A4"] = "Lokasi:"
    ws["B4"] = project_info.get("location", "Semarang")
    ws["A5"] = "Titik Sondir:"
    ws["B5"] = "S-01 (Kapasitas 2.5 Ton)"
    ws["A6"] = "Muka Air Tanah (MAT):"
    ws["B6"] = f"{float(project_info.get('water_table_depth', 1.5)):.2f} meter"
    
    for r in range(3, 7):
        ws[f"A{r}"].font = font_bold
        ws[f"B{r}"].font = font_reg
        
    headers = [
        "No", "Kedalaman (m)", "qc (kg/cm²)", "JH (kg/cm²)", "HP (kg/cm)",
        "JHP Total (kg/cm)", "HS / fs (kg/cm²)", "Rasio Gesek FR (%)",
        "Klasifikasi Tanah (Robertson 1986)"
    ]
    
    start_row = 8
    for col_idx, h in enumerate(headers, 1):
        cell = ws.cell(row=start_row, column=col_idx, value=h)
        cell.fill = fill_header
        cell.font = font_header
        cell.alignment = align_center
        cell.border = thin_border
        
    for idx, pt in enumerate(cpt_points, 1):
        r_num = start_row + idx
        row_vals = [
            idx,
            round(pt.get("depth", 0.0), 2),
            round(pt.get("qc", 0.0), 1),
            round(pt.get("jh", 0.0), 1),
            round(pt.get("hp", 0.0), 1),
            round(pt.get("jhp", 0.0), 1),
            round(pt.get("hs", 0.0), 3),
            round(pt.get("fr", 0.0), 2),
            pt.get("soil_type", "-")
        ]
        for c_idx, v in enumerate(row_vals, 1):
            cell = ws.cell(row=r_num, column=c_idx, value=v)
            cell.font = font_reg
            cell.border = thin_border
            cell.alignment = align_left if c_idx == 9 else align_center
            
    for col in ws.columns:
        max_len = max(len(str(c.value or '')) for c in col)
        col_letter = get_column_letter(col[0].column)
        ws.column_dimensions[col_letter].width = max(max_len + 3, 12)
        
    out = io.BytesIO()
    wb.save(out)
    out.seek(0)
    return out.getvalue()
