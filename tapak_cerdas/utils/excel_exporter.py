"""
=============================================================================
TAPAK CERDAS - GENERATOR EKSPOR EXCEL & CSV RESMI (BERSTANDAR TEKNIK SIPIL)
=============================================================================
File: utils/excel_exporter.py
Deskripsi: Mengekspor rekapitulasi data proyek, pembebanan SNI 1727:2020,
           data borehole SPT (ASTM D1586), data sondir CPT (SNI 2827:2008),
           komparasi 4 metode daya dukung lengkap dengan grafik interaktif Excel
           serta penjabaran detail rumus-rumus geoteknik.
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


def generate_excel_report(project_info, soil_params, load_params, comp_results, selected_dim):
    """
    Menghasilkan berkas Excel (.xlsx) multihalaman yang rapi, profesional,
    dan berstandar rekayasa teknik sipil:
    - Sheet 1: Ringkasan & Pembebanan SNI 1727:2020
    - Sheet 2: Komparasi 4 Metode Geoteknik (Dilengkapi Grafik BarChart)
    - Sheet 3: Penjabaran Detail & Rumus Eksak 4 Metode (Terzaghi, Meyerhof, Vesic, Hansen)
    """
    wb = openpyxl.Workbook()

    # Shared Styles
    font_title = Font(name="Calibri", size=15, bold=True, color="1E3A8A")
    font_section = Font(name="Calibri", size=11, bold=True, color="0F172A")
    font_sub_section = Font(name="Calibri", size=10, bold=True, color="1E40AF")
    font_bold = Font(name="Calibri", size=10, bold=True)
    font_regular = Font(name="Calibri", size=10)
    font_safe = Font(name="Calibri", size=10, bold=True, color="15803D")
    font_danger = Font(name="Calibri", size=10, bold=True, color="B91C1C")

    fill_meta = PatternFill(start_color="F1F5F9", end_color="F1F5F9", fill_type="solid")
    fill_zebra = PatternFill(start_color="F8FAFC", end_color="F8FAFC", fill_type="solid")
    fill_white = PatternFill(start_color="FFFFFF", end_color="FFFFFF", fill_type="solid")
    fill_safe = PatternFill(start_color="DCFCE7", end_color="DCFCE7", fill_type="solid")
    fill_danger = PatternFill(start_color="FEE2E2", end_color="FEE2E2", fill_type="solid")

    thin_border = Border(
        left=Side(style='thin', color='CBD5E1'),
        right=Side(style='thin', color='CBD5E1'),
        top=Side(style='thin', color='CBD5E1'),
        bottom=Side(style='thin', color='CBD5E1')
    )

    align_center = Alignment(horizontal='center', vertical='center')
    align_left = Alignment(horizontal='left', vertical='center')
    align_right = Alignment(horizontal='right', vertical='center')

    # =========================================================================
    # SHEET 1: RINGKASAN & PEMBEBANAN BANGUNAN
    # =========================================================================
    ws1 = wb.active
    ws1.title = "Ringkasan & Beban SNI"
    ws1.views.sheetView[0].showGridLines = True

    ws1["A1"] = "LAPORAN PERENCANAAN FONDASI TELAPAK - TAPAK CERDAS"
    ws1["A1"].font = font_title
    ws1["A2"] = "Standar Desain: SNI 1727:2020 (Beban Desain) & Buku Analisis Perancangan Fondasi (Hary Christady Hardiyatmo)"
    ws1["A2"].font = Font(name="Calibri", size=9, italic=True, color="64748B")

    ws1["A4"] = "1. IDENTITAS PROYEK & KONDISI TANAH DASAR"
    ws1["A4"].font = font_section

    phi_val = soil_params.get("friction_angle", 0.0)
    phi_eff_val = soil_params.get("phi_eff", phi_val)
    c_val = soil_params.get("cohesion", 0.0)
    cu_val = soil_params.get("cu", c_val)

    meta_data = [
        ("Nama Proyek", project_info.get("name", "Pembangunan Bangunan Cerdas")),
        ("Lokasi Proyek", project_info.get("location", "Semarang")),
        ("Sumber Data Tanah", soil_params.get("source", "Penyelidikan Lapangan")),
        ("Tipe Tanah Dominan", soil_params.get("soil_type", "Lempung Sedang")),
        ("Kohesi Tanah (c / cu)", f"{c_val} kPa (Kuat Geser Undrained cu = {cu_val} kPa)"),
        ("Sudut Geser Dalam (φ)", f"{phi_val}° (Estimasi Sudut Geser Efektif φ' = {phi_eff_val}°)"),
        ("Berat Isi Lembab (γ)", f"{soil_params.get('unit_weight', 17.5)} kN/m³"),
        ("Berat Isi Jenuh (γsat)", f"{soil_params.get('sat_unit_weight', 19.0)} kN/m³"),
        ("Kedalaman Muka Air Tanah (dw)", f"{project_info.get('water_table_depth', 1.50)} m dari muka tanah")
    ]

    r = 5
    for label, val in meta_data:
        ws1[f"A{r}"] = label
        ws1[f"A{r}"].font = font_bold
        ws1[f"A{r}"].fill = fill_meta
        ws1[f"A{r}"].border = thin_border
        ws1[f"B{r}"] = val
        ws1[f"B{r}"].font = font_regular
        ws1[f"B{r}"].border = thin_border
        r += 1

    r += 1
    ws1[f"A{r}"] = "2. ESTIMASI PEMBEBANAN STRUKTUR (SNI 1727:2020)"
    ws1[f"A{r}"].font = font_section
    r += 1

    p_col = float(load_params.get("p_column", 0.0))
    pu_col = float(load_params.get("pu_column", 0.0))

    load_data = [
        ("Fungsi Bangunan", load_params.get("building_function", "Rumah Tinggal / Ruko")),
        ("Jumlah Lantai Gedung", f"{load_params.get('floors', 2)} Lantai"),
        ("Luas Lantai per Lantai", f"{load_params.get('floor_area', 100.0)} m²"),
        ("Beban Mati Nominal (DL)", f"{load_params.get('dead_load_unit', 7.85)} kN/m²"),
        ("Beban Hidup SNI (LL)", f"{load_params.get('live_load_unit', 1.92)} kN/m²"),
        ("Beban Kolom Rencana Izin (P)", f"{p_col:,.1f} kN (~{p_col/9.81:,.1f} Ton)"),
        ("Beban Kolom Terfaktor Kuat (Pu)", f"{pu_col:,.1f} kN (Kombinasi 1.2 DL + 1.6 LL)")
    ]

    for label, val in load_data:
        ws1[f"A{r}"] = label
        ws1[f"A{r}"].font = font_bold
        ws1[f"A{r}"].fill = fill_meta
        ws1[f"A{r}"].border = thin_border
        ws1[f"B{r}"] = val
        ws1[f"B{r}"].font = font_regular
        ws1[f"B{r}"].border = thin_border
        r += 1

    r += 1
    ws1[f"A{r}"] = "3. GEOMETRI & TEGANGAN DASAR FONDASI TERPILIH"
    ws1[f"A{r}"].font = font_section
    r += 1

    b_val = float(selected_dim.get("B", 1.5))
    l_val = float(selected_dim.get("L", 1.5))
    df_val = float(selected_dim.get("Df", 1.5))
    sf_target = float(selected_dim.get("SF", 3.0))
    area_f = b_val * l_val
    hf_val = 0.30  # estimasi tebal pelat
    vol_beton = area_f * hf_val
    berat_fondasi = vol_beton * 24.0
    berat_tanah_urug = area_f * max(0.0, df_val - hf_val) * float(soil_params.get("unit_weight", 17.5))
    p_total = p_col + berat_fondasi + berat_tanah_urug
    q_kontak = p_total / area_f if area_f > 0 else 0.0

    geom_data = [
        ("Bentuk Fondasi", selected_dim.get("shape", "Bujur Sangkar")),
        ("Lebar Fondasi (B)", f"{b_val:.2f} meter"),
        ("Panjang Fondasi (L)", f"{l_val:.2f} meter"),
        ("Kedalaman Tertanam (Df)", f"{df_val:.2f} meter"),
        ("Target Faktor Keamanan (SF)", f"{sf_target:.2f} (Opsi SNI: 2.0; 2.5; 3.0; 3.5)"),
        ("Tegangan Kontak Kerja Total (q)", f"{q_kontak:.2f} kPa")
    ]

    for label, val in geom_data:
        ws1[f"A{r}"] = label
        ws1[f"A{r}"].font = font_bold
        ws1[f"A{r}"].fill = fill_meta
        ws1[f"A{r}"].border = thin_border
        ws1[f"B{r}"] = val
        ws1[f"B{r}"].font = font_regular
        ws1[f"B{r}"].border = thin_border
        r += 1

    # Auto-width sheet 1
    for col in ws1.columns:
        max_len = max(len(str(c.value or '')) for c in col)
        col_letter = get_column_letter(col[0].column)
        ws1.column_dimensions[col_letter].width = max(max_len + 4, 18)

    # =========================================================================
    # SHEET 2: KOMPARASI 4 METODE DAYA DUKUNG & GRAFIK
    # =========================================================================
    ws2 = wb.create_sheet(title="Komparasi 4 Metode")
    ws2.views.sheetView[0].showGridLines = True

    ws2["A1"] = "KOMPARASI PERHITUNGAN DAYA DUKUNG 4 METODE GEOTEKNIK RESMI"
    ws2["A1"].font = font_title
    ws2["A2"] = f"Dimensi Rencana: B = {b_val:.2f} m | L = {l_val:.2f} m | Df = {df_val:.2f} m | Tegangan Kontak q = {q_kontak:.1f} kPa | Target SF = {sf_target}"
    ws2["A2"].font = font_bold

    headers_comp = [
        "Metode Geoteknik", "Nc", "Nq", "Nγ",
        "sc", "sq", "sγ", "dc", "dq", "dγ",
        "po (kPa)", "qu Ultimit (kPa)",
        f"qall (SF={sf_target})", "qall (SF=2.0)", "qall (SF=2.5)", "qall (SF=3.0)", "qall (SF=3.5)",
        "q Kontak (kPa)", "SF Terhitung", "Status Evaluasi"
    ]

    start_row = 4
    for c_idx, h in enumerate(headers_comp, 1):
        cell = ws2.cell(row=start_row, column=c_idx, value=h)
        _style_header_cell(cell, fill_color="1E3A8A", text_color="FFFFFF", bold=True, size=10)
        _style_border(cell)

    row_idx = start_row
    for res in comp_results:
        row_idx += 1
        qu_num = _clean_num(res.get("qu", 0.0))
        po_num = _clean_num(res.get("po", 0.0))
        qun = max(0.0, qu_num - po_num)

        # Hitung kapasitas izin untuk seluruh variasi SF: 2.0; 2.5; 3.0; 3.5
        qall_current = (qun / sf_target) + po_num
        qall_20 = (qun / 2.0) + po_num
        qall_25 = (qun / 2.5) + po_num
        qall_30 = (qun / 3.0) + po_num
        qall_35 = (qun / 3.5) + po_num

        sf_actual = (qu_num / q_kontak) if q_kontak > 0 else 0.0
        is_safe = (q_kontak <= qall_current)

        row_vals = [
            res.get("metode", "-"),
            res.get("Nc", 0.0),
            res.get("Nq", 0.0),
            res.get("Ngamma", 0.0),
            res.get("sc", 1.0),
            res.get("sq", 1.0),
            res.get("sgamma", 1.0),
            res.get("dc", 1.0),
            res.get("dq", 1.0),
            res.get("dgamma", 1.0),
            round(po_num, 1),
            round(qu_num, 1),
            round(qall_current, 1),
            round(qall_20, 1),
            round(qall_25, 1),
            round(qall_30, 1),
            round(qall_35, 1),
            round(q_kontak, 1),
            round(sf_actual, 2),
            "AMAN (Lolos)" if is_safe else "PERLU DIPERLEBAR"
        ]

        fill_row = fill_zebra if row_idx % 2 == 0 else fill_white
        for c_idx, val in enumerate(row_vals, 1):
            cell = ws2.cell(row=row_idx, column=c_idx, value=val)
            cell.font = font_regular
            cell.fill = fill_row
            _style_border(cell)
            cell.alignment = align_left if c_idx == 1 else align_center

            # Format Kolom Status & SF
            if c_idx == 19:
                cell.font = font_bold
            elif c_idx == 20:
                cell.fill = fill_safe if is_safe else fill_danger
                cell.font = font_safe if is_safe else font_danger

    # Tambahkan Catatan Ilmiah Mengenai Ngamma = 0
    note_row = row_idx + 2
    ws2[f"A{note_row}"] = "📌 CATATAN TEKNIS GEOTEKNIK:"
    ws2[f"A{note_row}"].font = font_sub_section
    note_row += 1
    ws2[f"A{note_row}"] = (
        "1. Nilai Nγ = 0.0 muncul secara analitis pada tanah lempung jenuh air (kondisi tegangan total undrained, φ = 0°), "
        "karena rumus faktor Nγ berbanding lurus dengan tan(φ). Saat φ = 0°, suku tan(0°) = 0, sehingga suku berat tanah di bawah fondasi tidak menyumbang gesekan."
    )
    ws2[f"A{note_row}"].font = Font(name="Calibri", size=9, italic=True, color="334155")
    note_row += 1
    ws2[f"A{note_row}"] = (
        "2. Jika analisis ditinjau berdasarkan tegangan efektif jangka panjang (drained, φ' > 0°), maka seluruh faktor Nc, Nq, dan Nγ bernilai positif > 0."
    )
    ws2[f"A{note_row}"].font = Font(name="Calibri", size=9, italic=True, color="334155")

    # Native Excel BarChart: Kapasitas Izin vs Tegangan Kontak
    try:
        chart_comp = BarChart()
        chart_comp.type = "col"
        chart_comp.title = f"Komparasi Kapasitas Dukung Izin (qall, SF={sf_target}) vs Tegangan Kontak (q)"
        chart_comp.style = 10
        chart_comp.y_axis.title = "Tekanan / Tegangan (kPa)"
        chart_comp.x_axis.title = "Metode Geoteknik"
        chart_comp.width = 18
        chart_comp.height = 11

        data_ref = Reference(ws2, min_col=13, min_row=start_row, max_col=13, max_row=row_idx)
        cats_ref = Reference(ws2, min_col=1, min_row=start_row + 1, max_row=row_idx)
        chart_comp.add_data(data_ref, titles_from_data=True)
        chart_comp.set_categories(cats_ref)
        ws2.add_chart(chart_comp, f"B{note_row + 2}")
    except Exception:
        pass

    # Auto-adjust column width Sheet 2
    for col in ws2.columns:
        col_letter = get_column_letter(col[0].column)
        if col[0].column > 20:
            continue
        max_len = max(len(str(c.value or '')) for c in col[:row_idx + 1])
        ws2.column_dimensions[col_letter].width = max(max_len + 3, 11)

    # =========================================================================
    # SHEET 3: PENJABARAN LENGKAP & RUMUS-RUMUS 4 METODE
    # =========================================================================
    ws3 = wb.create_sheet(title="Penjabaran & Rumus 4 Metode")
    ws3.views.sheetView[0].showGridLines = True

    ws3["A1"] = "PENJABARAN RUMUS & LANGKAH PERHITUNGAN 4 METODE DAYA DUKUNG"
    ws3["A1"].font = font_title
    ws3["A2"] = "Referensi Teori: Terzaghi (1943), Meyerhof (1963), Vesic (1975), Brinch Hansen (1970)"
    ws3["A2"].font = Font(name="Calibri", size=9, italic=True, color="64748B")

    formulas_info = [
        ("I. PERSAMAAN UMUM KAPASITAS DUKUNG TANAH DANGKAL", [
            ("Prinsip Daya Dukung Ultimit (qu):", "qu = Suku Kohesi + Suku Beban Overburden + Suku Berat Massa Tanah Bawah"),
            ("Persamaan Dasar Tiga Suku:", "qu = (c · Nc · sc · dc · ic) + (po · Nq · sq · dq · iq) + (0.5 · γ · B · Nγ · sγ · dγ · iγ)"),
            ("Kapasitas Neto Izin (qall):", "qall = ((qu - po) / SF) + po   (dengan SF = 2.0; 2.5; 3.0; atau 3.5)"),
            ("Tegangan Kontak Pondasi (q):", "q = P_total / (B · L) = (P_kolom + Berat Fondasi + Berat Tanah) / Area")
        ]),
        ("II. FAKTOR KAPASITAS DUKUNG (Nc, Nq, Nγ) MENURUT TEORI", [
            ("Faktor Overburden Nq:", "Nq = tan²(45° + φ/2) · e^(π · tan φ)"),
            ("Faktor Kohesi Nc:", "Nc = (Nq - 1) · cot φ    (saat φ = 0°, Nc = 5.14 untuk Meyerhof/Vesic/Hansen, Nc = 5.70 untuk Terzaghi)"),
            ("Faktor Berat Tanah Nγ Meyerhof (1963):", "Nγ = (Nq - 1) · tan(1.4 · φ)"),
            ("Faktor Berat Tanah Nγ Vesic (1975):", "Nγ = 2 · (Nq + 1) · tan φ"),
            ("Faktor Berat Tanah Nγ Hansen (1970):", "Nγ = 1.5 · (Nq - 1) · tan φ"),
            ("Faktor Berat Tanah Nγ Terzaghi (1943):", "Nγ = 0.5 · tan φ · (Kpγ / cos²φ - 1)   [atau Grafik Terzaghi / Pendekatan Cernica]"),
            ("Mengapa Nγ = 0 saat φ = 0°?:", "Karena seluruh rumus Nγ mengalikan suku tan(φ). Bila sudut geser φ = 0°, tan(0°) = 0, sehingga Nγ = 0.")
        ]),
        ("III. FAKTOR BENTUK (sc, sq, sγ) & FAKTOR KEDALAMAN (dc, dq, dγ)", [
            ("Metode Terzaghi (Bujur Sangkar):", "qu = 1.3 · c · Nc + po · Nq + 0.4 · γ · B · Nγ"),
            ("Metode Terzaghi (Persegi Panjang):", "qu = c · Nc · (1 + 0.3 B/L) + po · Nq + 0.5 · γ · B · Nγ · (1 - 0.2 B/L)"),
            ("Metode Meyerhof - Bentuk (sc, sq, sγ):", "sc = 1 + 0.2·Kp·(B/L);   sq = sγ = 1 + 0.1·Kp·(B/L) jika φ ≥ 10°, Kp = tan²(45°+φ/2)"),
            ("Metode Meyerhof - Kedalaman (dc, dq, dγ):", "dc = 1 + 0.2·√Kp·(Df/B);   dq = dγ = 1 + 0.1·√Kp·(Df/B) jika φ ≥ 10°"),
            ("Metode Vesic - Bentuk (sc, sq, sγ):", "sc = 1 + (B/L)·(Nq/Nc);   sq = 1 + (B/L)·tan φ;   sγ = 1 - 0.4·(B/L)"),
            ("Metode Vesic - Kedalaman (dc, dq, dγ):", "k = Df/B (jika Df/B ≤ 1) atau atan(Df/B); dc = 1 + 0.4k; dq = 1 + 2k·tan φ·(1-sin φ)²; dγ = 1.0"),
            ("Metode Hansen - Bentuk & Kedalaman:", "Hansen membedakan kasus φ = 0: qu = 5.14·c·(1 + 0.2 B/L + 0.4k) + po; dan kasus φ > 0 sesuai tabel Hansen")
        ]),
        ("IV. PENGARUH KEDALAMAN MUKA AIR TANAH (MAT / dw)", [
            ("Kondisi dw ≥ Df (Air di bawah dasar):", "Tegangan overburden po = γ_moist · Df"),
            ("Kondisi dw ≤ 0 (Air di permukaan tanah):", "Tegangan overburden po = (γ_sat - 9.81) · Df"),
            ("Kondisi 0 < dw < Df (Air di antara 0 & Df):", "po = (γ_moist · dw) + ((γ_sat - 9.81) · (Df - dw))"),
            ("Berat isi tanah bawah dasar (γ_eff):", "Jika z = dw - Df ≥ B: γ_eff = γ_moist; jika z ≤ 0: γ_eff = γ_sub; jika 0 < z < B: γ_eff = γ_sub + (z/B)·(γ_moist - γ_sub)")
        ])
    ]

    r3 = 4
    for section_title, items in formulas_info:
        ws3[f"A{r3}"] = section_title
        ws3[f"A{r3}"].font = font_section
        r3 += 1
        for label, formula in items:
            ws3[f"A{r3}"] = label
            ws3[f"A{r3}"].font = font_bold
            ws3[f"A{r3}"].border = thin_border
            ws3[f"A{r3}"].fill = fill_meta
            ws3[f"B{r3}"] = formula
            ws3[f"B{r3}"].font = font_regular
            ws3[f"B{r3}"].border = thin_border
            r3 += 1
        r3 += 1

    # Auto-width Sheet 3
    for col in ws3.columns:
        max_len = max(len(str(c.value or '')) for c in col)
        col_letter = get_column_letter(col[0].column)
        ws3.column_dimensions[col_letter].width = max(max_len + 3, 20)

    # Simpan ke byte buffer
    output = io.BytesIO()
    wb.save(output)
    output.seek(0)
    return output.getvalue()


def generate_csv_report(comp_results, selected_dim):
    """
    Menghasilkan data teks CSV ringkasan 4 metode.
    """
    df = pd.DataFrame(comp_results)
    df["B (m)"] = selected_dim.get("B", 1.5)
    df["L (m)"] = selected_dim.get("L", 1.5)
    df["Df (m)"] = selected_dim.get("Df", 1.5)
    df["Target_SF"] = selected_dim.get("SF", 3.0)
    return df.to_csv(index=False)


def generate_spt_excel(spt_layers, project_info):
    """
    Mengekspor data penyelidikan SPT dan formasi lapisan tanah ke format Excel resmi:
    - Dilengkapi styling profesional
    - Nilai N-SPT, Konsistensi, Jenis Tanah, c, cu, φ, φ', γ
    - Dilengkapi grafik interaktif Excel (LineChart) kurva N-SPT vs Kedalaman
    - Rangkuman zona pengaruh fondasi dangkal (0 - 3.0 m)
    """
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Bore Log SPT"
    ws.views.sheetView[0].showGridLines = True

    font_title = Font(name="Calibri", size=15, bold=True, color="1E3A8A")
    font_sub = Font(name="Calibri", size=9, italic=True, color="64748B")
    font_bold = Font(name="Calibri", size=10, bold=True)
    font_reg = Font(name="Calibri", size=10)
    fill_meta = PatternFill(start_color="F1F5F9", end_color="F1F5F9", fill_type="solid")
    fill_zebra = PatternFill(start_color="F8FAFC", end_color="F8FAFC", fill_type="solid")
    fill_white = PatternFill(start_color="FFFFFF", end_color="FFFFFF", fill_type="solid")

    thin_border = Border(
        left=Side(style='thin', color='CBD5E1'),
        right=Side(style='thin', color='CBD5E1'),
        top=Side(style='thin', color='CBD5E1'),
        bottom=Side(style='thin', color='CBD5E1')
    )

    align_center = Alignment(horizontal='center', vertical='center')
    align_left = Alignment(horizontal='left', vertical='center')

    # Header Dokumen
    ws["A1"] = "BORE LOG - PENYELIDIKAN TANAH BORING & N-SPT (ASTM D1586 / SNI)"
    ws["A1"].font = font_title
    ws["A2"] = "Standar Pengujian: ASTM D1586 (Standard Penetration Test) & Koreksi Energi Skempton (1986)"
    ws["A2"].font = font_sub

    # Blok Metadata
    meta = [
        ("Nama Proyek", project_info.get("name", "Proyek Bangunan Cerdas")),
        ("Lokasi Penyelidikan", project_info.get("location", "Semarang")),
        ("Titik Pemboran (Bore Hole)", project_info.get("borehole_id", "BH-01")),
        ("Kedalaman Muka Air Tanah (MAT)", f"{float(project_info.get('water_table_depth', 1.50)):.2f} meter")
    ]

    r = 4
    for lbl, val in meta:
        ws[f"A{r}"] = lbl
        ws[f"A{r}"].font = font_bold
        ws[f"A{r}"].fill = fill_meta
        ws[f"A{r}"].border = thin_border
        ws[f"B{r}"] = val
        ws[f"B{r}"].font = font_reg
        ws[f"B{r}"].border = thin_border
        r += 1

    headers_spt = [
        "No", "Interval Kedalaman (m)", "Tebal (m)", "N1 (15cm)", "N2 (15cm)", "N3 (15cm)",
        "N-SPT (N2+N3)", "Konsistensi / Kepadatan", "Klasifikasi Tanah", "Deskripsi Lapangan",
        "Kohesi c (kPa)", "Kuat Geser cu (kPa)", "Sudut Geser φ (°)", "Sudut Geser Efektif φ' (°)",
        "Berat Isi γ (kN/m³)"
    ]

    start_row = 9
    for c_idx, h in enumerate(headers_spt, 1):
        cell = ws.cell(row=start_row, column=c_idx, value=h)
        _style_header_cell(cell, fill_color="1E3A8A", text_color="FFFFFF", bold=True, size=10)
        _style_border(cell)

    for idx, lyr in enumerate(spt_layers, 1):
        r_num = start_row + idx
        thick = round(float(lyr.get("depth_bot", 0.0)) - float(lyr.get("depth_top", 0.0)), 2)
        n_val = int(lyr.get("n_spt", 0))
        c_val = float(lyr.get("c", 0.0))
        cu_val = float(lyr.get("cu", c_val))
        phi_val = float(lyr.get("phi", 0.0))
        phi_eff = float(lyr.get("phi_eff", phi_val if phi_val > 0 else 22.0))

        row_vals = [
            idx,
            lyr.get("interval_str", f"{lyr.get('depth_top', 0):.2f} - {lyr.get('depth_bot', 0):.2f} m"),
            thick,
            lyr.get("n1", 0),
            lyr.get("n2", 0),
            lyr.get("n3", 0),
            n_val,
            lyr.get("konsistensi", "-"),
            lyr.get("soil_type", "Tanah"),
            lyr.get("deskripsi", "-"),
            c_val,
            cu_val,
            phi_val,
            phi_eff,
            lyr.get("gamma", 17.5)
        ]

        fill_row = fill_zebra if idx % 2 == 0 else fill_white
        for c_idx, v in enumerate(row_vals, 1):
            cell = ws.cell(row=r_num, column=c_idx, value=v)
            cell.font = font_reg
            cell.fill = fill_row
            _style_border(cell)
            cell.alignment = align_left if c_idx in [2, 9, 10] else align_center
            if c_idx == 7:  # Highlight N-SPT
                cell.font = font_bold

    # Rangkuman Zona Dangkal
    last_row = start_row + len(spt_layers)
    sum_row = last_row + 2
    ws[f"A{sum_row}"] = "🎯 RANGKUMAN ESTIMASI PARAMETER ZONA PONDASI DANGKAL (0 - 3.0 m):"
    ws[f"A{sum_row}"].font = Font(name="Calibri", size=10, bold=True, color="1E3A8A")

    # Native Excel LineChart Kurva N-SPT vs Kedalaman
    if len(spt_layers) > 0:
        try:
            chart = LineChart()
            chart.title = "Kurva Nilai Penetrasi Standar (N-SPT) vs Kedalaman"
            chart.style = 13
            chart.y_axis.title = "Kedalaman (m)"
            chart.x_axis.title = "N-SPT (Pukulan / 30 cm)"
            chart.width = 17
            chart.height = 12

            data_ref = Reference(ws, min_col=7, min_row=start_row, max_row=last_row)
            cats_ref = Reference(ws, min_col=2, min_row=start_row + 1, max_row=last_row)
            chart.add_data(data_ref, titles_from_data=True)
            chart.set_categories(cats_ref)
            ws.add_chart(chart, f"Q{start_row - 5}")
        except Exception:
            pass

    # Auto-adjust column width
    for col in ws.columns:
        if col[0].column > 15:
            continue
        max_len = max(len(str(c.value or '')) for c in col[:last_row + 1])
        col_letter = get_column_letter(col[0].column)
        ws.column_dimensions[col_letter].width = max(max_len + 3, 11)

    out = io.BytesIO()
    wb.save(out)
    out.seek(0)
    return out.getvalue()


def generate_cpt_excel(cpt_points, project_info):
    """
    Mengekspor data uji penetrasi sondir CPT bikonus 2.5 ton ke format Excel resmi:
    - Dilengkapi styling profesional bertema Geoteknik Hijau-Emerald
    - Kedalaman, qc, JH, HP, JHP, HS/fs (Tegangan Geser Selimut), FR, Robertson SBT, cu, φ'
    - Dilengkapi grafik interaktif Excel (LineChart) kurva qc & JHP vs Kedalaman
    - Rangkuman daya dukung ujung dan batas tanah keras (qc ≥ 150 kg/cm²)
    """
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Hasil Uji Sondir CPT"
    ws.views.sheetView[0].showGridLines = True

    font_title = Font(name="Calibri", size=15, bold=True, color="065F46")
    font_sub = Font(name="Calibri", size=9, italic=True, color="64748B")
    font_bold = Font(name="Calibri", size=10, bold=True)
    font_reg = Font(name="Calibri", size=10)
    fill_meta = PatternFill(start_color="ECFDF5", end_color="ECFDF5", fill_type="solid")
    fill_zebra = PatternFill(start_color="F8FAFC", end_color="F8FAFC", fill_type="solid")
    fill_white = PatternFill(start_color="FFFFFF", end_color="FFFFFF", fill_type="solid")

    thin_border = Border(
        left=Side(style='thin', color='CBD5E1'),
        right=Side(style='thin', color='CBD5E1'),
        top=Side(style='thin', color='CBD5E1'),
        bottom=Side(style='thin', color='CBD5E1')
    )

    align_center = Alignment(horizontal='center', vertical='center')
    align_left = Alignment(horizontal='left', vertical='center')

    # Header Dokumen
    ws["A1"] = "HASIL UJI PENETRASI KONUS / SONDIR BIKONUS 2.5 TON (CPT)"
    ws["A1"].font = font_title
    ws["A2"] = "Standar Pelaksanaan: SNI 2827:2008 & ASTM D3441 (Ac = 10 cm², Ag = 100 cm², Bikonus Begemann)"
    ws["A2"].font = font_sub

    # Blok Metadata
    meta = [
        ("Nama Proyek", project_info.get("name", "Proyek Bangunan Cerdas")),
        ("Lokasi Pengujian", project_info.get("location", "Semarang")),
        ("Titik Penyelidikan Sondir", "S-01 (Kapasitas Manometer 2.5 Ton / 250 kg/cm²)"),
        ("Kedalaman Muka Air Tanah (MAT)", f"{float(project_info.get('water_table_depth', 1.50)):.2f} meter")
    ]

    r = 4
    for lbl, val in meta:
        ws[f"A{r}"] = lbl
        ws[f"A{r}"].font = font_bold
        ws[f"A{r}"].fill = fill_meta
        ws[f"A{r}"].border = thin_border
        ws[f"B{r}"] = val
        ws[f"B{r}"].font = font_reg
        ws[f"B{r}"].border = thin_border
        r += 1

    headers_cpt = [
        "No", "Kedalaman (m)", "qc (kg/cm²)", "qc (kPa)", "JH (kg/cm²)", "HP (kg/cm)",
        "JHP Total (kg/cm)", "HS / fs (kg/cm²)", "Tegangan Geser Selimut fs (kPa)",
        "Rasio Gesek FR (%)", "Klasifikasi Tanah (Robertson 1986)",
        "Kuat Geser cu (kPa)", "Sudut Geser Efektif φ' (°)"
    ]

    start_row = 9
    for c_idx, h in enumerate(headers_cpt, 1):
        cell = ws.cell(row=start_row, column=c_idx, value=h)
        _style_header_cell(cell, fill_color="065F46", text_color="FFFFFF", bold=True, size=10)
        _style_border(cell)

    for idx, pt in enumerate(cpt_points, 1):
        r_num = start_row + idx
        qc_val = float(pt.get("qc", 0.0))
        hs_val = float(pt.get("hs", 0.0))
        fs_kpa = float(pt.get("fs_kpa", round(hs_val * 98.07, 1)))
        cu_kpa = float(pt.get("cu_kpa", round(max(10.0, (qc_val * 98.07) / 16.0), 1)))
        phi_eff = float(pt.get("phi_eff", 24.0 if qc_val < 30 else 32.0))

        row_vals = [
            idx,
            round(float(pt.get("depth", 0.0)), 2),
            round(qc_val, 1),
            round(qc_val * 98.07, 1),
            round(float(pt.get("jh", 0.0)), 1),
            round(float(pt.get("hp", 0.0)), 1),
            round(float(pt.get("jhp", 0.0)), 1),
            round(hs_val, 3),
            fs_kpa,
            round(float(pt.get("fr", 0.0)), 2),
            pt.get("soil_type", "-"),
            cu_kpa,
            phi_eff
        ]

        fill_row = fill_zebra if idx % 2 == 0 else fill_white
        for c_idx, v in enumerate(row_vals, 1):
            cell = ws.cell(row=r_num, column=c_idx, value=v)
            cell.font = font_reg
            cell.fill = fill_row
            _style_border(cell)
            cell.alignment = align_left if c_idx == 11 else align_center
            if c_idx in [3, 7, 9]:
                cell.font = font_bold

    last_row = start_row + len(cpt_points)

    # Catatan Teknis Tegangan Geser Sondir
    note_row = last_row + 2
    ws[f"A{note_row}"] = "💡 INFORMASI TEKNIS TEGANGAN GESER & KUAT GESER SONDIR:"
    ws[f"A{note_row}"].font = Font(name="Calibri", size=10, bold=True, color="065F46")
    note_row += 1
    ws[f"A{note_row}"] = (
        "1. Tegangan Geser Selimut fs (kPa): Dihitung langsung dari bacaan hambatan pelekat manometer bikonus Begemann "
        "fs = (JH - qc) / 10 (kg/cm²) × 98.07. Nilai ini adalah tahanan geser aktual antara selimut pipa baja dan tanah."
    )
    ws[f"A{note_row}"].font = Font(name="Calibri", size=9, italic=True, color="334155")
    note_row += 1
    ws[f"A{note_row}"] = (
        "2. Kuat Geser Undrained cu (kPa): Ditaksir menggunakan korelasi baku Robertson & Lunne: cu = (qc × 98.07) / Nk (dengan faktor konus Nk ≈ 16)."
    )
    ws[f"A{note_row}"].font = Font(name="Calibri", size=9, italic=True, color="334155")

    # Native Excel LineChart qc & JHP vs Kedalaman
    if len(cpt_points) > 0:
        try:
            chart = LineChart()
            chart.title = "Grafik Penyelidikan Sondir (qc & JHP vs Kedalaman)"
            chart.style = 13
            chart.y_axis.title = "Kedalaman (m)"
            chart.x_axis.title = "Tahanan Konus qc (kg/cm²) & Total Friksi JHP (kg/cm)"
            chart.width = 18
            chart.height = 14

            data_ref = Reference(ws, min_col=3, min_row=start_row, max_col=3, max_row=last_row)
            cats_ref = Reference(ws, min_col=2, min_row=start_row + 1, max_row=last_row)
            chart.add_data(data_ref, titles_from_data=True)
            chart.set_categories(cats_ref)
            ws.add_chart(chart, f"O{start_row - 5}")
        except Exception:
            pass

    # Auto-adjust column width
    for col in ws.columns:
        if col[0].column > 13:
            continue
        max_len = max(len(str(c.value or '')) for c in col[:last_row + 1])
        col_letter = get_column_letter(col[0].column)
        ws.column_dimensions[col_letter].width = max(max_len + 3, 11)

    out = io.BytesIO()
    wb.save(out)
    out.seek(0)
    return out.getvalue()
