"""
=============================================================================
TAPAK CERDAS - ENGINE PENGOLAHAN DATA STANDARD PENETRATION TEST (SPT)
=============================================================================
File: modules/spt_analyzer.py
Deskripsi: Perhitungan N-SPT = N2 + N3, koreksi N60 & (N1)60, klasifikasi
           konsistensi otomatis dari N-SPT, korelasi parameter mekanika tanah
           (c, phi, gamma), kurva penetrasi dan stratigrafi profil tanah.
=============================================================================
"""

import math
import pandas as pd
import plotly.graph_objects as go

def infer_soil_from_spt(n_spt, user_type_hint=None):
    """
    Mengidentifikasi karakteristik dan parameter tanah otomatis dari nilai N-SPT
    apabila jenis tanah belum diketahui secara pasti di laboratorium.
    Acuan: Terzaghi & Peck (1967), Meyerhof (1956), Bowles (1996).
    """
    n_spt = max(1, int(n_spt))

    if user_type_hint and "Pasir" in user_type_hint:
        is_granular = True
    elif user_type_hint and "Lempung" in user_type_hint:
        is_granular = False
    else:
        # Default estimasi geoteknik awal: N rendah (<= 15) umumnya didominasi lempung/lanau halus
        # N tinggi (> 15) bisa berupa lempung sangat kaku atau pasir berkerikil
        is_granular = (n_spt > 25)

    if not is_granular:
        # Tanah Kohesif (Lempung / Lanau Kelempungan)
        if n_spt < 2:
            konsistensi = "Sangat Lunak (Very Soft)"
            deskripsi = "Tanah lempung sangat lunak, mudah tertekan dengan jari"
            c = round(max(10.0, 12.0 * n_spt), 1)
            phi = 0.0
            gamma = 15.2
            gamma_sat = 16.8
            soil_cat = "Lempung Sangat Lunak"
            color = "#7C3AED"
        elif n_spt <= 4:
            konsistensi = "Lunak (Soft)"
            deskripsi = "Tanah lempung lunak, dapat dibentuk dengan tekanan ibu jari"
            c = round(12.5 * n_spt, 1)
            phi = 0.0
            gamma = 16.2
            gamma_sat = 17.8
            soil_cat = "Lempung Lunak"
            color = "#6366F1"
        elif n_spt <= 8:
            konsistensi = "Sedang / Teguh (Medium Stiff)"
            deskripsi = "Tanah lempung sedang, membutuhkan tekanan kuat untuk dibentuk"
            c = round(min(55.0, 7.5 * n_spt + 15), 1)
            phi = 5.0
            gamma = 17.5
            gamma_sat = 19.0
            soil_cat = "Lempung Sedang"
            color = "#3B82F6"
        elif n_spt <= 15:
            konsistensi = "Kaku (Stiff)"
            deskripsi = "Tanah lempung kaku, tidak dapat dibentuk dengan jari"
            c = round(min(100.0, 6.0 * n_spt + 20), 1)
            phi = 10.0
            gamma = 18.5
            gamma_sat = 20.0
            soil_cat = "Lempung Kaku"
            color = "#0EA5E9"
        elif n_spt <= 30:
            konsistensi = "Sangat Kaku (Very Stiff)"
            deskripsi = "Tanah lempung sangat kaku, sulit digores kuku"
            c = round(min(180.0, 5.5 * n_spt + 30), 1)
            phi = 12.0
            gamma = 19.2
            gamma_sat = 20.8
            soil_cat = "Lempung Sangat Kaku"
            color = "#0D9488"
        else:
            konsistensi = "Keras (Hard)"
            deskripsi = "Tanah lempung keras membatu (hard cohesive)"
            c = round(min(250.0, 5.0 * n_spt + 40), 1)
            phi = 15.0
            gamma = 20.0
            gamma_sat = 21.5
            soil_cat = "Lempung Keras"
            color = "#059669"
    else:
        # Tanah Granular (Pasir / Pasir Berkerikil)
        c = 0.0
        if n_spt < 4:
            konsistensi = "Sangat Lepas (Very Loose)"
            deskripsi = "Pasir berbutir sangat lepas"
            phi = 28.0
            gamma = 15.5
            gamma_sat = 17.5
            soil_cat = "Pasir Sangat Lepas"
            color = "#F59E0B"
        elif n_spt <= 10:
            konsistensi = "Lepas (Loose)"
            deskripsi = "Pasir lepas, mudah tergeser"
            phi = round(28.0 + (n_spt - 4) * 0.5, 1)
            gamma = 16.8
            gamma_sat = 18.5
            soil_cat = "Pasir Lepas"
            color = "#EAB308"
        elif n_spt <= 30:
            konsistensi = "Kepadatan Sedang (Medium Dense)"
            deskripsi = "Pasir agak padat, tahanan penetrasi sedang"
            phi = round(31.0 + (n_spt - 10) * 0.25, 1)
            gamma = 18.2
            gamma_sat = 20.0
            soil_cat = "Pasir Sedang"
            color = "#D97706"
        elif n_spt <= 50:
            konsistensi = "Padat (Dense)"
            deskripsi = "Pasir padat, kekuatan geser tinggi"
            phi = round(36.0 + (n_spt - 30) * 0.25, 1)
            gamma = 19.5
            gamma_sat = 21.2
            soil_cat = "Pasir Padat"
            color = "#B45309"
        else:
            konsistensi = "Sangat Padat (Very Dense)"
            deskripsi = "Pasir berkerikil sangat padat (padas)"
            phi = 42.0
            gamma = 20.5
            gamma_sat = 22.0
            soil_cat = "Pasir Sangat Padat"
            color = "#92400E"

    return {
        "konsistensi": konsistensi,
        "deskripsi": deskripsi,
        "soil_cat": soil_cat,
        "c": c,
        "phi": phi,
        "gamma": gamma,
        "gamma_sat": gamma_sat,
        "color": color
    }


def compute_spt_layer(depth_top, depth_bot, n1, n2, n3, user_desc="", soil_type="Auto (Deteksi dari N-SPT)", energy_ratio=0.60, gw_depth=1.5):
    """
    Menghitung N-SPT dan menginterpretasikan jenis serta karakteristik tanah.
    """
    n_spt = int(n2 + n3)
    
    # Skempton (1986) N60
    ce = energy_ratio / 0.60
    cb = 1.0  # Diameter lubang standar 73 mm
    cs = 1.0  # Tabung standar tanpa liner
    avg_depth = (depth_top + depth_bot) / 2.0
    if avg_depth < 4.0:
        cr = 0.75
    elif avg_depth < 6.0:
        cr = 0.85
    elif avg_depth < 10.0:
        cr = 0.95
    else:
        cr = 1.0
        
    n60 = round(n_spt * ce * cb * cs * cr, 1)
    
    # Liao & Whitman (1986) Overburden (N1)60
    gamma_est = 17.5
    gamma_eff = (gamma_est - 9.81) if avg_depth > gw_depth else gamma_est
    sigma_v0 = max(10.0, avg_depth * gamma_eff)
    pa = 100.0  # 1 atm ≈ 100 kPa
    cn = min(1.7, math.sqrt(pa / sigma_v0))
    n1_60 = round(cn * n60, 1)

    # Identifikasi jenis tanah otomatis
    interp = infer_soil_from_spt(n_spt, soil_type)
    
    # Jika pengguna memberikan deskripsi manual (seperti di Bore Log Undip)
    deskripsi_final = user_desc if user_desc.strip() else interp["deskripsi"]

    return {
        "depth_top": depth_top,
        "depth_bot": depth_bot,
        "interval_str": f"{depth_top:.2f} - {depth_bot:.2f} m",
        "thickness": round(depth_bot - depth_top, 2),
        "n1": n1,
        "n2": n2,
        "n3": n3,
        "n_spt": n_spt,
        "n60": n60,
        "n1_60": n1_60,
        "soil_type": interp["soil_cat"] if "Auto" in soil_type else soil_type,
        "konsistensi": interp["konsistensi"],
        "deskripsi": deskripsi_final,
        "phi": interp["phi"],
        "c": interp["c"],
        "gamma": interp["gamma"],
        "gamma_sat": interp["gamma_sat"],
        "color": interp["color"]
    }


def compute_weighted_average_params(layers, target_depth=3.0):
    """
    Menghitung parameter rata-rata terbobot ketebalan untuk zona pengaruh pondasi (0 - target_depth m).
    """
    total_thick = 0.0
    sum_phi = 0.0
    sum_c = 0.0
    sum_gamma = 0.0
    sum_gamma_sat = 0.0
    dominant_types = []

    for lyr in layers:
        z_top = lyr.get("depth_top", 0.0)
        z_bot = lyr.get("depth_bot", 0.0)
        
        # Cari irisan dengan zona 0 - target_depth
        overlap_top = max(0.0, z_top)
        overlap_bot = min(target_depth, z_bot)
        
        if overlap_bot > overlap_top:
            h = overlap_bot - overlap_top
            total_thick += h
            sum_phi += lyr.get("phi", 0.0) * h
            sum_c += lyr.get("c", 0.0) * h
            sum_gamma += lyr.get("gamma", 17.5) * h
            sum_gamma_sat += lyr.get("gamma_sat", 19.0) * h
            dominant_types.append(lyr.get("soil_type", "Tanah"))

    if total_thick > 0:
        avg_phi = round(sum_phi / total_thick, 1)
        avg_c = round(sum_c / total_thick, 1)
        avg_gamma = round(sum_gamma / total_thick, 1)
        avg_gamma_sat = round(sum_gamma_sat / total_thick, 1)
        desc_summary = ", ".join(list(dict.fromkeys(dominant_types)))
    else:
        avg_phi = 15.0
        avg_c = 30.0
        avg_gamma = 17.5
        avg_gamma_sat = 19.0
        desc_summary = "Tanah Campuran"

    return {
        "target_depth": target_depth,
        "actual_depth_evaluated": round(total_thick, 2),
        "phi": avg_phi,
        "c": avg_c,
        "gamma": avg_gamma,
        "gamma_sat": avg_gamma_sat,
        "summary": desc_summary
    }


def plot_spt_profile(layers, gw_depth=1.5):
    """
    Membuat grafik interaktif Profil N-SPT terhadap Kedalaman (Sumbu Y ke bawah).
    """
    if not layers:
        return go.Figure()

    depths = []
    n_vals = []
    hover_texts = []

    for lyr in layers:
        z_top = lyr.get("depth_top", 0.0)
        z_bot = lyr.get("depth_bot", z_top + 1.5)
        mid_z = (z_top + z_bot) / 2.0
        depths.append(mid_z)
        n_val = lyr.get("n_spt", 10)
        n_vals.append(n_val)
        
        interval = lyr.get("interval_str", f"{z_top:.2f} - {z_bot:.2f} m")
        kons = lyr.get("konsistensi", "Sedang")
        desc = lyr.get("deskripsi", lyr.get("soil_type", "Tanah"))
        c_val = lyr.get("c", 0.0)
        phi_val = lyr.get("phi", 0.0)

        hover_texts.append(
            f"<b>Lapisan:</b> {interval}<br>"
            f"<b>N-SPT:</b> {n_val} pukulan<br>"
            f"<b>Konsistensi:</b> {kons}<br>"
            f"<b>Deskripsi:</b> {desc}<br>"
            f"<b>c:</b> {c_val} kPa | <b>φ:</b> {phi_val}°"
        )

    fig = go.Figure()

    # Trace N-SPT
    fig.add_trace(
        go.Scatter(
            x=n_vals,
            y=depths,
            mode="lines+markers",
            line=dict(color="#38BDF8", width=3, shape="linear"),
            marker=dict(size=9, color="#0284C7", line=dict(color="#FFFFFF", width=1.5)),
            name="N-SPT Terukur",
            text=hover_texts,
            hoverinfo="text"
        )
    )

    # Tambahkan Garis Muka Air Tanah (MAT)
    fig.add_hline(
        y=gw_depth,
        line_dash="dash",
        line_color="#06B6D4",
        line_width=2,
        annotation_text="▽ MAT (Muka Air Tanah)",
        annotation_position="bottom right",
        annotation_font=dict(color="#06B6D4", size=12)
    )

    # Shading Zona Fondasi Dangkal (0 - 3m)
    fig.add_hrect(
        y0=0.0, y1=min(3.0, max(depths) if depths else 3.0),
        fillcolor="rgba(56, 189, 248, 0.08)",
        layer="below", line_width=0,
        annotation_text="Zona Pengaruh Fondasi Dangkal (0 - 3m)",
        annotation_position="top left",
        annotation_font=dict(color="#38BDF8", size=11)
    )

    max_z = max([lyr["depth_bot"] for lyr in layers]) if layers else 10.0

    fig.update_layout(
        title="<b>Kurva Nilai Penetrasi Standar (N-SPT) vs Kedalaman</b>",
        xaxis=dict(
            title="<b>Nilai N-SPT (pukulan / 30 cm)</b>",
            gridcolor="#1E293B",
            zerolinecolor="#334155",
            range=[0, max(60, max(n_vals) + 10)]
        ),
        yaxis=dict(
            title="<b>Kedalaman Tanah (meter)</b>",
            autorange="reversed",  # Kedalaman bertambah ke bawah
            gridcolor="#1E293B",
            zerolinecolor="#334155",
            range=[max_z + 0.5, 0.0]
        ),
        paper_bgcolor="rgba(15, 23, 42, 0.7)",
        plot_bgcolor="rgba(11, 19, 41, 0.85)",
        font=dict(color="#F8FAFC", family="Plus Jakarta Sans"),
        margin=dict(l=60, r=40, t=50, b=40),
        height=480,
        showlegend=True
    )

    return fig


def plot_stratigraphy_column(layers):
    """
    Membuat diagram penampang kolom stratigrafi lapisan tanah vertikal warna.
    """
    if not layers:
        return go.Figure()

    fig = go.Figure()

    for lyr in layers:
        z_top = lyr.get("depth_top", 0.0)
        z_bot = lyr.get("depth_bot", z_top + 1.5)
        h = max(0.2, z_bot - z_top)
        interval = lyr.get("interval_str", f"{z_top:.2f} - {z_bot:.2f} m")
        stype = lyr.get("soil_type", "Tanah")
        n_spt = lyr.get("n_spt", 10)
        kons = lyr.get("konsistensi", "Sedang")
        desc = lyr.get("deskripsi", stype)
        c_val = lyr.get("c", 0.0)
        phi_val = lyr.get("phi", 0.0)
        
        fig.add_trace(
            go.Bar(
                x=["Profil Tanah"],
                y=[h],
                base=z_top,
                marker=dict(
                    color=lyr.get("color", "#3B82F6"),
                    line=dict(color="#FFFFFF", width=1)
                ),
                name=f"{interval}: {stype}",
                hovertemplate=(
                    f"<b>{interval}</b><br>"
                    f"N-SPT: {n_spt} ({kons})<br>"
                    f"Deskripsi: {desc}<br>"
                    f"c = {c_val} kPa, φ = {phi_val}°<extra></extra>"
                ),
                text=f"<b>{interval}</b><br>{stype}<br>N={n_spt}",
                textposition="inside",
                insidetextanchor="middle"
            )
        )

    max_z = max([lyr.get("depth_bot", 5.0) for lyr in layers])

    fig.update_layout(
        title="<b>Kolom Stratigrafi Lapisan Tanah</b>",
        barmode="stack",
        yaxis=dict(
            title="<b>Kedalaman (m)</b>",
            autorange="reversed",
            range=[max_z, 0.0],
            gridcolor="#1E293B"
        ),
        xaxis=dict(showticklabels=False),
        paper_bgcolor="rgba(15, 23, 42, 0.7)",
        plot_bgcolor="rgba(11, 19, 41, 0.85)",
        font=dict(color="#F8FAFC", family="Plus Jakarta Sans"),
        margin=dict(l=50, r=20, t=50, b=40),
        height=480,
        showlegend=False
    )

    return fig


# DATA CONTOH NYATA BORE LOG UNDIP (STA. 3+000 MANGKANG BH. 4)
SAMPLE_BORELOG_UNDIP_BH4 = [
    {
        "depth_top": 0.0, "depth_bot": 1.0, "n1": 1, "n2": 2, "n3": 1, "n_spt": 3,
        "soil_type": "LANAU Kelempungan",
        "konsistensi": "Lunak",
        "deskripsi": "Lunak, warna coklat abu-abu",
        "phi": 0.0, "c": 25.0, "gamma": 16.0, "gamma_sat": 17.5, "color": "#6366F1", "interval_str": "0.00 - 1.00 m"
    },
    {
        "depth_top": 1.0, "depth_bot": 7.0, "n1": 0, "n2": 1, "n3": 0, "n_spt": 1,
        "soil_type": "LEMPUNG Kepasiran Halus",
        "konsistensi": "Sangat Lunak",
        "deskripsi": "Sangat lunak, warna abu-abu (Muka air tanah -2.00 m)",
        "phi": 0.0, "c": 12.0, "gamma": 15.0, "gamma_sat": 16.5, "color": "#7C3AED", "interval_str": "1.00 - 7.00 m"
    },
    {
        "depth_top": 7.0, "depth_bot": 15.5, "n1": 1, "n2": 1, "n3": 1, "n_spt": 2,
        "soil_type": "LEMPUNG",
        "konsistensi": "Sangat Lunak s/d Lunak",
        "deskripsi": "Sangat lunak sampai lunak, warna abu-abu",
        "phi": 0.0, "c": 18.0, "gamma": 15.8, "gamma_sat": 17.2, "color": "#6366F1", "interval_str": "7.00 - 15.50 m"
    },
    {
        "depth_top": 15.5, "depth_bot": 20.0, "n1": 3, "n2": 4, "n3": 5, "n_spt": 9,
        "soil_type": "LEMPUNG",
        "konsistensi": "Lunak s/d Teguh",
        "deskripsi": "Lunak, warna abu-abu",
        "phi": 8.0, "c": 50.0, "gamma": 17.8, "gamma_sat": 19.2, "color": "#0EA5E9", "interval_str": "15.50 - 20.00 m"
    },
    {
        "depth_top": 20.0, "depth_bot": 22.5, "n1": 4, "n2": 6, "n3": 6, "n_spt": 12,
        "soil_type": "LEMPUNG Kepasiran Halus",
        "konsistensi": "Lunak s/d Teguh",
        "deskripsi": "Lunak sampai teguh, warna abu-abu",
        "phi": 10.0, "c": 70.0, "gamma": 18.2, "gamma_sat": 19.8, "color": "#0EA5E9", "interval_str": "20.00 - 22.50 m"
    },
    {
        "depth_top": 22.5, "depth_bot": 25.0, "n1": 5, "n2": 6, "n3": 7, "n_spt": 13,
        "soil_type": "LEMPUNG",
        "konsistensi": "Teguh (Stiff)",
        "deskripsi": "Teguh, warna abu-abu",
        "phi": 11.0, "c": 80.0, "gamma": 18.5, "gamma_sat": 20.0, "color": "#0D9488", "interval_str": "22.50 - 25.00 m"
    }
]
