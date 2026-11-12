"""
=============================================================================
TAPAK CERDAS - ENGINE EKSPOR GAMBAR TEKNIK AUTOCAD (DXF)
=============================================================================
File: modules/dxf_exporter.py
Deskripsi: Generator file gambar kerja CAD (Drawing Exchange Format / .dxf)
           untuk perencanaan struktur fondasi telapak (Isolated Footing):
           - Satuan gambar: Milimeter (mm) - $INSUNITS = 4
           - Tampak Atas (Plan View) lengkap dengan jaring tulangan atas & bawah
           - Tampak Samping (Elevation View) dengan elevasi galian tanah & MAT
           - Potongan Melintang (Cross-Section View) dengan pembesian keranjang kotak
           - Model 3D Isometrik (3D CAD Wireframe / 3DFace) siap 3DORBIT
           - Kop Gambar (Title Block) resmi format konsultan struktur
=============================================================================
"""

import io
import math
from datetime import datetime


class DXFBuilder:
    """Builder murni Python untuk menghasilkan format DXF R12 / R2000 tanpa pustaka eksternal."""
    def __init__(self):
        self.entities = []
        self.layers = [
            ("0", 7, "CONTINUOUS"),
            ("STR_CONCRETE", 7, "CONTINUOUS"),     # Putih / Hitam tebal
            ("STR_PEDESTAL", 7, "CONTINUOUS"),
            ("STR_REBAR_BOTTOM", 4, "CONTINUOUS"), # Cyan (Tulangan Bawah)
            ("STR_REBAR_TOP", 1, "CONTINUOUS"),    # Merah (Tulangan Atas Kotak)
            ("STR_DOWEL", 3, "CONTINUOUS"),        # Hijau (Stek Dowel Kolom)
            ("STR_STIRRUP", 2, "CONTINUOUS"),      # Kuning (Sengkang/Begel)
            ("STR_DIMENSION", 6, "CONTINUOUS"),    # Magenta (Garis Dimensi & Ukur)
            ("STR_TEXT", 7, "CONTINUOUS"),         # Teks Notasi
            ("STR_TITLE", 5, "CONTINUOUS"),        # Judul Gambar (Biru)
            ("GEO_SOIL", 30, "CONTINUOUS"),        # Cokelat / Oranye (Muka Tanah)
            ("GEO_BLINDING", 8, "CONTINUOUS"),     # Abu-abu (Lantai Kerja)
            ("TITLE_BLOCK", 5, "CONTINUOUS")       # Biru Tua (Kop Gambar)
        ]

    def _add(self, code, val):
        self.entities.append(f"{code}\n{val}")

    def add_line(self, layer, x1, y1, z1, x2, y2, z2):
        self._add(0, "LINE")
        self._add(8, layer)
        self._add(10, f"{float(x1):.3f}")
        self._add(20, f"{float(y1):.3f}")
        self._add(30, f"{float(z1):.3f}")
        self._add(11, f"{float(x2):.3f}")
        self._add(21, f"{float(y2):.3f}")
        self._add(31, f"{float(z2):.3f}")

    def add_circle(self, layer, cx, cy, cz, radius):
        self._add(0, "CIRCLE")
        self._add(8, layer)
        self._add(10, f"{float(cx):.3f}")
        self._add(20, f"{float(cy):.3f}")
        self._add(30, f"{float(cz):.3f}")
        self._add(40, f"{float(radius):.3f}")

    def add_text(self, layer, text, x, y, z=0.0, height=80.0, rotation=0.0, align="LEFT"):
        self._add(0, "TEXT")
        self._add(8, layer)
        self._add(10, f"{float(x):.3f}")
        self._add(20, f"{float(y):.3f}")
        self._add(30, f"{float(z):.3f}")
        self._add(40, f"{float(height):.2f}")
        self._add(1, str(text))
        if rotation != 0.0:
            self._add(50, f"{float(rotation):.1f}")
        if align == "CENTER":
            self._add(72, "1")
            self._add(11, f"{float(x):.3f}")
            self._add(21, f"{float(y):.3f}")
            self._add(31, f"{float(z):.3f}")
        elif align == "RIGHT":
            self._add(72, "2")
            self._add(11, f"{float(x):.3f}")
            self._add(21, f"{float(y):.3f}")
            self._add(31, f"{float(z):.3f}")

    def add_rect(self, layer, x1, y1, x2, y2, z=0.0):
        """Menambahkan kotak 2D menggunakan 4 garis kontinu."""
        self.add_line(layer, x1, y1, z, x2, y1, z)
        self.add_line(layer, x2, y1, z, x2, y2, z)
        self.add_line(layer, x2, y2, z, x1, y2, z)
        self.add_line(layer, x1, y2, z, x1, y1, z)

    def add_dim_horiz(self, x1, x2, y, offset_y, text, layer="STR_DIMENSION"):
        """Garis dimensi horizontal lengkap dengan garis bantu, garis ukur, dan tanda centang (tick)."""
        dim_y = y + offset_y
        tick = 25.0
        # Extension lines
        self.add_line(layer, x1, y, 0.0, x1, dim_y + (50 if offset_y > 0 else -50), 0.0)
        self.add_line(layer, x2, y, 0.0, x2, dim_y + (50 if offset_y > 0 else -50), 0.0)
        # Dimension line
        self.add_line(layer, x1, dim_y, 0.0, x2, dim_y, 0.0)
        # Ticks (arsir 45 derajat)
        self.add_line(layer, x1 - tick, dim_y - tick, 0.0, x1 + tick, dim_y + tick, 0.0)
        self.add_line(layer, x2 - tick, dim_y - tick, 0.0, x2 + tick, dim_y + tick, 0.0)
        # Text
        mid_x = (x1 + x2) / 2.0
        txt_y = dim_y + (20 if offset_y > 0 else -60)
        self.add_text(layer, text, mid_x, txt_y, 0.0, height=45.0, align="CENTER")

    def add_dim_vert(self, x, y1, y2, offset_x, text, layer="STR_DIMENSION"):
        """Garis dimensi vertikal lengkap dengan garis bantu, garis ukur, dan tanda centang (tick)."""
        dim_x = x + offset_x
        tick = 25.0
        # Extension lines
        self.add_line(layer, x, y1, 0.0, dim_x + (50 if offset_x > 0 else -50), y1, 0.0)
        self.add_line(layer, x, y2, 0.0, dim_x + (50 if offset_x > 0 else -50), y2, 0.0)
        # Dimension line
        self.add_line(layer, dim_x, y1, 0.0, dim_x, y2, 0.0)
        # Ticks
        self.add_line(layer, dim_x - tick, y1 - tick, 0.0, dim_x + tick, y1 + tick, 0.0)
        self.add_line(layer, dim_x - tick, y2 - tick, 0.0, dim_x + tick, y2 + tick, 0.0)
        # Text
        mid_y = (y1 + y2) / 2.0
        txt_x = dim_x + (25 if offset_x > 0 else -30)
        self.add_text(layer, text, txt_x, mid_y, 0.0, height=45.0, rotation=90.0, align="CENTER")

    def add_3d_box_wireframe(self, layer, x1, y1, z1, x2, y2, z2):
        """Membuat wireframe balok 3D (12 garis rusuk)."""
        # Bawah
        self.add_line(layer, x1, y1, z1, x2, y1, z1)
        self.add_line(layer, x2, y1, z1, x2, y2, z1)
        self.add_line(layer, x2, y2, z1, x1, y2, z1)
        self.add_line(layer, x1, y2, z1, x1, y1, z1)
        # Atas
        self.add_line(layer, x1, y1, z2, x2, y1, z2)
        self.add_line(layer, x2, y1, z2, x2, y2, z2)
        self.add_line(layer, x2, y2, z2, x1, y2, z2)
        self.add_line(layer, x1, y2, z2, x1, y1, z2)
        # Vertikal
        self.add_line(layer, x1, y1, z1, x1, y1, z2)
        self.add_line(layer, x2, y1, z1, x2, y1, z2)
        self.add_line(layer, x2, y2, z1, x2, y2, z2)
        self.add_line(layer, x1, y2, z1, x1, y2, z2)

    def add_3d_face(self, layer, p1, p2, p3, p4):
        """Membuat 3DFACE AutoCAD agar dapat di-render / shaded."""
        self._add(0, "3DFACE")
        self._add(8, layer)
        self._add(10, f"{float(p1[0]):.3f}")
        self._add(20, f"{float(p1[1]):.3f}")
        self._add(30, f"{float(p1[2]):.3f}")
        self._add(11, f"{float(p2[0]):.3f}")
        self._add(21, f"{float(p2[1]):.3f}")
        self._add(31, f"{float(p2[2]):.3f}")
        self._add(12, f"{float(p3[0]):.3f}")
        self._add(21, f"{float(p3[1]):.3f}")
        self._add(31, f"{float(p3[2]):.3f}")
        self._add(13, f"{float(p4[0]):.3f}")
        self._add(23, f"{float(p4[1]):.3f}")
        self._add(33, f"{float(p4[2]):.3f}")

    def build(self):
        """Menyusun seluruh struktur format DXF R12 baku."""
        out = []

        # 1. HEADER SECTION (Units = mm, Insunits = 4)
        out.extend(["0", "SECTION", "2", "HEADER"])
        out.extend(["9", "$ACADVER", "1", "AC1009"])  # DXF R12 compatibility (Universal)
        out.extend(["9", "$INSUNITS", "70", "4"])     # 4 = Millimeters
        out.extend(["9", "$MEASUREMENT", "70", "1"])  # 1 = Metric
        out.extend(["0", "ENDSEC"])

        # 2. TABLES SECTION (Layers Table)
        out.extend(["0", "SECTION", "2", "TABLES"])
        out.extend(["0", "TABLE", "2", "LAYER", "70", str(len(self.layers))])
        for lname, color_code, ltype in self.layers:
            out.extend(["0", "LAYER", "2", lname, "70", "0", "62", str(color_code), "6", ltype])
        out.extend(["0", "ENDTAB"])
        out.extend(["0", "ENDSEC"])

        # 3. ENTITIES SECTION
        out.extend(["0", "SECTION", "2", "ENTITIES"])
        out.extend(self.entities)
        out.extend(["0", "ENDSEC"])

        # 4. EOF
        out.extend(["0", "EOF\n"])
        return "\n".join(out).encode("utf-8")


def generate_foundation_dxf(
    B_m=1.5,
    L_m=1.5,
    hf_m=0.45,
    Df_m=1.5,
    col_b_m=0.40,
    col_h_m=0.40,
    cover_mm=75.0,
    bar_dia_mm=16.0,
    reinf_results=None,
    project_info=None
):
    """
    Menghasilkan file AutoCAD DXF lengkap dengan 4 Gambar Utama:
    1. TAMPAK ATAS (PLAN VIEW): Dimensi tapak, kolom, jaring tulangan bawah X/Y & tulangan atas X/Y
    2. POTONGAN MELINTANG (CROSS SECTION): Struktur beton, lantai kerja, keranjang pembesian KOTAK, dowel, begel
    3. TAMPAK SAMPING (ELEVATION VIEW): Muka tanah asli, kedalaman Df, tebal pelat hf, pedestal kolom
    4. MODEL 3D ISOMETRIK (3D CAD WIREFRAME): Ruang koordinat 3D AutoCAD siap perintah 3DORBIT
    Semua dalam satuan Milimeter (mm)!
    """
    dxf = DXFBuilder()

    # Konversi ke Milimeter (mm)
    B = float(B_m) * 1000.0
    L = float(L_m) * 1000.0
    hf = float(hf_m) * 1000.0
    Df = float(Df_m) * 1000.0
    cb = float(col_b_m) * 1000.0
    ch = float(col_h_m) * 1000.0
    cc = float(cover_mm)
    db = float(bar_dia_mm)

    # Ambil detail tulangan jika ada
    nx_bars = 10
    ny_bars = 10
    callout_x = f"D{int(db)}-150 mm"
    callout_y = f"D{int(db)}-150 mm"
    callout_top = f"D{int(max(10, db - 3))}-200 mm (Keranjang Kotak)"

    if reinf_results:
        fx = reinf_results.get("flexure_rebar", {}).get("dir_x", {})
        fy = reinf_results.get("flexure_rebar", {}).get("dir_y", {})
        nx_bars = max(3, fx.get("n_bars", 10))
        ny_bars = max(3, fy.get("n_bars", 10))
        callout_x = fx.get("callout", callout_x)
        callout_y = fy.get("callout", callout_y)

    p_name = (project_info or {}).get("name", "Perencanaan Fondasi Bangunan")
    p_loc = (project_info or {}).get("location", "Semarang, Jawa Tengah")
    p_eng = (project_info or {}).get("engineer", "Insinyur Perencana")
    p_date = datetime.now().strftime("%Y-%m-%d")

    # Jarak spasi antar gambar di layout CAD
    gap_x = max(2500.0, B + 1500.0)

    # =========================================================================
    # VIEW 1: TAMPAK ATAS (PLAN VIEW) - Base: (0, 0)
    # =========================================================================
    p_x0, p_y0 = 0.0, 0.0

    # 1. Garis Luar Fondasi Telapak (B x L)
    dxf.add_rect("STR_CONCRETE", p_x0, p_y0, p_x0 + B, p_y0 + L)

    # 2. Kolom Pedestal di Tengah Tapak (cb x ch)
    col_x1 = p_x0 + (B - cb) / 2.0
    col_y1 = p_y0 + (L - ch) / 2.0
    col_x2 = col_x1 + cb
    col_y2 = col_y1 + ch
    dxf.add_rect("STR_PEDESTAL", col_x1, col_y1, col_x2, col_y2)

    # Garis Silang As Kolom Pedestal
    dxf.add_line("STR_PEDESTAL", col_x1, col_y1, 0.0, col_x2, col_y2, 0.0)
    dxf.add_line("STR_PEDESTAL", col_x1, col_y2, 0.0, col_x2, col_y1, 0.0)

    # 3. Jaring Tulangan Bawah Arah X (Garis horizontal membentang dari kiri ke kanan)
    x_rebar_start = p_x0 + cc
    x_rebar_end = p_x0 + B - cc
    y_rebar_step = (L - 2 * cc) / max(1, ny_bars - 1)

    for i in range(ny_bars):
        y_pos = p_y0 + cc + i * y_rebar_step
        dxf.add_line("STR_REBAR_BOTTOM", x_rebar_start, y_pos, 0.0, x_rebar_end, y_pos, 0.0)

    # 4. Jaring Tulangan Bawah Arah Y (Garis vertikal membentang dari bawah ke atas)
    y_rebar_start = p_y0 + cc
    y_rebar_end = p_y0 + L - cc
    x_rebar_step = (B - 2 * cc) / max(1, nx_bars - 1)

    for i in range(nx_bars):
        x_pos = p_x0 + cc + i * x_rebar_step
        dxf.add_line("STR_REBAR_BOTTOM", x_pos, y_rebar_start, 0.0, x_pos, y_rebar_end, 0.0)

    # 5. Jaring Tulangan Atas (Keranjang Kotak / Top Mesh) - Offset sedikit agar terlihat di CAD
    top_offset = 15.0
    for i in range(max(3, ny_bars - 1)):
        y_pos = p_y0 + cc + i * y_rebar_step + top_offset
        if y_pos < p_y0 + L - cc:
            dxf.add_line("STR_REBAR_TOP", x_rebar_start + top_offset, y_pos, 0.0, x_rebar_end - top_offset, y_pos, 0.0)

    for i in range(max(3, nx_bars - 1)):
        x_pos = p_x0 + cc + i * x_rebar_step + top_offset
        if x_pos < p_x0 + B - cc:
            dxf.add_line("STR_REBAR_TOP", x_pos, y_rebar_start + top_offset, 0.0, x_pos, y_rebar_end - top_offset, 0.0)

    # 6. Titik Stek Tulangan Sudut Kolom
    d_dowel = 20.0
    dc_cov = 40.0
    dxf.add_circle("STR_DOWEL", col_x1 + dc_cov, col_y1 + dc_cov, 0.0, d_dowel / 2.0)
    dxf.add_circle("STR_DOWEL", col_x2 - dc_cov, col_y1 + dc_cov, 0.0, d_dowel / 2.0)
    dxf.add_circle("STR_DOWEL", col_x2 - dc_cov, col_y2 - dc_cov, 0.0, d_dowel / 2.0)
    dxf.add_circle("STR_DOWEL", col_x1 + dc_cov, col_y2 - dc_cov, 0.0, d_dowel / 2.0)

    # 7. Garis Dimensi Tampak Atas
    dxf.add_dim_horiz(p_x0, p_x0 + B, p_y0, -350.0, f"B = {B:.0f} mm")
    dxf.add_dim_horiz(col_x1, col_x2, p_y0, -180.0, f"bc = {cb:.0f} mm")
    dxf.add_dim_vert(p_x0, p_y0, p_y0 + L, -350.0, f"L = {L:.0f} mm")
    dxf.add_dim_vert(col_x1, col_y1, col_y2, -180.0, f"hc = {ch:.0f} mm")

    # 8. Judul & Keterangan Tampak Atas
    dxf.add_text("STR_TITLE", "TAMPAK ATAS (PLAN VIEW)", p_x0 + B / 2.0, p_y0 - 550.0, height=110.0, align="CENTER")
    dxf.add_text("STR_TEXT", f"Tul. Bawah X: {callout_x} | Tul. Bawah Y: {callout_y}", p_x0 + B / 2.0, p_y0 - 680.0, height=65.0, align="CENTER")
    dxf.add_text("STR_TEXT", f"Tul. Atas (Kotak): {callout_top}", p_x0 + B / 2.0, p_y0 - 770.0, height=60.0, align="CENTER")
    dxf.add_text("STR_TEXT", "SKALA 1:20 (SATUAN: MM)", p_x0 + B / 2.0, p_y0 - 870.0, height=60.0, align="CENTER")

    # =========================================================================
    # VIEW 2: POTONGAN MELINTANG A-A (CROSS SECTION) - Base: (gap_x, 0)
    # =========================================================================
    s_x0 = p_x0 + gap_x
    s_y0 = 0.0  # Elevasi dasar fondasi telapak

    # 1. Lantai Kerja Beton Kurus (Lean Concrete 100 mm) & Pasir Urug (50 mm)
    dxf.add_rect("GEO_BLINDING", s_x0 - 100.0, s_y0 - 100.0, s_x0 + B + 100.0, s_y0)
    dxf.add_text("STR_TEXT", "Lantai Kerja 100 mm (fc' 10 MPa)", s_x0 + B + 140.0, s_y0 - 60.0, height=45.0)

    # 2. Pelat Fondasi Telapak (B x hf)
    dxf.add_rect("STR_CONCRETE", s_x0, s_y0, s_x0 + B, s_y0 + hf)

    # 3. Kolom Pedestal Beton (cb x tinggi_mencuat)
    col_sec_x1 = s_x0 + (B - cb) / 2.0
    col_sec_x2 = col_sec_x1 + cb
    col_sec_top = s_y0 + hf + 850.0
    dxf.add_rect("STR_PEDESTAL", col_sec_x1, s_y0 + hf, col_sec_x2, col_sec_top)

    # 4. KERANJANG PEMBESIAN KOTAK FOOTPLATE (BOX REBAR CAGE):
    hook_len = max(100.0, hf - 2.0 * cc - 20.0)

    # A. TULANGAN BAWAH ARAH X (Dengan kait 90 derajat ke ATAS)
    z_bot_rebar = s_y0 + cc + db / 2.0
    dxf.add_line("STR_REBAR_BOTTOM", s_x0 + cc, z_bot_rebar + hook_len, 0.0, s_x0 + cc, z_bot_rebar, 0.0)
    dxf.add_line("STR_REBAR_BOTTOM", s_x0 + cc, z_bot_rebar, 0.0, s_x0 + B - cc, z_bot_rebar, 0.0)
    dxf.add_line("STR_REBAR_BOTTOM", s_x0 + B - cc, z_bot_rebar, 0.0, s_x0 + B - cc, z_bot_rebar + hook_len, 0.0)

    # B. TULANGAN BAWAH ARAH Y (Tampak potongan titik/lingkaran)
    step_sec_bars = (B - 2 * cc) / max(1, nx_bars - 1)
    for i in range(nx_bars):
        cx_pos = s_x0 + cc + i * step_sec_bars
        dxf.add_circle("STR_REBAR_BOTTOM", cx_pos, z_bot_rebar + db, 0.0, db / 2.0)

    # C. TULANGAN ATAS ARAH X (Dengan kait 90 derajat ke BAWAH - MEMBENTUK KOTAK KERANJANG!)
    z_top_rebar = s_y0 + hf - cc - db / 2.0
    dxf.add_line("STR_REBAR_TOP", s_x0 + cc, z_top_rebar - hook_len, 0.0, s_x0 + cc, z_top_rebar, 0.0)
    dxf.add_line("STR_REBAR_TOP", s_x0 + cc, z_top_rebar, 0.0, s_x0 + B - cc, z_top_rebar, 0.0)
    dxf.add_line("STR_REBAR_TOP", s_x0 + B - cc, z_top_rebar, 0.0, s_x0 + B - cc, z_top_rebar - hook_len, 0.0)

    # D. TULANGAN ATAS ARAH Y (Tampak potongan titik/lingkaran atas)
    for i in range(nx_bars):
        cx_pos = s_x0 + cc + i * step_sec_bars
        dxf.add_circle("STR_REBAR_TOP", cx_pos, z_top_rebar - db, 0.0, (db - 2) / 2.0)

    # E. SENGKANG / BEGEL PENGHUBUNG TEPI KOTAK KERANJANG
    dxf.add_line("STR_STIRRUP", s_x0 + cc + 10.0, z_bot_rebar, 0.0, s_x0 + cc + 10.0, z_top_rebar, 0.0)
    dxf.add_line("STR_STIRRUP", s_x0 + B - cc - 10.0, z_bot_rebar, 0.0, s_x0 + B - cc - 10.0, z_top_rebar, 0.0)

    # 5. Tulangan Dowel Stek Kolom (Starter Bars dengan Kaki Tekuk 300 mm)
    dowel_kaki = min(350.0, (cb - 2 * dc_cov) + 100.0)
    # Kaki kiri
    dxf.add_line("STR_DOWEL", col_sec_x1 + dc_cov - dowel_kaki, z_bot_rebar + 15.0, 0.0, col_sec_x1 + dc_cov, z_bot_rebar + 15.0, 0.0)
    dxf.add_line("STR_DOWEL", col_sec_x1 + dc_cov, z_bot_rebar + 15.0, 0.0, col_sec_x1 + dc_cov, col_sec_top + 400.0, 0.0)
    # Kaki kanan
    dxf.add_line("STR_DOWEL", col_sec_x2 - dc_cov + dowel_kaki, z_bot_rebar + 15.0, 0.0, col_sec_x2 - dc_cov, z_bot_rebar + 15.0, 0.0)
    dxf.add_line("STR_DOWEL", col_sec_x2 - dc_cov, z_bot_rebar + 15.0, 0.0, col_sec_x2 - dc_cov, col_sec_top + 400.0, 0.0)

    # 6. Sengkang / Begel Kolom Pedestal
    begel_y_start = s_y0 + hf + 50.0
    for i in range(6):
        b_y = begel_y_start + i * 150.0
        dxf.add_line("STR_STIRRUP", col_sec_x1 + dc_cov, b_y, 0.0, col_sec_x2 - dc_cov, b_y, 0.0)

    # 7. Garis Dimensi Potongan Melintang
    dxf.add_dim_horiz(s_x0, s_x0 + B, s_y0, -250.0, f"B = {B:.0f} mm")
    dxf.add_dim_horiz(col_sec_x1, col_sec_x2, col_sec_top, 150.0, f"bc = {cb:.0f} mm")
    dxf.add_dim_vert(s_x0, s_y0, s_y0 + hf, -250.0, f"hf = {hf:.0f} mm")
    dxf.add_dim_vert(s_x0, s_y0 + hf, col_sec_top, -250.0, "hc = 850 mm")

    # Notasi Panah & Teks
    dxf.add_text("STR_TEXT", f"Tulangan Bawah: {callout_x}", s_x0 + B + 80.0, z_bot_rebar + 30.0, height=55.0)
    dxf.add_text("STR_TEXT", f"Tulangan Atas: {callout_top}", s_x0 + B + 80.0, z_top_rebar - 30.0, height=55.0)
    dxf.add_text("STR_TEXT", "Selimut Beton Bersih cc = 75 mm (SNI 2847)", s_x0 + B + 80.0, s_y0 + 120.0, height=50.0)
    dxf.add_text("STR_TEXT", "Dowel Kolom: 4-D16 (Kait L = 300 mm)", col_sec_x2 + 80.0, col_sec_top + 100.0, height=50.0)
    dxf.add_text("STR_TEXT", "Begel Kolom: Ø10 - 150 mm", col_sec_x2 + 80.0, begel_y_start + 150.0, height=50.0)

    # Judul Potongan
    dxf.add_text("STR_TITLE", "POTONGAN MELINTANG A-A (CROSS SECTION)", s_x0 + B / 2.0, s_y0 - 450.0, height=110.0, align="CENTER")
    dxf.add_text("STR_TEXT", "DETAIL PEMBESIAN KERANJANG KOTAK FOOTPLATE (DOUBLE MESH)", s_x0 + B / 2.0, s_y0 - 580.0, height=65.0, align="CENTER")
    dxf.add_text("STR_TEXT", "SKALA 1:20 (SATUAN: MM)", s_x0 + B / 2.0, s_y0 - 680.0, height=60.0, align="CENTER")

    # =========================================================================
    # VIEW 3: TAMPAK SAMPING & GALIAN TANAH (ELEVATION VIEW) - Base: (gap_x*2, 0)
    # =========================================================================
    e_x0 = p_x0 + gap_x * 2.0
    e_y_base = 0.0          # Elevasi dasar galian fondasi (-Df)
    e_y_ground = e_y_base + Df # Elevasi muka tanah asli (EL ±0.00)

    # 1. Garis Muka Tanah Asli (Ground Line EL ±0.00)
    dxf.add_line("GEO_SOIL", e_x0 - 800.0, e_y_ground, 0.0, e_x0 + B + 800.0, e_y_ground, 0.0)
    dxf.add_text("GEO_SOIL", "MUKA TANAH ASLI (EL ±0.00)", e_x0 + B + 850.0, e_y_ground - 20.0, height=65.0)

    # 2. Kemiringan Lereng Galian Tanah Tapak (Trench Pit Slope 1:0.5)
    slope_dx = 300.0
    dxf.add_line("GEO_SOIL", e_x0 - 600.0, e_y_ground, 0.0, e_x0 - 250.0, e_y_base, 0.0)
    dxf.add_line("GEO_SOIL", e_x0 - 250.0, e_y_base, 0.0, e_x0 + B + 250.0, e_y_base, 0.0)
    dxf.add_line("GEO_SOIL", e_x0 + B + 250.0, e_y_base, 0.0, e_x0 + B + 600.0, e_y_ground, 0.0)

    # 3. Fondasi Telapak di Dasar Galian
    dxf.add_rect("STR_CONCRETE", e_x0, e_y_base, e_x0 + B, e_y_base + hf)

    # 4. Kolom Pedestal sampai Menembus Muka Tanah (+350 mm)
    e_col_x1 = e_x0 + (B - cb) / 2.0
    e_col_x2 = e_col_x1 + cb
    e_col_top = e_y_ground + 350.0
    dxf.add_rect("STR_PEDESTAL", e_col_x1, e_y_base + hf, e_col_x2, e_col_top)

    # 5. Muka Air Tanah (GWL) jika ada
    dw_mm = float((project_info or {}).get("water_table", 1.5)) * 1000.0
    if dw_mm <= Df + 500.0:
        gw_y = e_y_ground - dw_mm
        dxf.add_line("STR_DIMENSION", e_x0 - 750.0, gw_y, 0.0, e_x0 + B + 750.0, gw_y, 0.0)
        dxf.add_text("STR_DIMENSION", f"▽ MAT (Muka Air Tanah = -{dw_mm/1000:.2f} m)", e_x0 + B + 800.0, gw_y - 20.0, height=55.0)

    # 6. Garis Dimensi Tampak Samping
    dxf.add_dim_horiz(e_x0, e_x0 + B, e_y_base, -250.0, f"B = {B:.0f} mm")
    dxf.add_dim_vert(e_x0, e_y_base, e_y_ground, -300.0, f"Df = {Df:.0f} mm")
    dxf.add_dim_vert(e_x0, e_y_base, e_y_base + hf, -150.0, f"hf = {hf:.0f} mm")

    # Judul Tampak Samping
    dxf.add_text("STR_TITLE", "TAMPAK SAMPING (ELEVATION VIEW)", e_x0 + B / 2.0, e_y_base - 450.0, height=110.0, align="CENTER")
    dxf.add_text("STR_TEXT", f"Kedalaman Galian Df = {Df:.0f} mm | Tebal Pelat hf = {hf:.0f} mm", e_x0 + B / 2.0, e_y_base - 580.0, height=65.0, align="CENTER")
    dxf.add_text("STR_TEXT", "SKALA 1:20 (SATUAN: MM)", e_x0 + B / 2.0, e_y_base - 680.0, height=60.0, align="CENTER")

    # =========================================================================
    # VIEW 4: MODEL 3D ISOMETRIK (3D CAD WIREFRAME / 3DFACE)
    # =========================================================================
    # Ditempatkan di koordinat terpisah Y = -(L + 2500 mm)
    iso_x0 = 0.0
    iso_y0 = -(L + 3000.0)
    iso_z0 = 0.0  # Elevasi dasar fondasi 3D

    # 1. Balok 3D Pelat Fondasi Telapak (B x L x hf)
    dxf.add_3d_box_wireframe("STR_CONCRETE", iso_x0, iso_y0, iso_z0, iso_x0 + B, iso_y0 + L, iso_z0 + hf)

    # 2. Balok 3D Kolom Pedestal (cb x ch x 900)
    iso_col_x1 = iso_x0 + (B - cb) / 2.0
    iso_col_y1 = iso_y0 + (L - ch) / 2.0
    iso_col_x2 = iso_col_x1 + cb
    iso_col_y2 = iso_col_y1 + ch
    iso_col_z2 = iso_z0 + hf + 900.0
    dxf.add_3d_box_wireframe("STR_PEDESTAL", iso_col_x1, iso_col_y1, iso_z0 + hf, iso_col_x2, iso_col_y2, iso_col_z2)

    # 3. KERANJANG KOTAK PEMBESIAN 3D (3D REBAR BOX CAGE):
    z3d_bot = iso_z0 + cc
    z3d_top = iso_z0 + hf - cc
    hook_3d = max(80.0, hf - 2 * cc - 10.0)

    # A. Batang Tulangan Bawah X (dengan kait Z ke atas)
    for i in range(ny_bars):
        y_p = iso_y0 + cc + i * y_rebar_step
        # Kait kiri
        dxf.add_line("STR_REBAR_BOTTOM", iso_x0 + cc, y_p, z3d_bot + hook_3d, iso_x0 + cc, y_p, z3d_bot)
        # Batang datar
        dxf.add_line("STR_REBAR_BOTTOM", iso_x0 + cc, y_p, z3d_bot, iso_x0 + B - cc, y_p, z3d_bot)
        # Kait kanan
        dxf.add_line("STR_REBAR_BOTTOM", iso_x0 + B - cc, y_p, z3d_bot, iso_x0 + B - cc, y_p, z3d_bot + hook_3d)

    # B. Batang Tulangan Bawah Y (dengan kait Z ke atas)
    for i in range(nx_bars):
        x_p = iso_x0 + cc + i * x_rebar_step
        dxf.add_line("STR_REBAR_BOTTOM", x_p, iso_y0 + cc, z3d_bot + hook_3d, x_p, iso_y0 + cc, z3d_bot)
        dxf.add_line("STR_REBAR_BOTTOM", x_p, iso_y0 + cc, z3d_bot, x_p, iso_y0 + L - cc, z3d_bot)
        dxf.add_line("STR_REBAR_BOTTOM", x_p, iso_y0 + L - cc, z3d_bot, x_p, iso_y0 + L - cc, z3d_bot + hook_3d)

    # C. Batang Tulangan Atas X (dengan kait Z ke BAWAH - MENUTUP KOTAK)
    for i in range(max(3, ny_bars - 1)):
        y_p = iso_y0 + cc + i * y_rebar_step
        dxf.add_line("STR_REBAR_TOP", iso_x0 + cc, y_p, z3d_top - hook_3d, iso_x0 + cc, y_p, z3d_top)
        dxf.add_line("STR_REBAR_TOP", iso_x0 + cc, y_p, z3d_top, iso_x0 + B - cc, y_p, z3d_top)
        dxf.add_line("STR_REBAR_TOP", iso_x0 + B - cc, y_p, z3d_top, iso_x0 + B - cc, y_p, z3d_top - hook_3d)

    # D. Batang Tulangan Atas Y (dengan kait Z ke BAWAH)
    for i in range(max(3, nx_bars - 1)):
        x_p = iso_x0 + cc + i * x_rebar_step
        dxf.add_line("STR_REBAR_TOP", x_p, iso_y0 + cc, z3d_top - hook_3d, x_p, iso_y0 + cc, z3d_top)
        dxf.add_line("STR_REBAR_TOP", x_p, iso_y0 + cc, z3d_top, x_p, iso_y0 + L - cc, z3d_top)
        dxf.add_line("STR_REBAR_TOP", x_p, iso_y0 + L - cc, z3d_top, x_p, iso_y0 + L - cc, z3d_top - hook_3d)

    # E. Stek Tulangan 4 Sudut Kolom 3D (Starter Dowels)
    dowel_corners_3d = [
        (iso_col_x1 + dc_cov, iso_col_y1 + dc_cov),
        (iso_col_x2 - dc_cov, iso_col_y1 + dc_cov),
        (iso_col_x2 - dc_cov, iso_col_y2 - dc_cov),
        (iso_col_x1 + dc_cov, iso_col_y2 - dc_cov)
    ]
    for dx_c, dy_c in dowel_corners_3d:
        # Kaki tekuk di atas tulangan bawah
        dxf.add_line("STR_DOWEL", dx_c, dy_c, z3d_bot + 10.0, dx_c + (200 if dx_c > iso_x0 + B/2 else -200), dy_c, z3d_bot + 10.0)
        # Batang vertikal ke atas
        dxf.add_line("STR_DOWEL", dx_c, dy_c, z3d_bot + 10.0, dx_c, dy_c, iso_col_z2 + 350.0)

    # Judul Model 3D
    dxf.add_text("STR_TITLE", "MODEL 3D ISOMETRIK (3D CAD WIREFRAME)", iso_x0 + B / 2.0, iso_y0 - 250.0, height=110.0, align="CENTER")
    dxf.add_text("STR_TEXT", "PETUNJUK DI AUTOCAD: KETIK '3DORBIT' ATAU KLIK VIEWCUBE (ISOMETRIC)", iso_x0 + B / 2.0, iso_y0 - 380.0, height=65.0, align="CENTER")
    dxf.add_text("STR_TEXT", "KERANJANG KOTAK PEMBESIAN 3D LENGKAP TULANGAN ATAS, BAWAH, DOWEL & SENGKANG", iso_x0 + B / 2.0, iso_y0 - 480.0, height=60.0, align="CENTER")

    # =========================================================================
    # KOP GAMBAR RESMI (TITLE BLOCK)
    # =========================================================================
    tb_x0 = gap_x
    tb_y0 = -(L + 3000.0)
    tb_w = gap_x * 1.5
    tb_h = 950.0

    dxf.add_rect("TITLE_BLOCK", tb_x0, tb_y0, tb_x0 + tb_w, tb_y0 + tb_h)
    dxf.add_line("TITLE_BLOCK", tb_x0, tb_y0 + 700.0, 0.0, tb_x0 + tb_w, tb_y0 + 700.0, 0.0)
    dxf.add_line("TITLE_BLOCK", tb_x0, tb_y0 + 400.0, 0.0, tb_x0 + tb_w, tb_y0 + 400.0, 0.0)
    dxf.add_line("TITLE_BLOCK", tb_x0 + tb_w * 0.65, tb_y0, 0.0, tb_x0 + tb_w * 0.65, tb_y0 + 700.0, 0.0)

    dxf.add_text("TITLE_BLOCK", "TAPAK CERDAS v2.0 PRO — SOFTWARE GEOTEKNIK & STRUKTUR BETON", tb_x0 + 50.0, tb_y0 + 780.0, height=80.0)
    dxf.add_text("STR_TEXT", "STANDAR: SNI 1727:2020 / SNI 2847:2019 / SNI 8460:2017", tb_x0 + 50.0, tb_y0 + 720.0, height=50.0)

    dxf.add_text("STR_TEXT", f"Proyek  : {p_name}", tb_x0 + 50.0, tb_y0 + 620.0, height=55.0)
    dxf.add_text("STR_TEXT", f"Lokasi  : {p_loc}", tb_x0 + 50.0, tb_y0 + 540.0, height=50.0)
    dxf.add_text("STR_TEXT", f"Dimensi : B={B:.0f} mm x L={L:.0f} mm x hf={hf:.0f} mm (Df={Df:.0f} mm)", tb_x0 + 50.0, tb_y0 + 460.0, height=50.0)

    dxf.add_text("STR_TEXT", f"Perencana : {p_eng}", tb_x0 + 50.0, tb_y0 + 320.0, height=50.0)
    dxf.add_text("STR_TEXT", f"Tanggal   : {p_date}", tb_x0 + 50.0, tb_y0 + 240.0, height=50.0)
    dxf.add_text("STR_TEXT", "Satuan    : MILIMETER (mm)", tb_x0 + 50.0, tb_y0 + 160.0, height=50.0)
    dxf.add_text("STR_TEXT", "Skala     : 1 : 20 (NTS pada Model 3D)", tb_x0 + 50.0, tb_y0 + 80.0, height=50.0)

    dxf.add_text("STR_TITLE", "LEMBAR GAMBAR", tb_x0 + tb_w * 0.65 + 50.0, tb_y0 + 550.0, height=60.0)
    dxf.add_text("STR_TITLE", "STR - 01", tb_x0 + tb_w * 0.65 + 150.0, tb_y0 + 220.0, height=180.0)

    return dxf.build()
