# =============================================================================
# TAPAK CERDAS - USER MANUAL & TECHNICAL GUIDE GENERATOR (PDF)
# =============================================================================
# Generator Script for TAPAK CERDAS Professional User Manual PDF
# Covers:
# 1. Overview & Dual Pathways (Layman / Civil Engineer)
# 2. Getting Started & Web Access (Localhost & Streamlit Cloud)
# 3. Module 1: Soil Investigation (SPT ASTM D1586, CPT SNI 2827:2008, 3D Subsurface Block)
# 4. Module 2: Shallow Foundation Bearing Capacity (4 Methods: Terzaghi, Meyerhof, Vesic, Hansen)
# 5. Module 3: Structural Footing Reinforcement Design (SNI 2847:2019 / ACI 318M)
# 6. Interactive 3D Cutaway Foundation & Soil Visualizations
# 7. Professional Excel Reporting:
#    - 5-Sheet Soil Investigation Report (Boring Log & CPT)
#    - 6-Sheet Foundation Calculation Report (Active Excel Formulas)
# 8. GitHub & Streamlit Cloud Deployment Guide (Fixing AttributeError)
# =============================================================================

import sys
import os
from unittest.mock import MagicMock

# Mock PIL to bypass broken _imaging DLL in QGIS Python
mock_pil = MagicMock()
sys.modules['PIL'] = mock_pil
sys.modules['PIL.Image'] = mock_pil

import reportlab
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm, mm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas


class NumberedCanvas(canvas.Canvas):
    """Running Header & Footer with dynamic 'Halaman X dari Y'."""
    def __init__(self, *args, **kwargs):
        super(NumberedCanvas, self).__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super(NumberedCanvas, self).showPage()
        super(NumberedCanvas, self).save()

    def draw_page_decorations(self, page_count):
        if self._pageNumber == 1:
            return  # Skip Cover Page

        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748B"))

        # Running Header
        self.drawString(20 * mm, 282 * mm, "TAPAK CERDAS v2.0 PRO - BUKU PANDUAN PENGGUNAAN & TEKNIS")
        self.drawRightString(190 * mm, 282 * mm, "https://tapakcerdas-abrar.streamlit.app")
        self.setStrokeColor(colors.HexColor("#CBD5E1"))
        self.setLineWidth(0.6)
        self.line(20 * mm, 280 * mm, 190 * mm, 280 * mm)

        # Running Footer
        self.line(20 * mm, 16 * mm, 190 * mm, 16 * mm)
        self.drawString(20 * mm, 12 * mm, "Software Geoteknik & Penulangan Fondasi Dangkal (SNI 1727:2020 / SNI 2847:2019)")
        page_str = f"Halaman {self._pageNumber} dari {page_count}"
        self.drawRightString(190 * mm, 12 * mm, page_str)
        self.restoreState()


def create_callout(text, title="TIPS PENGGUNAAN", bg_color="#F0FDF4", border_color="#16A34A", title_color="#15803D"):
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CalloutTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9.5,
        textColor=colors.HexColor(title_color),
        spaceAfter=3
    )
    body_style = ParagraphStyle(
        'CalloutBody',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=12,
        textColor=colors.HexColor("#1E293B")
    )
    content = [
        Paragraph(f"<b>{title}</b>", title_style),
        Paragraph(text, body_style)
    ]
    t = Table([[content]], colWidths=[170 * mm])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor(bg_color)),
        ('LEFTPADDING', (0,0), (-1,-1), 12),
        ('RIGHTPADDING', (0,0), (-1,-1), 12),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('LINELEFT', (0,0), (0,0), 3.5, colors.HexColor(border_color)),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
    ]))
    return t


def build_manual_pdf(output_pdf_path):
    doc = SimpleDocTemplate(
        output_pdf_path,
        pagesize=A4,
        leftMargin=20 * mm,
        rightMargin=20 * mm,
        topMargin=22 * mm,
        bottomMargin=20 * mm
    )

    styles = getSampleStyleSheet()

    c_primary = colors.HexColor("#1E3A8A")    # Deep Navy
    c_secondary = colors.HexColor("#0284C7")  # Cyan / Blue
    c_dark = colors.HexColor("#0F172A")       # Slate 900
    c_body = colors.HexColor("#334155")       # Slate 700

    title_cover = ParagraphStyle('CoverTitle', fontName='Helvetica-Bold', fontSize=26, leading=32, textColor=c_primary, alignment=1)
    sub_cover = ParagraphStyle('CoverSubtitle', fontName='Helvetica-Bold', fontSize=13, leading=17, textColor=c_secondary, alignment=1)
    desc_cover = ParagraphStyle('CoverDesc', fontName='Helvetica', fontSize=10, leading=15, textColor=c_body, alignment=1)

    h1 = ParagraphStyle('H1', fontName='Helvetica-Bold', fontSize=15, leading=19, textColor=c_primary, spaceBefore=12, spaceAfter=6, keepWithNext=True)
    h2 = ParagraphStyle('H2', fontName='Helvetica-Bold', fontSize=11.5, leading=15, textColor=c_secondary, spaceBefore=9, spaceAfter=4, keepWithNext=True)
    h3 = ParagraphStyle('H3', fontName='Helvetica-Bold', fontSize=10, leading=13, textColor=c_dark, spaceBefore=6, spaceAfter=3, keepWithNext=True)

    body = ParagraphStyle('Body', fontName='Helvetica', fontSize=9, leading=13, textColor=c_body, spaceAfter=4)
    body_bold = ParagraphStyle('BodyBold', fontName='Helvetica-Bold', fontSize=9, leading=13, textColor=c_dark, spaceAfter=4)
    bullet = ParagraphStyle('Bullet', fontName='Helvetica', fontSize=9, leading=13, textColor=c_body, leftIndent=12, firstLineIndent=-8, spaceAfter=3)

    table_header = ParagraphStyle('TableHeader', fontName='Helvetica-Bold', fontSize=8.5, leading=11, textColor=colors.white, alignment=1)
    table_cell = ParagraphStyle('TableCell', fontName='Helvetica', fontSize=8, leading=11, textColor=c_body)
    table_cell_bold = ParagraphStyle('TableCellBold', fontName='Helvetica-Bold', fontSize=8, leading=11, textColor=c_dark)
    table_cell_code = ParagraphStyle('TableCellCode', fontName='Courier', fontSize=7.5, leading=10, textColor=colors.HexColor("#1E40AF"))

    story = []

    # =========================================================================
    # 1. COVER PAGE (HALAMAN SAMPUL)
    # =========================================================================
    story.append(Spacer(1, 15 * mm))

    badge_data = [[Paragraph("<b>MANUAL RESMI REKAYASA GEOTEKNIK & STRUKTUR BETON</b>", ParagraphStyle('Badge', fontName='Helvetica-Bold', fontSize=9, textColor=colors.HexColor("#1D4ED8"), alignment=1))]]
    t_badge = Table(badge_data, colWidths=[130 * mm])
    t_badge.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#DBEAFE")),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#93C5FD")),
    ]))
    story.append(t_badge)
    story.append(Spacer(1, 8 * mm))

    story.append(Paragraph("BUKU PANDUAN LENGKAP<br/>PENGGUNAAN & DOKUMENTASI TEKNIS", title_cover))
    story.append(Spacer(1, 4 * mm))
    story.append(Paragraph("APLIKASI TAPAK CERDAS v2.0 PRO", sub_cover))
    story.append(Spacer(1, 6 * mm))

    story.append(Paragraph(
        "Panduan Komprehensif Identifikasi Tanah Lapangan (Borelog SPT & Sondir CPT), "
        "Perencanaan Kapasitas Dukung 4 Metode Geoteknik (Terzaghi, Meyerhof, Vesic, Hansen), "
        "Desain Penulangan Struktur Fondasi (SNI 2847:2019), Visualisasi 3D Cutaway & Subsurface Blok, "
        "Serta Ekspor Laporan Excel Profesional dengan Rumus Aktif Excel.",
        desc_cover
    ))
    story.append(Spacer(1, 12 * mm))

    info_box_data = [
        [Paragraph("<b>Alamat Akses Cloud:</b>", table_cell_bold), Paragraph("https://tapakcerdas-abrar.streamlit.app", table_cell_code)],
        [Paragraph("<b>Akses Jaringan Lokal:</b>", table_cell_bold), Paragraph("http://localhost:8501 (atau http://[IP-Komputer]:8501)", table_cell_code)],
        [Paragraph("<b>Platform Komputasi:</b>", table_cell_bold), Paragraph("Streamlit Cloud & Python 3.10+ / OpenPyXL / Plotly 3D", table_cell)],
        [Paragraph("<b>Standar Acuan Utama:</b>", table_cell_bold), Paragraph("SNI 1727:2020, SNI 2847:2019, SNI 8460:2017, ASTM D1586, SNI 2827:2008", table_cell)],
        [Paragraph("<b>Pengembang Sistem:</b>", table_cell_bold), Paragraph("Tim Pengembang Tapak Cerdas - Kolaborasi Insinyur Geoteknik & Struktur", table_cell)],
        [Paragraph("<b>Edisi Panduan:</b>", table_cell_bold), Paragraph("Edisi 2.0 Revisi Lengkap (November 2026)", table_cell)],
    ]
    t_info = Table(info_box_data, colWidths=[45 * mm, 125 * mm])
    t_info.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#F8FAFC")),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(t_info)

    story.append(Spacer(1, 12 * mm))
    story.append(create_callout(
        "<b>Petunjuk Membaca:</b> Buku panduan ini disusun runtut dari persiapan teknis, "
        "pengolahan data investigasi tanah, perancangan dimensi & penulangan pondasi telapak, "
        "interaksi visual 3D, ekspor laporan Excel, hingga pemecahan masalah deploy Streamlit Cloud.",
        title="INFORMASI PENTING",
        bg_color="#EFF6FF",
        border_color="#3B82F6",
        title_color="#1D4ED8"
    ))

    story.append(PageBreak())

    # =========================================================================
    # 2. DAFTAR ISI & SYARAT AKSES
    # =========================================================================
    story.append(Paragraph("DAFTAR ISI & STRUKTUR PEMBAHASAN", h1))
    story.append(HRFlowable(width="100%", thickness=1, color=c_primary, spaceBefore=2, spaceAfter=8))

    toc_data = [
        [Paragraph("<b>Bab</b>", table_header), Paragraph("<b>Uraian Pokok Pembahasan</b>", table_header), Paragraph("<b>Target Pengguna</b>", table_header)],
        [Paragraph("<b>Bab 1</b>", table_cell_bold), Paragraph("<b>Pengenalan & Filosofi TAPAK CERDAS v2.0</b><br/>Latar belakang, arsitektur sistem, alur kerja rekayasa, dan 2 mode akses (Pengguna Awam vs Praktisi Geoteknik).", table_cell), Paragraph("Semua Pengguna", table_cell)],
        [Paragraph("<b>Bab 2</b>", table_cell_bold), Paragraph("<b>Petunjuk Memulai, Akses Jaringan & Dashboard</b><br/>Persyaratan koneksi WiFi/internet, peramban web, navigasi navbar, dan inisialisasi parameter proyek.", table_cell), Paragraph("Semua Pengguna", table_cell)],
        [Paragraph("<b>Bab 3</b>", table_cell_bold), Paragraph("<b>Modul 1: Investigasi Karakteristik Tanah (SPT/CPT)</b><br/>- Pengeboran N-SPT (ASTM D1586) & Borelog UNDIP BH-4<br/>- Sondir Bikonus CPT (SNI 2827:2008 & Robertson 1986)<br/>- Katalog Pengguna Awam (Tanpa Uji Laboratorium)<br/>- Model Blok 3D Stratigrafi Bawah Permukaan Tanah", table_cell), Paragraph("Praktisi & Pengguna Awam", table_cell)],
        [Paragraph("<b>Bab 4</b>", table_cell_bold), Paragraph("<b>Modul 2: Perencanaan Fondasi Dangkal</b><br/>- Estimasi Beban Gedung Standar SNI 1727:2020<br/>- Komparasi 4 Metode (Terzaghi, Meyerhof, Vesic, Hansen)<br/>- Penentuan Safety Factor (2.0; 2.5; 3.0; 3.5)<br/>- Fitur Auto-Optimasi Dimensi Paling Ekonomis", table_cell), Paragraph("Insinyur Sipil & Konsultan", table_cell)],
        [Paragraph("<b>Bab 5</b>", table_cell_bold), Paragraph("<b>Modul 3: Desain Penulangan Struktur (SNI 2847:2019)</b><br/>- Material fc', fy, selimut beton 75 mm, diameter tulangan<br/>- Analisis lentur arah X & Y (As perlu, As min, spasi s)<br/>- Kontrol geser balok 1 arah & geser pons 2 arah (3 rumus)<br/>- Panjang penyaluran kait 90 derajat & Bill of Quantities (BoQ)", table_cell), Paragraph("Insinyur Struktur & Kontraktor", table_cell)],
        [Paragraph("<b>Bab 6</b>", table_cell_bold), Paragraph("<b>Visualisasi Interaktif 3D Cutaway Fondasi & Tulangan</b><br/>Model 3D potongan pondasi, rebar mesh, starter dowel, begel kolom, lubang galian tanah bergradasi, dan muka air tanah.", table_cell), Paragraph("Semua Pengguna", table_cell)],
        [Paragraph("<b>Bab 7</b>", table_cell_bold), Paragraph("<b>Sistem Ekspor Excel Profesional Standar Konsultan</b><br/>- Laporan Soil Investigation 5-Sheets (Boring Log & CPT)<br/>- Laporan Perhitungan Pondasi 6-Sheets Rumus Aktif Excel", table_cell), Paragraph("Konsultan & Klien", table_cell)],
        [Paragraph("<b>Bab 8</b>", table_cell_bold), Paragraph("<b>Panduan Deploy Streamlit Cloud & Solusi Error</b><br/>Penyelesaian tuntas AttributeError importlib.reload, sinkronisasi repositori GitHub, dan manajemen database otomatis.", table_cell), Paragraph("Administrator & Developer", table_cell)],
    ]
    t_toc = Table(toc_data, colWidths=[18 * mm, 117 * mm, 35 * mm])
    t_toc.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_primary),
        ('ALIGN', (0,0), (-1,0), 'CENTER'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#F8FAFC")]),
    ]))
    story.append(t_toc)
    story.append(Spacer(1, 5 * mm))

    story.append(create_callout(
        "<b>1. Jaringan Internet:</b> Pastikan komputer terhubung ke jaringan internet stabil (WiFi kantor/rumah) saat mengakses tautan cloud.<br/>"
        "<b>2. Peramban Rekomendasi:</b> Google Chrome atau Microsoft Edge versi modern dengan akselerasi perangkat keras WebGL aktif untuk rendering 3D mulus.<br/>"
        "<b>3. Perangkat Optimal:</b> Komputer desktop atau laptop dengan layar min 14 inci direkomendasikan untuk menelaah tabel rekap dan gambar 3D.",
        title="PERSYARATAN SISTEM SEBELUM MENGGUNAKAN APLIKASI",
        bg_color="#FEF3C7",
        border_color="#D97706",
        title_color="#B45309"
    ))

    story.append(PageBreak())

    # =========================================================================
    # BAB 1: PENGENALAN & FILOSOFI APLIKASI
    # =========================================================================
    story.append(Paragraph("BAB 1: MENGENAL APLIKASI TAPAK CERDAS v2.0", h1))
    story.append(HRFlowable(width="100%", thickness=1, color=c_primary, spaceBefore=2, spaceAfter=8))

    story.append(Paragraph(
        "<b>TAPAK CERDAS</b> adalah ekosistem software rekayasa geoteknik dan struktur pondasi dangkal berbasis web. "
        "Aplikasi ini diciptakan untuk menjawab kebutuhan praktisi sipil, konsultan perencana, kontraktor, serta pemilik bangunan "
        "yang membutuhkan alat bantu hitung yang cepat, presisi, transparan, dan memenuhi standar nasional terbaru "
        "<b>SNI 1727:2020</b> (Beban Gedung), <b>SNI 2847:2019</b> (Persyaratan Beton Struktural), dan <b>SNI 8460:2017</b> (Perancangan Geoteknik).",
        body
    ))

    story.append(Paragraph("1.1 Dua Jalur Fleksibel bagi Pengguna", h2))
    story.append(Paragraph("• <b>Jalur Praktisi & Insinyur Geoteknik:</b> Memiliki data hasil uji bor (N-SPT) atau sondir (CPT). Pengguna memasukkan data lapisan tanah riil, sistem mengkorelasikan parameter mekanika tanah (kohesi cu, sudut geser phi, berat isi gamma, kuat geser total tau), kemudian mengekspornya langsung ke modul fondasi.", bullet))
    story.append(Paragraph("• <b>Jalur Pengguna Awam / Estimasi Cepat:</b> Pemilik bangunan pribadi atau pelaksana lapangan yang tidak memiliki uji laboratorium. Pengguna dapat memanfaatkan katalog preset tanah visual (Lempung Lunak, Lempung Sedang, Pasir Lepas, Tanah Keras/Padas) atau langsung merencanakan pondasi dengan asumsi konservatif yang aman.", bullet))

    story.append(Paragraph("1.2 Empat Pilar Utama Formulasi Geoteknik", h2))
    story.append(Paragraph("1. <b>Metode Terzaghi (1943):</b> Menjadi acuan dasar terpopuler. Mengasumsikan dasar tapak kasar dan keruntuhan geser umum. Bersifat paling konservatif (menghasilkan angka daya dukung paling aman).", bullet))
    story.append(Paragraph("2. <b>Metode Meyerhof (1963):</b> Mengembangkan garis keruntuhan tanah menembus hingga ke permukaan tanah serta menyertakan faktor bentuk dan kedalaman fondasi.", bullet))
    story.append(Paragraph("3. <b>Metode Vesic (1975):</b> Memperhitungkan kompresibilitas massa tanah di bawah dasar fondasi dan sudut keruntuhan baji Prandtl termodifikasi (45 deg + phi/2).", bullet))
    story.append(Paragraph("4. <b>Metode Brinch Hansen (1970):</b> Formulasi paling komprehensif, memperhitungkan faktor bentuk, kedalaman, kemiringan beban, serta koreksi kondisi lempung jenuh (phi = 0).", bullet))

    story.append(Spacer(1, 4 * mm))

    # =========================================================================
    # BAB 2: PETUNJUK MEMULAI & DASHBOARD UTAMA
    # =========================================================================
    story.append(Paragraph("BAB 2: PETUNJUK MEMULAI & DASHBOARD PROYEK", h1))
    story.append(HRFlowable(width="100%", thickness=1, color=c_primary, spaceBefore=2, spaceAfter=8))

    story.append(Paragraph("2.1 Menjalankan Aplikasi", h2))
    story.append(Paragraph("<b>A. Melalui Peramban Web (Streamlit Cloud):</b><br/>Buka browser dan kunjungi tautan resmi: <code>https://tapakcerdas-abrar.streamlit.app</code>. Aplikasi siap digunakan secara instan tanpa perlu instalasi apapun.", body))
    story.append(Paragraph("<b>B. Melalui Komputer Lokal / Server Kantor:</b><br/>Buka terminal atau jalankan file <code>run_app.bat</code> yang tersedia di folder proyek. Buka browser pada alamat <code>http://localhost:8501</code>.", body))

    story.append(Paragraph("2.2 Struktur Menu Navigasi", h2))
    nav_table_data = [
        [Paragraph("<b>Tombol Navigasi</b>", table_header), Paragraph("<b>Nama Halaman</b>", table_header), Paragraph("<b>Fungsi Utama</b>", table_header)],
        [Paragraph("<b>Dashboard Utama</b>", table_cell_bold), Paragraph("app.py", table_cell), Paragraph("Inisialisasi nama proyek, lokasi, muka air tanah, dan katalog tanah instan.", table_cell)],
        [Paragraph("<b>1. Analisis Tanah</b>", table_cell_bold), Paragraph("1_Analisis_Tanah.py", table_cell), Paragraph("Pengolahan N-SPT, CPT Sondir 2.5T, grafik 2D terpadu, blok 3D stratigrafi, & ekspor Soil Investigation.", table_cell)],
        [Paragraph("<b>2. Perencanaan Pondasi</b>", table_cell_bold), Paragraph("2_Perencanaan_Pondasi.py", table_cell), Paragraph("Analisis beban SNI 1727, komparasi 4 metode, auto-optimasi, desain penulangan SNI 2847, & 3D Cutaway.", table_cell)],
        [Paragraph("<b>3. Riwayat / Klien</b>", table_cell_bold), Paragraph("3_Riwayat_Laporan.py", table_cell), Paragraph("Database penyimpanan proyek dan rekapitulasi pengajuan klien online.", table_cell)],
        [Paragraph("<b>4. Tentang Aplikasi</b>", table_cell_bold), Paragraph("4_Tentang_Aplikasi.py", table_cell), Paragraph("Dokumentasi standar ilmiah, rumus geoteknik, dan landasan SNI.", table_cell)],
    ]
    t_nav = Table(nav_table_data, colWidths=[40 * mm, 38 * mm, 92 * mm])
    t_nav.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_primary),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#F8FAFC")]),
    ]))
    story.append(t_nav)

    story.append(PageBreak())

    # =========================================================================
    # BAB 3: IDENTIFIKASI TANAH & MODEL BLOK 3D SUBSURFACE
    # =========================================================================
    story.append(Paragraph("BAB 3: MODUL 1 - INVESTIGASI TANAH & BLOK 3D", h1))
    story.append(HRFlowable(width="100%", thickness=1, color=c_primary, spaceBefore=2, spaceAfter=8))

    story.append(Paragraph("3.1 Opsi A: Identifikasi Berdasarkan Uji N-SPT (ASTM D1586)", h2))
    story.append(Paragraph("1. Buka halaman <b>1. Analisis Tanah</b> dan pilih tab <b>'Input Data N-SPT'</b>.", bullet))
    story.append(Paragraph("2. Masukkan tebal lapisan, nilai penetrasi N1, N2, N3. Nilai N-SPT dihitung otomatis: N-SPT = N2 + N3.", bullet))
    story.append(Paragraph("3. <i>Fitur Praktis:</i> Klik tombol <b>'Muat Data Lapangan Nyata (Borelog UNDIP BH-4)'</b> untuk menguji data riil proyek.", bullet))
    story.append(Paragraph("4. <b>Grafik 2D Terpadu:</b> Menampilkan kurva N-SPT dan kolom warna stratigrafi tanah pada satu sumbu kedalaman terintegrasi.", bullet))
    story.append(Paragraph("5. <b>Tabel Korelasi Parameter Geoteknik:</b> Menghasilkan nilai kohesi undrained (cu), sudut geser butiran (phi), berat volume (gamma), dan kuat geser tanah (tau_f).", bullet))

    story.append(Paragraph("3.2 Opsi B: Identifikasi Berdasarkan Uji Sondir CPT (SNI 2827:2008)", h2))
    story.append(Paragraph("1. Pilih tab <b>'Uji Sondir Bikonus (CPT)'</b>.", bullet))
    story.append(Paragraph("2. Masukkan kedalaman (z), tahanan konus (qc dalam kg/cm2), dan jumlah hambatan (JH).", bullet))
    story.append(Paragraph("3. <b>Klasifikasi Robertson (1986):</b> Menentukan profil tanah berdasarkan Friction Ratio (Rf = fs/qc x 100%).", bullet))

    story.append(Paragraph("3.3 Visualisasi 3D Subsurface Blok Tanah & Borehole", h2))
    story.append(Paragraph(
        "Aplikasi dilengkapi fitur visualisasi <b>Model Blok 3D Bawah Permukaan</b> yang mengadopsi standar eksplorasi geoteknik "
        "(sesuai referensi pemodelan blok tanah 3D):",
        body
    ))
    story.append(Paragraph("• <b>Balok Stratigrafi Berwarna 3D:</b> Menampilkan lapisan tanah secara isometrik lengkap dengan batas kedalaman, elevasi, dan warna litologi geoteknik yang berbeda untuk setiap jenis tanah.", bullet))
    story.append(Paragraph("• <b>Kolom Silinder Lubang Bor (Borehole):</b> Merepresentasikan posisi titik bor di tengah blok dengan segmen warna yang merefleksikan nilai kerapatan N-SPT atau tahanan ujung qc.", bullet))
    story.append(Paragraph("• <b>Bidang Muka Air Tanah (GWL):</b> Lapisan transparan biru muda yang menandai posisi muka air tanah aktual di dalam formasi tanah.", bullet))

    story.append(Paragraph("3.4 Katalog Asumsi Cepat bagi Pengguna Awam", h2))
    soil_preset_data = [
        [Paragraph("<b>Kondisi Fisik Tanah di Lapangan</b>", table_header), Paragraph("<b>Preset yang Dipilih</b>", table_header), Paragraph("<b>c (kPa)</b>", table_header), Paragraph("<b>phi (deg)</b>", table_header), Paragraph("<b>gamma (kN/m3)</b>", table_header)],
        [Paragraph("Sangat lembek, becek, jejak kaki mudah amblas dalam", table_cell), Paragraph("Tanah Lempung Sangat Lunak", table_cell_bold), Paragraph("12.0", table_cell), Paragraph("0.0", table_cell), Paragraph("16.0", table_cell)],
        [Paragraph("Lembek, mudah dicetak tangan, lengket bila basah", table_cell), Paragraph("Tanah Lempung Lunak", table_cell_bold), Paragraph("20.0", table_cell), Paragraph("0.0", table_cell), Paragraph("16.8", table_cell)],
        [Paragraph("Tanah pekarangan biasa, cukup padat, agak sukar dicetak", table_cell), Paragraph("Tanah Lempung Sedang / Teguh", table_cell_bold), Paragraph("35.0", table_cell), Paragraph("12.0", table_cell), Paragraph("17.5", table_cell)],
        [Paragraph("Tanah keras, padat, membutuhkan cangkul kuat untuk menggali", table_cell), Paragraph("Tanah Lempung Keras / Padas", table_cell_bold), Paragraph("70.0", table_cell), Paragraph("18.0", table_cell), Paragraph("19.0", table_cell)],
        [Paragraph("Tanah berbutir pasir lepas, mudah tumpah bila digenggam", table_cell), Paragraph("Tanah Pasir Lepas", table_cell_bold), Paragraph("0.0", table_cell), Paragraph("28.0", table_cell), Paragraph("17.0", table_cell)],
        [Paragraph("Tanah pasir padat bercampur kerikil, sangat stabil", table_cell), Paragraph("Tanah Pasir Padat / Kerikilan", table_cell_bold), Paragraph("0.0", table_cell), Paragraph("36.0", table_cell), Paragraph("19.5", table_cell)],
    ]
    t_soil = Table(soil_preset_data, colWidths=[55 * mm, 45 * mm, 22 * mm, 22 * mm, 26 * mm])
    t_soil.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_primary),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#F8FAFC")]),
    ]))
    story.append(t_soil)

    story.append(PageBreak())

    # =========================================================================
    # BAB 4: PERENCANAAN FONDASI DANGKAL & 4 METODE
    # =========================================================================
    story.append(Paragraph("BAB 4: PERENCANAAN FONDASI & 4 METODE DAYA DUKUNG", h1))
    story.append(HRFlowable(width="100%", thickness=1, color=c_primary, spaceBefore=2, spaceAfter=8))

    story.append(Paragraph("4.1 Estimasi Beban Gedung Standar SNI 1727:2020", h2))
    story.append(Paragraph("1. Pilih <b>Fungsi Gedung</b> (Rumah Tinggal, Kantor, Ruko/Pertokoan, Sekolah, Gudang, dll.).", bullet))
    story.append(Paragraph("2. Masukkan <b>Jumlah Lantai Bangunan</b>, <b>Luas Total Lantai</b>, dan <b>Luas Tributary Area Kolom</b>.", bullet))
    story.append(Paragraph("3. Sistem mengkalkulasi beban mati (DL), beban hidup (LL), beban kerja nominal (P = DL + LL), dan beban terfaktor (Pu = 1.2 DL + 1.6 LL).", bullet))

    story.append(Paragraph("4.2 Konfigurasi Dimensi & Pilihan Faktor Keamanan (SF)", h2))
    story.append(Paragraph("• <b>Bentuk Fondasi:</b> Bujur Sangkar (Square), Persegi Panjang (Rectangular), Lingkaran (Circular), atau Jalur Menerus (Continuous/Strip).", bullet))
    story.append(Paragraph("• <b>Pilihan Nilai SF:</b> Disediakan opsi <b>2.0; 2.5; 3.0; dan 3.5</b> sesuai dengan tingkat risiko bangunan dan rekomendasi SNI 8460:2017.", bullet))

    story.append(Paragraph("4.3 Komparasi 4 Metode Daya Dukung Terpercaya", h2))
    comp_desc_data = [
        [Paragraph("<b>Metode Daya Dukung</b>", table_header), Paragraph("<b>Karakteristik & Mekanisme Keruntuhan</b>", table_header), Paragraph("<b>Rekomendasi Pemakaian</b>", table_header)],
        [Paragraph("<b>Terzaghi (1943)</b>", table_cell_bold), Paragraph("Asumsi dasar tapak kasar. Mengabaikan tahanan geser tanah di atas dasar fondasi (hanya dihitung sebagai beban overburden po). Bersifat paling konservatif.", table_cell), Paragraph("Acuan batas aman paling kritis di lapangan (Governing Method).", table_cell)],
        [Paragraph("<b>Meyerhof (1963)</b>", table_cell_bold), Paragraph("Memperhitungkan keruntuhan tanah memanjang hingga ke permukaan tanah. Menyertakan faktor bentuk (sc, sq) dan faktor kedalaman (dc, dq).", table_cell), Paragraph("Sangat baik untuk fondasi dengan kedalaman tertanam (Df/B > 0.5).", table_cell)],
        [Paragraph("<b>Vesic (1975)</b>", table_cell_bold), Paragraph("Memperhitungkan indeks kompresibilitas tanah dan sudut baji beralas (45 deg + phi/2). Menghitung kapasitas dukung tanah berbutir maupun kohesif.", table_cell), Paragraph("Direkomendasikan untuk tanah pasir atau lempung kompresibel.", table_cell)],
        [Paragraph("<b>Brinch Hansen (1970)</b>", table_cell_bold), Paragraph("Formulasi paling lengkap. Mengakomodasi faktor bentuk, kedalaman, kemiringan beban, serta koreksi khusus kondisi lempung murni (phi = 0).", table_cell), Paragraph("Digunakan luas oleh konsultan perencana struktur profesional.", table_cell)],
    ]
    t_comp = Table(comp_desc_data, colWidths=[38 * mm, 82 * mm, 50 * mm])
    t_comp.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_primary),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#F8FAFC")]),
    ]))
    story.append(t_comp)

    story.append(Spacer(1, 3 * mm))
    story.append(Paragraph("4.4 Fitur Auto-Optimasi Dimensi Paling Ekonomis", h2))
    story.append(Paragraph(
        "Apabila salah satu metode menunjukkan status <b>OVERSTRESSED</b>, aktifkan tombol <b>'Auto-Optimasi Dimensi'</b> pada sidebar. "
        "Algoritma Tapak Cerdas akan melakukan simulasi bertahap hingga menemukan ukuran tapak terkecil di mana seluruh 4 metode "
        "serentak berstatus <b>AMAN (OK)</b>, menghemat biaya beton hingga 25% - 40%.",
        body
    ))

    story.append(PageBreak())

    # =========================================================================
    # BAB 5: DESAIN PENULANGAN PONDASI (SNI 2847:2019)
    # =========================================================================
    story.append(Paragraph("BAB 5: DESAIN PENULANGAN PONDASI (SNI 2847:2019)", h1))
    story.append(HRFlowable(width="100%", thickness=1, color=c_primary, spaceBefore=2, spaceAfter=8))

    story.append(Paragraph(
        "Setelah ukuran dimensi tapak fondasi dinyatakan aman terhadap daya dukung tanah, "
        "aplikasi secara otomatis mengaktifkan <b>Modul Desain Penulangan Struktur Fondasi Telapak</b> "
        "berdasarkan standar baku <b>SNI 2847:2019</b> (Tata Cara Perhitungan Struktur Beton untuk Bangunan Gedung).",
        body
    ))

    story.append(Paragraph("5.1 Parameter Input Struktur & Material", h2))
    story.append(Paragraph("• <b>Mutu Beton (fc'):</b> Pilihan mutu beton struktural (17.5, 20, 25, 30, 35 MPa). Default fc' = 25 MPa.", bullet))
    story.append(Paragraph("• <b>Mutu Baja Tulangan (fy):</b> Tegangan leleh baja ulir deformasi (280, 420, 520 MPa). Default fy = 420 MPa.", bullet))
    story.append(Paragraph("• <b>Tebal Selimut Beton Bersih (cc):</b> Sesuai SNI 2847:2019 Tabel 20.6.1.3.1, untuk elemen beton yang dicor langsung di atas tanah, selimut beton minimum adalah <b>75 mm</b>.", bullet))
    story.append(Paragraph("• <b>Diameter Tulangan Utama (D):</b> Pilihan diameter tulangan ulir (D10, D13, D16, D19, D22, D25 mm).", bullet))
    story.append(Paragraph("• <b>Dimensi Kolom Pedestal (bc x hc):</b> Ukuran penampang kolom beton di atas tapak (misal 40 cm x 40 cm).", bullet))
    story.append(Paragraph("• <b>Momen Lentur Kolom (Mux & Muy):</b> Gaya momen terfaktor yang bekerja pada kolom fondasi.", bullet))

    story.append(Paragraph("5.2 Alur Komputasi Penulangan Lengkap", h2))
    reinf_steps = [
        [Paragraph("<b>Langkah Perhitungan</b>", table_header), Paragraph("<b>Formula Standar SNI 2847:2019</b>", table_header), Paragraph("<b>Keterangan Teknis</b>", table_header)],
        [Paragraph("1. Tekanan Tanah Terfaktor (qu)", table_cell_bold), Paragraph("qu = Pu / (B x L) + 6 Muy / (B L^2) + 6 Mux / (L B^2)", table_cell_code), Paragraph("Tekanan kontak neto pada dasar pelat tapak.", table_cell)],
        [Paragraph("2. Momen Lentur Kritis (Mu)", table_cell_bold), Paragraph("Mu = qu x L x (B - bc)^2 / 8", table_cell_code), Paragraph("Penampang kritis momen berada tepat di muka kolom.", table_cell)],
        [Paragraph("3. Desain Tulangan Lentur (As)", table_cell_bold), Paragraph("Rn = Mu / (phi b d^2)<br/>rho = 0.85 fc'/fy [1 - sqrt(1 - 2Rn/(0.85 fc'))]<br/>rho_min = 0.0018 x (420/fy)<br/>As_req = max(rho, rho_min) x b x d", table_cell_code), Paragraph("Faktor reduksi phi = 0.90. Memenuhi batas rasio tulangan susut dan suhu.", table_cell)],
        [Paragraph("4. Jumlah & Spasi Tulangan", table_cell_bold), Paragraph("n = ceil(As / Ab)<br/>s = (B - 2 cc - D) / (n - 1)<br/>s_max = min(3 hf, 450 mm)", table_cell_code), Paragraph("Kontrol spasi agar tidak melampaui batas retak maksimum SNI.", table_cell)],
        [Paragraph("5. Kontrol Geser Balok 1 Arah", table_cell_bold), Paragraph("Vu1 = qu x L x [(B - bc)/2 - d]<br/>phi Vc1 = 0.75 x 0.17 lambda sqrt(fc') x L x d", table_cell_code), Paragraph("Penampang kritis berjarak d dari muka kolom. Syarat: Vu1 <= phi Vc1.", table_cell)],
        [Paragraph("6. Kontrol Geser Pons 2 Arah (Punching Shear)", table_cell_bold), Paragraph("bo = 2(bc + d) + 2(hc + d)<br/>Vc2 = min(Pers. 22.6.5.2a, b, c)<br/>phi Vc2 = 0.75 x Vc2", table_cell_code), Paragraph("Kritis mengelilingi perimeter bo pada jarak d/2 dari muka kolom.", table_cell)],
        [Paragraph("7. Panjang Penyaluran Kait (ldh)", table_cell_bold), Paragraph("ldh = [0.24 fy psi / (lambda sqrt(fc'))] x D", table_cell_code), Paragraph("Kait standar 90 derajat untuk menjamin angkur tulangan.", table_cell)],
        [Paragraph("8. Bill of Quantities (BoQ)", table_cell_bold), Paragraph("V_beton = B x L x hf (m3)<br/>W_besi = Total panjang x berat/meter (kg)", table_cell_code), Paragraph("Menghasilkan estimasi volume beton dan rasio kg/m3.", table_cell)],
    ]
    t_reinf = Table(reinf_steps, colWidths=[40 * mm, 78 * mm, 52 * mm])
    t_reinf.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_primary),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('TOPPADDING', (0,0), (-1,-1), 3.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3.5),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#F8FAFC")]),
    ]))
    story.append(t_reinf)

    story.append(PageBreak())

    # =========================================================================
    # BAB 6: VISUALISASI 3D CUTAWAY PONDASI & PENULANGAN
    # =========================================================================
    story.append(Paragraph("BAB 6: VISUALISASI 3D CUTAWAY FONDASI & TANAH", h1))
    story.append(HRFlowable(width="100%", thickness=1, color=c_primary, spaceBefore=2, spaceAfter=8))

    story.append(Paragraph(
        "Fitur visualisasi <b>3D Cutaway Foundation</b> dirancang khusus mengikuti standar render fotorealistik "
        "(sesuai referensi gambar potongan pondasi telapak dengan pembesian interior dan stratigrafi tanah):",
        body
    ))

    story.append(Paragraph("6.1 Komponen Model 3D Cutaway Realistis", h2))
    story.append(Paragraph("1. <b>Pelat Beton Tapak dengan Irisan Cutaway:</b> Sebagian badan beton ditampilkan terbuka sehingga detail jaring tulangan baja di bagian dalam dapat terlihat jelas dari berbagai sudut pandang.", bullet))
    story.append(Paragraph("2. <b>Keranjang Kotak Pembesian (3D Rebar Box Cage):</b> Sesuai standar konstruksi footplate modern, pembesian terdiri dari <b>jaring tulangan bawah</b> (kait membengkok ke atas), <b>jaring tulangan atas</b> (kait membengkok ke bawah), serta <b>sabuk begel keliling dan sengkang vertikal tepi</b> yang saling mengikat membentuk sangkar/kotak pembesian 3D kokoh.", bullet))
    story.append(Paragraph("3. <b>Kolom Pedestal & Stek Tulangan Kolom (Starter Dowels):</b> Penampang kolom di atas tapak dilengkapi tulangan longitudinal kolom yang menjulur ke atas serta begel (sengkang pengikat) horizontal.", bullet))
    story.append(Paragraph("4. <b>Lapisan Lantai Kerja (Lean Concrete Blinding):</b> Lapisan beton kurus setebal 100 mm dan dasar pasir urug padat di bawah dasar telapak fondasi.", bullet))
    story.append(Paragraph("5. <b>Lubang Galian Tanah & Stratigrafi Berlapis:</b> Dinding lubang galian memperlihatkan susunan strata tanah asli bergradasi warna litologi (tanah urug, lempung, pasir berlempung, dan kerikil).", bullet))
    story.append(Paragraph("6. <b>Bidang Muka Air Tanah (GWL):</b> Permukaan air tanah transparan yang dapat diamati posisinya terhadap dasar pondasi telapak.", bullet))

    story.append(Paragraph("6.2 Fitur Interaktivitas 3D di Browser", h2))
    story.append(Paragraph("• <b>Rotasi Bebas 360 Derajat:</b> Klik dan seret mouse untuk memutar model dari atas, samping, atau bawah.", bullet))
    story.append(Paragraph("• <b>Zoom & Pan Dinamis:</b> Gunakan scroll mouse untuk memperbesar hingga melihat detail jarak kait tulangan.", bullet))
    story.append(Paragraph("• <b>Hover Label Interaktif:</b> Arahkan kursor ke setiap batang tulangan atau lapisan tanah untuk membaca dimensi dan nama komponen secara langsung.", bullet))

    story.append(Spacer(1, 4 * mm))

    # =========================================================================
    # BAB 7: SISTEM EKSPOR DOKUMEN EXCEL PROFESIONAL
    # =========================================================================
    story.append(Paragraph("BAB 7: SISTEM EKSPOR EXCEL STANDAR KONSULTAN", h1))
    story.append(HRFlowable(width="100%", thickness=1, color=c_primary, spaceBefore=2, spaceAfter=8))

    story.append(Paragraph("7.1 Laporan Soil Investigation Report (5 Sheets)", h2))
    story.append(Paragraph(
        "Pada halaman Analisis Tanah, klik tombol <b>'Unduh Laporan Soil Investigation 5-Sheets (.xlsx)'</b>. "
        "Workbook Excel yang dihasilkan memiliki format resmi penyelidikan tanah berstandar konsultan geoteknik:",
        body
    ))

    sheet_soil_data = [
        [Paragraph("<b>Nama Sheet</b>", table_header), Paragraph("<b>Isi & Komponen Teknis</b>", table_header)],
        [Paragraph("<b>Sheet 1: General Information</b>", table_cell_bold), Paragraph("Identitas proyek, nama klien, lokasi, koordinat X/Y, tanggal pengujian, elevasi muka tanah, kedalaman penyelidikan, dan instansi konsultan.", table_cell)],
        [Paragraph("<b>Sheet 2: Boring Log - SPT</b>", table_cell_bold), Paragraph("Format Boring Log resmi sesuai standar ASTM D1586: Depth (m), Thickness (m), Simbol Muka Air Tanah (GWL), Simbol Litologi Tanah, Sample Type, Deskripsi Visual Tanah, pukulan N1, N2, N3, nilai N-SPT terhitung otomatis, dan <b>Grafik Vektor Native Excel N-SPT terhadap Kedalaman</b>.", table_cell)],
        [Paragraph("<b>Sheet 3: CPT Log</b>", table_cell_bold), Paragraph("Tabel pembacaan sondir: Kedalaman, Cone Resistance (qc), Sleeve Friction (fs), Friction Ratio (Rf), dan <b>Grafik Dual-Axis Hubungan Parameter CPT terhadap Kedalaman</b>.", table_cell)],
        [Paragraph("<b>Sheet 4: Soil Profile</b>", table_cell_bold), Paragraph("Visualisasi penampang kolom stratigrafi lapisan tanah lengkap dengan susunan kedalaman, ketebalan, deskripsi teknis, elevasi muka air tanah, dan kode warna litologi geoteknik.", table_cell)],
        [Paragraph("<b>Sheet 5: Summary</b>", table_cell_bold), Paragraph("Ringkasan parameter tanah representatif, elevasi lapisan tanah keras pendukung fondasi, serta kesimpulan teknis dan rekomendasi jenis fondasi.", table_cell)],
    ]
    t_s_soil = Table(sheet_soil_data, colWidths=[55 * mm, 115 * mm])
    t_s_soil.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_primary),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('TOPPADDING', (0,0), (-1,-1), 3.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3.5),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#F8FAFC")]),
    ]))
    story.append(t_s_soil)

    story.append(PageBreak())

    story.append(Paragraph("7.2 Laporan Perhitungan Pondasi 6-Sheets (Rumus Aktif Excel)", h2))
    story.append(Paragraph(
        "Pada halaman Perencanaan Pondasi, klik tombol <b>'Unduh Laporan Perhitungan Struktur 6-Sheets (.xlsx)'</b>. "
        "File ini dirancang khusus dengan <b>RUMUS AKTIF EXCEL</b> menggunakan referensi sel antar-sheet "
        "(seperti <code>='Design Criteria'!D9</code>, <code>=IF(...)</code>, <code>=SQRT(...)</code>). "
        "Pengguna dapat mengubah dimensi atau beban langsung di Microsoft Excel, dan seluruh hasil hitungan otomatis terbarui:",
        body
    ))

    sheet_found_data = [
        [Paragraph("<b>Nama Sheet</b>", table_header), Paragraph("<b>Isi & Karakteristik Rumus Aktif Excel</b>", table_header)],
        [Paragraph("<b>Sheet 1: Design Criteria</b>", table_cell_bold), Paragraph("Data kriteria desain: Nama proyek, fungsi gedung, beban SNI 1727:2020, dimensi rencana (B, L, hf, Df), mutu material (fc', fy, cc, D), dan ukuran kolom pedestal. Sel input diberi warna biru muda khusus.", table_cell)],
        [Paragraph("<b>Sheet 2: Soil Parameter</b>", table_cell_bold), Paragraph("Tabel parameter mekanika tanah: Kohesi c, sudut geser phi, berat volume gamma, kedalaman muka air tanah dw, berat volume efektif, serta faktor daya dukung tanah (Nc, Nq, Ngamma).", table_cell)],
        [Paragraph("<b>Sheet 3: Dimension Calculation</b>", table_cell_bold), Paragraph("<b>RUMUS AKTIF:</b> Menghitung kapasitas dukung ultimit (qu), beban izin (qall), tekanan kontak efektif, dan safety factor aktual untuk 4 metode secara dinamis.", table_cell)],
        [Paragraph("<b>Sheet 4: Structural Calculation</b>", table_cell_bold), Paragraph("<b>RUMUS AKTIF:</b> Tekanan kontak terfaktor qu, momen lentur terfaktor Mu, tegangan geser balok satu arah Vu1, kapasitas geser phi Vc1, dan kontrol geser pons dua arah phi Vc2.", table_cell)],
        [Paragraph("<b>Sheet 5: Reinforcement Calculation</b>", table_cell_bold), Paragraph("<b>RUMUS AKTIF:</b> Koefisien tahanan Rn, rasio tulangan perlu & minimum, luas As, jumlah batang n, jarak spasi aktual s, kontrol spasi maksimum, panjang penyaluran ldh, serta total berat besi baja (kg).", table_cell)],
        [Paragraph("<b>Sheet 6: Final Design Summary</b>", table_cell_bold), Paragraph("Rekapitulasi eksekutif: Tabel rancangan terpasang, matriks kelayakan teknis (Checklist Keamanan AMAN/OK), Bill of Quantities (Volume Beton m3 & Berat Besi kg), serta kesimpulan insinyur.", table_cell)],
    ]
    t_s_found = Table(sheet_found_data, colWidths=[55 * mm, 115 * mm])
    t_s_found.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_primary),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('TOPPADDING', (0,0), (-1,-1), 3.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3.5),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#F8FAFC")]),
    ]))
    story.append(t_s_found)
    story.append(Spacer(1, 4 * mm))

    story.append(Paragraph("7.3 Sistem Ekspor Gambar Kerja AutoCAD (.dxf dalam Satuan Milimeter)", h2))
    story.append(Paragraph(
        "Aplikasi menyediakan fitur ekspor gambar CAD berstandar konsultan perencana melalui tombol "
        "<b>'Unduh Gambar AutoCAD (.dxf)'</b>. File gambar kerja dihasilkan secara native dengan satuan <b>milimeter (mm)</b> "
        "dan dapat langsung dibuka di AutoCAD, Civil 3D, ZwCAD, maupun BricsCAD tanpa konversi skala:",
        body
    ))
    story.append(Paragraph("1. <b>Tampak Atas (Plan View):</b> Garis luar pelat fondasi (B x L mm), kolom pedestal (bc x hc mm), jaring tulangan bawah (cyan), dan jaring tulangan atas kotak (merah) lengkap dengan garis dimensi dan notasi diameter/spasi.", bullet))
    story.append(Paragraph("2. <b>Tampak Samping (Elevation View):</b> Elevasi muka tanah asli (EL ±0.00), kemiringan lereng galian tapak (slope 1:0.5), posisi pelat pada dasar galian (Df), muka air tanah (GWL), dan kolom menembus permukaan tanah.", bullet))
    story.append(Paragraph("3. <b>Potongan Melintang (Cross-Section):</b> Detail irisan vertikal memperlihatkan selimut beton 75 mm, jaring tulangan bawah dengan kait 90° ke atas, tulangan atas dengan kait membengkok ke bawah, stek dowel kolom, dan sengkang pedestal.", bullet))
    story.append(Paragraph("4. <b>Model 3D Isometrik CAD (3D Wireframe / 3DFace):</b> Geometri 3 dimensi fondasi dan sangkar pembesian utuh yang dapat diputar 360 derajat di AutoCAD menggunakan perintah <code>3DORBIT</code> atau ViewCube.", bullet))
    story.append(Paragraph("5. <b>Kop Gambar Resmi Konsultan (Title Block):</b> Lembar gambar dilengkapi etiket kop resmi (Nomor Lembar STR-01, Identitas Proyek, Nama Perencana, Tanggal, Skala 1:20, dan Acuan SNI).", bullet))

    story.append(Spacer(1, 4 * mm))

    # =========================================================================
    # BAB 8: PANDUAN DEPLOYMENT STREAMLIT CLOUD & SOLUSI ERROR
    # =========================================================================
    story.append(Paragraph("BAB 8: DEPLOYMENT STREAMLIT CLOUD & SOLUSI ERROR", h1))
    story.append(HRFlowable(width="100%", thickness=1, color=c_primary, spaceBefore=2, spaceAfter=8))

    story.append(Paragraph("8.1 Penjelasan & Solusi Tuntas Error AttributeError Streamlit Cloud", h2))
    story.append(Paragraph(
        "Pada pengunggahan repositori ke GitHub (<code>abrarishal/tapak_cerdas</code>), muncul pesan kesalahan di Streamlit Cloud:<br/>"
        "<code>AttributeError: ... in pages/1_Analisis_Tanah.py, line 29: importlib.reload(utils.excel_exporter)</code>",
        body
    ))
    story.append(Paragraph("<b>Penyebab Teknis:</b> Perintah <code>importlib.reload(...)</code> adalah fungsi debugging hot-reload lokal yang tidak kompatibel dengan arsitektur multi-threading Streamlit Cloud.", body))
    story.append(Paragraph("<b>Solusi yang Telah Diterapkan:</b> Seluruh baris <code>importlib.reload</code> telah <b>dibersihkan secara total</b> dari seluruh modul dan file halaman di folder aplikasi (<code>pages/1_Analisis_Tanah.py</code>, <code>pages/2_Perencanaan_Pondasi.py</code>, dan <code>pages/3_Riwayat_Laporan.py</code>). Seluruh modul kini diimpor secara standar Python bersih.", body))

    story.append(Paragraph("8.2 Langkah-Langkah Sinkronisasi Repositori GitHub & Streamlit Cloud", h2))
    story.append(Paragraph("Agar aplikasi di Streamlit Cloud (<code>tapakcerdas-abrar.streamlit.app</code>) berjalan mulus tanpa error:", body))
    story.append(Paragraph("1. Buka folder kerja lokal di komputer Anda: <code>C:\\Users\\Asus\\.gemini\\antigravity\\scratch\\tapak_cerdas</code>.", bullet))
    story.append(Paragraph("2. Salin (copy) seluruh file dan subfolder yang telah diperbarui ke folder git lokal Anda atau unggah langsung ke GitHub repository <b>abrarishal/tapak_cerdas</b>.", bullet))
    story.append(Paragraph("3. Lakukan <code>git add .</code>, <code>git commit -m 'Update Tapak Cerdas v2.0: 3D cutaway, reinforcement design, professional excel reports'</code>, dan <code>git push origin main</code>.", bullet))
    story.append(Paragraph("4. Buka dashboard Streamlit Cloud di browser. Streamlit Cloud akan mendeteksi commit baru secara otomatis dan melakukan *auto-rebuild*.", bullet))
    story.append(Paragraph("5. Jika diperlukan, klik tombol <b>'Manage app'</b> di pojok kanan bawah layar Streamlit Cloud, lalu pilih <b>'Reboot app'</b> atau <b>'Clear cache'</b>.", bullet))

    story.append(Spacer(1, 4 * mm))
    story.append(Paragraph("8.3 Integrasi Database Otomatis & Kerahasiaan Klien", h2))
    story.append(Paragraph("• Setiap kali pengunjung mengklik tombol kalkulasi di halaman web, data spesifikasi proyek otomatis tersimpan di folder <code>database/</code>.", bullet))
    story.append(Paragraph("• Pemilik aplikasi dapat membuka halaman <b>3. Riwayat / Klien</b> kapan saja untuk mengunduh rekapitulasi data klien dalam format Excel (<code>Rekap_Data_Pengguna_Masuk.xlsx</code>) atau menindaklanjutinya via WhatsApp.", bullet))

    story.append(Spacer(1, 6 * mm))
    story.append(Paragraph("<font color='#64748B' size='8'><i>(c) 2026 TAPAK CERDAS v2.0 PRO METRIK. Dikembangkan untuk kemajuan rekayasa geoteknik, keselamatan konstruksi gedung, dan digitalisasi ketekniksipilan nasional.</i></font>", ParagraphStyle('FooterEnd', alignment=1)))

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"PDF Buku Panduan berhasil dibuat: {output_pdf_path} (Ukuran: {os.path.getsize(output_pdf_path)} bytes)")


if __name__ == '__main__':
    out_path = r"C:\Users\Asus\.gemini\antigravity\scratch\tapak_cerdas\BUKU_PANDUAN_TAPAK_CERDAS.pdf"
    build_manual_pdf(out_path)
