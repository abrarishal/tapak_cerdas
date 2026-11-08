"""
=============================================================================
TAPAK CERDAS - ENGINE PENGOLAHAN DATA CONE PENETRATION TEST (CPT / SONDIR)
=============================================================================
File: modules/cpt_analyzer.py
Deskripsi: Pengolahan data sondir bikonus 2.5 ton sesuai SNI 2827:2008 & ASTM D3441:
           - Luas konus Ac = 10 cm2, Selimut Ag = 100 cm2
           - Hambatan Pelekat HP = 2 * (JH - qc) (kg/cm)
           - Jumlah Hambatan Pelekat JHP = sum(HP) (kg/cm)
           - Hambatan Setempat HS / fs = (JH - qc) / 10 (kg/cm2)
           - Rasio Gesekan FR = (HS / qc) * 100%
           - Klasifikasi Robertson & Campanella (1986) 12-Zone SBT
           - Grafik Dutch Cone Penetrometer Test (qc, Total Friksi & Stratigrafi)
=============================================================================
"""

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def classify_robertson_1986(qc_kg, fr_pct):
    """
    Klasifikasi Tanah menurut Robertson & Campanella (1986) berdasarkan qc (kg/cm2) dan FR (%).
    12 Zona Soil Behavior Type (SBT).
    Mengembalikan: zone, phi_undrained, c, gamma, color, phi_eff, cu_kpa
    """
    if qc_kg <= 0:
        return "Tidak Terdefinisi", 0.0, 0.0, 15.0, "#64748B", 20.0, 10.0

    # Estimasi Kuat Geser Undrained (cu) dari CPT: cu = (qc * 98.07) / Nk (dengan Nk = 16)
    cu_est = round(max(10.0, (qc_kg * 98.07) / 16.0), 1)

    # Klasifikasi Zona
    if fr_pct < 0.5:
        if qc_kg > 100:
            zone = "Pasir Berkerikil (Gravelly Sand)"
            phi = 38.0
            phi_eff = 38.0
            c = 0.0
            gamma = 19.5
            color = "#B45309"
        elif qc_kg > 40:
            zone = "Pasir Bersih (Sand)"
            phi = 36.0
            phi_eff = 36.0
            c = 0.0
            gamma = 19.0
            color = "#F59E0B"
        else:
            zone = "Tanah Butir Halus Sensitif"
            phi = 0.0
            phi_eff = 24.0
            c = round(max(10.0, qc_kg * 4.0), 1)
            gamma = 15.5
            color = "#EF4444"
    elif fr_pct < 1.2:
        if qc_kg > 50:
            zone = "Pasir s/d Pasir Berlanau"
            phi = 34.0
            phi_eff = 34.0
            c = 0.0
            gamma = 18.5
            color = "#EAB308"
        else:
            zone = "Pasir Berlanau / Lanau Berpasir"
            phi = 30.0
            phi_eff = 30.0
            c = 10.0
            gamma = 18.0
            color = "#84CC16"
    elif fr_pct < 2.5:
        if qc_kg > 70:
            zone = "Pasir Berlempung (Clayey Sand)"
            phi = 32.0
            phi_eff = 32.0
            c = 15.0
            gamma = 18.5
            color = "#D97706"
        elif qc_kg > 30:
            zone = "Lanau Berpasir s/d Lanau Lempungan"
            phi = 25.0
            phi_eff = 26.0
            c = 25.0
            gamma = 17.5
            color = "#10B981"
        else:
            zone = "Lanau Berlempung (Clayey Silt)"
            phi = 12.0
            phi_eff = 24.0
            c = 35.0
            gamma = 17.0
            color = "#06B6D4"
    elif fr_pct < 4.5:
        if qc_kg > 50:
            zone = "Lempung Kaku (Stiff Fine Grained)"
            phi = 15.0
            phi_eff = 26.0
            c = round(qc_kg * 5.0, 1)
            gamma = 18.5
            color = "#3B82F6"
        elif qc_kg > 15:
            zone = "Lempung Berlanau (Silty Clay)"
            phi = 0.0
            phi_eff = 22.0
            c = round(max(20.0, qc_kg * 5.5), 1)
            gamma = 16.8
            color = "#6366F1"
        else:
            zone = "Lempung Lunak (Clay)"
            phi = 0.0
            phi_eff = 20.0
            c = round(max(15.0, qc_kg * 5.0), 1)
            gamma = 16.2
            color = "#EC4899"
    else:
        # FR >= 4.5%
        if qc_kg < 15:
            zone = "Tanah Gambut / Organik"
            phi = 0.0
            phi_eff = 18.0
            c = 12.0
            gamma = 14.5
            color = "#831843"
        else:
            zone = "Lempung Sangat Plastis"
            phi = 0.0
            phi_eff = 21.0
            c = round(qc_kg * 5.0, 1)
            gamma = 16.5
            color = "#A855F7"

    return zone, phi, c, gamma, color, phi_eff, cu_est


def compute_cpt_table(points_raw):
    """
    Mengolah sekumpulan data mentah sondir (depth, qc, JH atau fs) menjadi tabel lengkap CPT.
    """
    processed = []
    jhp_running = 0.0

    for pt in points_raw:
        z = float(pt.get("depth", 0.0))
        qc = float(pt.get("qc", 0.0))
        
        # Cek apakah input berupa JH (Jumlah Hambatan) atau fs/HS langsung
        if "jh" in pt and pt["jh"] is not None:
            jh = float(pt["jh"])
            hp = max(0.0, 2.0 * (jh - qc))
            hs = max(0.0, (jh - qc) / 10.0)
        else:
            hs = float(pt.get("fs", 0.0))
            hp = hs * 20.0
            jh = qc + (hs * 10.0)

        jhp_running += hp
        fr = round((hs / qc * 100.0) if qc > 0 else 0.0, 2)
        
        zone, phi, c, gamma, color, phi_eff, cu_kpa = classify_robertson_1986(qc, fr)

        # Tegangan Geser Selimut Konus (fs) dalam satuan kPa
        fs_kpa = round(hs * 98.07, 1)

        processed.append({
            "depth": z,
            "qc": round(qc, 1),
            "jh": round(jh, 1),
            "hp": round(hp, 1),
            "jhp": round(jhp_running, 1),
            "hs": round(hs, 3),
            "fs_kpa": fs_kpa,
            "qc_kpa": round(qc * 98.07, 1),
            "fr": fr,
            "soil_type": zone,
            "phi": phi,
            "phi_eff": phi_eff,
            "c": c,
            "cu_kpa": cu_kpa,
            "gamma": gamma,
            "color": color
        })

    return processed


def plot_single_unified_cpt_chart(processed_data, gw_depth=1.5):
    """
    Membuat SATU GRAFIK TUNGGAL CPT TERINTEGRASI:
    - Sumbu X Bawah: Tahanan Konus qc (kg/cm²) dan Total Friksi JHP (kg/cm).
    - Sumbu X Atas: Rasio Gesekan FR (%).
    - Sumbu Y: Kedalaman Tanah (m) mengarah ke bawah.
    - Dilengkapi garis batas tanah keras (qc = 150 kg/cm²) dan Muka Air Tanah (MAT).
    - Legenda interaktif lengkap dan mudah dibaca.
    """
    df = pd.DataFrame(processed_data)
    if df.empty:
        return go.Figure()

    fig = go.Figure()

    # Trace 1: Tahanan Konus qc (Sumbu X Bawah)
    fig.add_trace(
        go.Scatter(
            x=df["qc"],
            y=df["depth"],
            mode="lines+markers",
            line=dict(color="#06B6D4", width=3),
            marker=dict(size=6, color="#0891B2"),
            name="🔵 Tahanan Konus qc (kg/cm²)",
            hovertemplate="Kedalaman: %{y:.2f} m<br><b>qc: %{x:.1f} kg/cm²</b><extra></extra>"
        )
    )

    # Trace 2: Total Friksi JHP (Sumbu X Bawah)
    fig.add_trace(
        go.Scatter(
            x=df["jhp"],
            y=df["depth"],
            mode="lines+markers",
            line=dict(color="#10B981", width=2.5, dash="dash"),
            marker=dict(size=5, color="#059669"),
            name="🟢 Total Friksi JHP (kg/cm)",
            hovertemplate="Kedalaman: %{y:.2f} m<br><b>JHP: %{x:.1f} kg/cm</b><extra></extra>"
        )
    )

    # Trace 3: Rasio Gesekan FR % (Sumbu X Atas / xaxis2)
    fig.add_trace(
        go.Scatter(
            x=df["fr"],
            y=df["depth"],
            mode="lines+markers",
            xaxis="x2",
            line=dict(color="#F59E0B", width=2.5),
            marker=dict(size=6, color="#D97706"),
            name="🟠 Rasio Gesekan FR (%)",
            hovertemplate="Kedalaman: %{y:.2f} m<br><b>FR: %{x:.2f}%</b><br>Tipe: %{customdata}<extra></extra>",
            customdata=df["soil_type"]
        )
    )

    # Garis Acuan Tanah Keras qc = 150 kg/cm2
    fig.add_vline(
        x=150, line_dash="dash", line_color="#EF4444", line_width=2,
        annotation_text="🔴 Batas Tanah Keras (qc = 150 kg/cm²)",
        annotation_position="top right",
        annotation_font=dict(color="#EF4444", size=11)
    )

    # Garis Muka Air Tanah (MAT)
    fig.add_hline(
        y=gw_depth, line_dash="dot", line_color="#38BDF8", line_width=2,
        annotation_text="💧 ▽ MAT (Muka Air Tanah)",
        annotation_position="bottom right",
        annotation_font=dict(color="#38BDF8", size=11)
    )

    max_depth = max(df["depth"].max(), 4.0) + 0.5
    max_qc_jhp = max(260.0, df["qc"].max() + 20, df["jhp"].max() + 20)
    max_fr = max(6.0, df["fr"].max() + 1.5)

    fig.update_layout(
        title=dict(
            text="<b>Grafik Terpadu Penyelidikan Sondir (CPT 2.5 Ton)</b>",
            font=dict(color="#F8FAFC", size=15)
        ),
        yaxis=dict(
            title=dict(text="<b>Kedalaman Tanah (meter)</b>"),
            autorange="reversed",
            gridcolor="#1E293B",
            zerolinecolor="#334155",
            range=[max_depth, 0.0]
        ),
        xaxis=dict(
            title=dict(
                text="<b>Tahanan Konus qc (kg/cm²) & Total Friksi JHP (kg/cm) [Sumbu Bawah]</b>",
                font=dict(color="#06B6D4")
            ),
            tickfont=dict(color="#06B6D4"),
            gridcolor="#1E293B",
            zerolinecolor="#334155",
            range=[0, max_qc_jhp],
            side="bottom"
        ),
        xaxis2=dict(
            title=dict(
                text="<b>Rasio Gesekan FR (%) [Sumbu Atas]</b>",
                font=dict(color="#F59E0B")
            ),
            tickfont=dict(color="#F59E0B"),
            overlaying="x",
            side="top",
            range=[0, max_fr],
            showgrid=False
        ),
        paper_bgcolor="rgba(15, 23, 42, 0.7)",
        plot_bgcolor="rgba(11, 19, 41, 0.85)",
        font=dict(color="#F8FAFC", family="Plus Jakarta Sans"),
        margin=dict(l=60, r=40, t=90, b=50),
        height=540,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.12,
            xanchor="center",
            x=0.5,
            bgcolor="rgba(15, 23, 42, 0.85)",
            bordercolor="#334155",
            borderwidth=1
        )
    )

    return fig


def plot_friction_ratio_chart(processed_data, gw_depth=1.5):
    """
    Membuat kurva Rasio Gesekan FR (%) terhadap kedalaman.
    """
    df = pd.DataFrame(processed_data)
    if df.empty:
        return go.Figure()

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=df["fr"],
            y=df["depth"],
            mode="lines+markers",
            line=dict(color="#F59E0B", width=2.5),
            marker=dict(size=6, color="#D97706"),
            name="FR (%)",
            hovertemplate="Kedalaman: %{y:.2f} m<br><b>FR: %{x:.2f}%</b><br>Tipe: %{customdata}<extra></extra>",
            customdata=df["soil_type"]
        )
    )

    # Shading tipe tanah berdasarkan FR
    fig.add_vrect(x0=0.0, x1=1.2, fillcolor="rgba(245, 158, 11, 0.1)", layer="below", line_width=0, annotation_text="Pasir", annotation_position="top left")
    fig.add_vrect(x0=1.2, x1=2.5, fillcolor="rgba(16, 185, 129, 0.1)", layer="below", line_width=0, annotation_text="Lanau", annotation_position="top left")
    fig.add_vrect(x0=2.5, x1=max(6.0, df["fr"].max() + 1), fillcolor="rgba(236, 72, 153, 0.1)", layer="below", line_width=0, annotation_text="Lempung", annotation_position="top left")

    fig.add_hline(
        y=gw_depth, line_dash="dot", line_color="#38BDF8", line_width=2,
        annotation_text="▽ MAT", annotation_position="bottom right"
    )

    max_depth = max(df["depth"].max(), 4.0) + 0.5

    fig.update_layout(
        title="<b>Kurva Rasio Gesekan (Friction Ratio / FR) vs Kedalaman</b>",
        xaxis=dict(
            title="<b>Rasio Gesekan FR (%)</b>",
            gridcolor="#1E293B",
            zerolinecolor="#334155",
            range=[0, max(6.0, df["fr"].max() + 1.0)]
        ),
        yaxis=dict(
            title="<b>Kedalaman (meter)</b>",
            autorange="reversed",
            gridcolor="#1E293B",
            zerolinecolor="#334155",
            range=[max_depth, 0.0]
        ),
        paper_bgcolor="rgba(15, 23, 42, 0.7)",
        plot_bgcolor="rgba(11, 19, 41, 0.85)",
        font=dict(color="#F8FAFC", family="Plus Jakarta Sans"),
        margin=dict(l=60, r=30, t=50, b=40),
        height=500
    )

    return fig


# DATA CONTOH SONDIR STANDAR LAPANGAN 2.5 TON
SAMPLE_SONDIR_2_5TON = [
    {"depth": 0.20, "qc": 4.0, "jh": 6.0},
    {"depth": 0.40, "qc": 5.0, "jh": 7.5},
    {"depth": 0.60, "qc": 5.0, "jh": 8.0},
    {"depth": 0.80, "qc": 6.0, "jh": 9.5},
    {"depth": 1.00, "qc": 6.0, "jh": 10.0},
    {"depth": 1.20, "qc": 7.0, "jh": 11.5},
    {"depth": 1.40, "qc": 7.0, "jh": 12.0},
    {"depth": 1.60, "qc": 8.0, "jh": 13.5},
    {"depth": 1.80, "qc": 8.0, "jh": 14.0},
    {"depth": 2.00, "qc": 9.0, "jh": 15.5},
    {"depth": 2.40, "qc": 9.0, "jh": 16.0},
    {"depth": 2.80, "qc": 10.0, "jh": 17.5},
    {"depth": 3.20, "qc": 10.0, "jh": 18.0},
    {"depth": 3.60, "qc": 16.0, "jh": 26.0},
    {"depth": 4.00, "qc": 18.0, "jh": 29.0},
    {"depth": 4.40, "qc": 20.0, "jh": 32.5},
    {"depth": 4.80, "qc": 22.0, "jh": 35.0},
    {"depth": 5.20, "qc": 24.0, "jh": 38.0},
    {"depth": 5.60, "qc": 32.0, "jh": 48.0},
    {"depth": 6.00, "qc": 40.0, "jh": 58.0},
    {"depth": 6.40, "qc": 48.0, "jh": 69.0},
    {"depth": 6.80, "qc": 68.0, "jh": 92.0},
    {"depth": 7.20, "qc": 78.0, "jh": 105.0},
    {"depth": 7.60, "qc": 88.0, "jh": 118.0},
    {"depth": 8.00, "qc": 95.0, "jh": 128.0},
    {"depth": 8.40, "qc": 110.0, "jh": 145.0},
    {"depth": 8.80, "qc": 130.0, "jh": 170.0},
    {"depth": 9.20, "qc": 145.0, "jh": 190.0},
    {"depth": 9.60, "qc": 165.0, "jh": 215.0},
    {"depth": 10.00, "qc": 210.0, "jh": 270.0}
]
