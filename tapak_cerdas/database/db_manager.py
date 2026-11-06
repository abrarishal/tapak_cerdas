"""
=============================================================================
TAPAK CERDAS - DATABASE & MANAJEMEN RIWAYAT PROYEK & KOTAK MASUK KLIEN
=============================================================================
File: database/db_manager.py
Deskripsi: Menyimpan, memuat, dan mengelola riwayat proyek perencanaan
           serta merekap data pengajuan pengguna lain (klien) ke Excel & JSON.
=============================================================================
"""

import json
import os
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from datetime import datetime

DB_DIR = os.path.dirname(__file__)
PROJECTS_FILE = os.path.join(DB_DIR, "projects.json")
SUBMISSIONS_FILE = os.path.join(DB_DIR, "data_pengguna_masuk.json")
SUBMISSIONS_EXCEL = os.path.join(DB_DIR, "Rekap_Data_Pengguna_Masuk.xlsx")


def load_all_projects():
    """Memuat semua proyek yang pernah disimpan."""
    if not os.path.exists(PROJECTS_FILE):
        return []
    try:
        with open(PROJECTS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def save_project(project_data):
    """Menyimpan atau memperbarui data proyek."""
    projects = load_all_projects()
    project_data["saved_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    existing_idx = next((i for i, p in enumerate(projects) if p.get("name") == project_data.get("name")), None)
    if existing_idx is not None:
        projects[existing_idx] = project_data
    else:
        projects.insert(0, project_data)
        
    with open(PROJECTS_FILE, "w", encoding="utf-8") as f:
        json.dump(projects, f, indent=2, ensure_ascii=False)
        
    return True


def delete_project(project_name):
    """Menghapus proyek dari database berdasarkan nama."""
    projects = load_all_projects()
    projects = [p for p in projects if p.get("name") != project_name]
    with open(PROJECTS_FILE, "w", encoding="utf-8") as f:
        json.dump(projects, f, indent=2, ensure_ascii=False)
    return True


# =========================================================================
# MANAJEMEN KOTAK MASUK KLIEN (DATA PENGGUNA LAIN YANG MENGISI)
# =========================================================================

def load_client_submissions():
    """Memuat semua data yang dikirimkan oleh pengguna/klien lain."""
    if not os.path.exists(SUBMISSIONS_FILE):
        return []
    try:
        with open(SUBMISSIONS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def save_client_submission(submission_data):
    """
    Menyimpan data pengajuan desain dari pengguna lain ke JSON dan otomatis
    membuat/memperbarui file master Excel 'Rekap_Data_Pengguna_Masuk.xlsx'.
    """
    subs = load_client_submissions()
    submission_data["submitted_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    submission_data["id"] = f"SUB-{len(subs) + 1:04d}"
    
    subs.insert(0, submission_data)
    
    with open(SUBMISSIONS_FILE, "w", encoding="utf-8") as f:
        json.dump(subs, f, indent=2, ensure_ascii=False)
        
    # Sinkronisasi ke Excel Master
    generate_submissions_excel(subs, SUBMISSIONS_EXCEL)
    return submission_data["id"]


def generate_submissions_excel(submissions_list, output_filepath):
    """
    Menghasilkan file Excel master yang rapi berisi seluruh data pengguna masuk.
    """
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Rekap Pengguna Masuk"
    
    # Styling
    navy_header_fill = PatternFill(start_color="0F172A", end_color="0F172A", fill_type="solid")
    header_font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
    data_font = Font(name="Calibri", size=10)
    thin_border = Border(
        left=Side(style='thin', color='CBD5E1'),
        right=Side(style='thin', color='CBD5E1'),
        top=Side(style='thin', color='CBD5E1'),
        bottom=Side(style='thin', color='CBD5E1')
    )
    
    # Judul Dokumen
    ws.merge_cells("A1:M1")
    ws["A1"] = "TAPAK CERDAS - REKAPITULASI DATA PERENCANAAN DARI PENGGUNA LAIN"
    ws["A1"].font = Font(name="Calibri", size=14, bold=True, color="1E3A8A")
    ws["A1"].alignment = Alignment(horizontal="center", vertical="center")
    
    headers = [
        "No", "ID", "Waktu Pengiriman", "Nama Pengguna/Klien", "No WhatsApp",
        "Nama Proyek & Lokasi", "Fungsi Bangunan", "Beban Kolom P (kN)",
        "Dimensi Rencana B x L x Df (m)", "Kohesi c (kPa)", "Sudut Geser φ (°)",
        "SF Terendah", "Status Kelayakan"
    ]
    
    ws.append([]) # Baris kosong ke-2
    ws.append(headers)
    
    for col_idx in range(1, len(headers) + 1):
        cell = ws.cell(row=3, column=col_idx)
        cell.fill = navy_header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        cell.border = thin_border
        
    for idx, s in enumerate(submissions_list, start=1):
        row_vals = [
            idx,
            s.get("id", ""),
            s.get("submitted_at", ""),
            s.get("client_name", "-"),
            s.get("client_wa", "-"),
            f"{s.get('project_name', '')} ({s.get('location', '')})",
            s.get("building_function", "-"),
            s.get("p_column", 0.0),
            f"{s.get('width_b', 0.0)} x {s.get('length_l', 0.0)} x {s.get('depth_df', 0.0)}",
            s.get("cohesion", 0.0),
            s.get("friction_angle", 0.0),
            s.get("min_sf", 0.0),
            s.get("status", "AMAN")
        ]
        ws.append(row_vals)
        r_num = ws.max_row
        for c_idx in range(1, len(headers) + 1):
            cell = ws.cell(row=r_num, column=c_idx)
            cell.font = data_font
            cell.border = thin_border
            if c_idx in [1, 2, 3, 5, 12, 13]:
                cell.alignment = Alignment(horizontal="center", vertical="center")
            elif c_idx in [8, 9, 10, 11]:
                cell.alignment = Alignment(horizontal="right", vertical="center")
            else:
                cell.alignment = Alignment(horizontal="left", vertical="center")
                
    # Auto-adjust column width
    for col in ws.columns:
        max_len = max(len(str(cell.value or '')) for cell in col)
        col_letter = openpyxl.utils.get_column_letter(col[0].column)
        ws.column_dimensions[col_letter].width = max(max_len + 3, 12)
        
    wb.save(output_filepath)
    return output_filepath
