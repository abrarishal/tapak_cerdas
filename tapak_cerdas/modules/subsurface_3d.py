"""
=============================================================================
TAPAK CERDAS - ENGINE VISUALISASI 3D LAPISAN TANAH & DATA INVESTIGASI (SPT/CPT)
=============================================================================
File: modules/subsurface_3d.py
Deskripsi: Membangun model blok geologi bawah permukaan (Subsurface 3D Geological Block)
           berdasarkan data pemboran N-SPT dan uji penetrasi sondir CPT sesuai
           referensi dokumen geoteknik profesional (SNI / ASTM).
=============================================================================
"""

import math
import numpy as np
import plotly.graph_objects as go

def _get_soil_layer_color(soil_name, n_spt=None):
    """Mengembalikan warna heksadesimal standar geoteknik untuk jenis tanah."""
    name = (soil_name or "").lower()
    if "pasir padat" in name or "gravel" in name or "kerikil" in name:
        return "#D97706"  # Amber / Dark Sand
    elif "pasir" in name:
        return "#FBBF24"  # Gold / Sand
    elif "lanau" in name or "silt" in name:
        return "#14B8A6"  # Teal / Silt
    elif "organik" in name or "gambut" in name:
        return "#78350F"  # Dark Brown Organic
    elif "keras" in name or "padas" in name or "rock" in name:
        return "#991B1B"  # Dark Red Bedrock
    elif "sangat lunak" in name:
        return "#8B5CF6"  # Soft Clay Purple
    elif "lunak" in name:
        return "#6366F1"  # Medium Clay Indigo
    elif "kaku" in name or "stiff" in name:
        return "#0284C7"  # Stiff Clay Blue
    else:
        # Default lempung sedang
        if n_spt is not None:
            if n_spt < 4:
                return "#8B5CF6"
            elif n_spt <= 10:
                return "#6366F1"
            elif n_spt <= 25:
                return "#0284C7"
            else:
                return "#0D9488"
        return "#0284C7"


def plot_subsurface_block_3d(
    layers,
    gw_depth=1.5,
    borehole_id="BH-01",
    test_type="SPT",
    cpt_points=None,
    block_width=6.0,
    block_length=6.0
):
    """
    Menghasilkan visualisasi 3D Blok Geologi Bawah Permukaan (Subsurface 3D Geological Block):
    - Tampilan blok tanah isometrik berdimensi block_width x block_length x total_depth
    - Lapisan-lapisan tanah dengan warna dan tekstur visual pembeda
    - Muka air tanah (GWL) sebagai bidang horizontal semi-transparan berwarna biru muda
    - Kolom penyelidikan bor/sondir 3D dengan segmen nilai N-SPT atau qc terhadap kedalaman
    - Interaktif 360 derajat, rotasi, zoom, pan, dan inspeksi kedalaman
    """
    fig = go.Figure()

    if not layers or len(layers) == 0:
        # Dummy layer jika data kosong
        layers = [
            {"depth_top": 0.0, "depth_bot": 2.0, "soil_type": "Tanah Urug / Lempung Lunak", "n_spt": 3},
            {"depth_top": 2.0, "depth_bot": 5.0, "soil_type": "Lempung Sedang / Teguh", "n_spt": 8},
            {"depth_top": 5.0, "depth_bot": 8.0, "soil_type": "Pasir Berlanau Sedang", "n_spt": 18},
            {"depth_top": 8.0, "depth_bot": 12.0, "soil_type": "Pasir Padat / Kerikil", "n_spt": 35}
        ]

    max_depth = max(float(l.get("depth_bot", 6.0)) for l in layers)
    half_w = block_width / 2.0
    half_l = block_length / 2.0

    # 1. GENERATE LAPISAN TANAH 3D (SOLID STRATA BLOCKS)
    for idx, lyr in enumerate(layers):
        z_top = -float(lyr.get("depth_top", 0.0))
        z_bot = -float(lyr.get("depth_bot", z_top - 1.5))
        s_name = lyr.get("soil_type", lyr.get("deskripsi", "Lapisan Tanah"))
        n_val = lyr.get("n_spt", None)
        layer_col = lyr.get("color") or _get_soil_layer_color(s_name, n_val)

        # 8 titik sudut prisma lapisan tanah
        x_pts = [-half_w, half_w, half_w, -half_w, -half_w, half_w, half_w, -half_w]
        y_pts = [-half_l, -half_l, half_l, half_l, -half_l, -half_l, half_l, half_l]
        z_pts = [z_bot, z_bot, z_bot, z_bot, z_top, z_top, z_top, z_top]

        # 12 segitiga untuk 6 sisi balok
        i_idx = [7, 0, 0, 0, 4, 4, 6, 6, 4, 0, 3, 2]
        j_idx = [3, 4, 1, 2, 5, 6, 5, 2, 0, 1, 6, 3]
        k_idx = [0, 7, 2, 3, 6, 7, 1, 1, 5, 5, 7, 6]

        thick = abs(z_top - z_bot)
        hover_info = (
            f"<b>Lapisan #{idx+1}: {s_name}</b><br>"
            f"Kedalaman: {-z_top:.2f} - {-z_bot:.2f} m (Tebal: {thick:.2f} m)<br>"
            f"N-SPT: {n_val if n_val is not None else '-'}<br>"
            f"Kohesi cu: {lyr.get('cu', lyr.get('c', '-'))} kPa<br>"
            f"Sudut Geser φ: {lyr.get('phi', lyr.get('phi_eff', '-'))}°"
        )

        fig.add_trace(go.Mesh3d(
            x=x_pts, y=y_pts, z=z_pts,
            i=i_idx, j=j_idx, k=k_idx,
            color=layer_col,
            opacity=0.72,
            name=f"Lapisan {idx+1}: {s_name[:20]}",
            hoverinfo="text",
            hovertext=hover_info,
            flatshading=True
        ))

        # Garis tepi pemisah antar lapisan (Stratigraphy Wireframe Lines)
        for z_edge in [z_top, z_bot]:
            fig.add_trace(go.Scatter3d(
                x=[-half_w, half_w, half_w, -half_w, -half_w],
                y=[-half_l, -half_l, half_l, half_l, -half_l],
                z=[z_edge, z_edge, z_edge, z_edge, z_edge],
                mode="lines",
                line=dict(color="#334155", width=2.5),
                showlegend=False,
                hoverinfo="skip"
            ))

    # 2. BIDANG MUKA AIR TANAH 3D (GROUNDWATER TABLE / GWL)
    if gw_depth is not None and gw_depth <= max_depth:
        z_gw = -float(gw_depth)
        x_gw = [-half_w * 1.15, half_w * 1.15, half_w * 1.15, -half_w * 1.15]
        y_gw = [-half_l * 1.15, -half_l * 1.15, half_l * 1.15, half_l * 1.15]
        z_gw_pts = [z_gw, z_gw, z_gw, z_gw]

        fig.add_trace(go.Mesh3d(
            x=x_gw, y=y_gw, z=z_gw_pts,
            i=[0, 0], j=[1, 2], k=[2, 3],
            color="#38BDF8",
            opacity=0.38,
            name=f"Muka Air Tanah (GWL = -{gw_depth:.2f} m)",
            hoverinfo="text",
            hovertext=f"<b>Muka Air Tanah (GWL)</b><br>Kedalaman: {gw_depth:.2f} m dari Muka Tanah"
        ))

        # Simbol Segitiga MAT
        fig.add_trace(go.Scatter3d(
            x=[0.0], y=[0.0], z=[z_gw],
            mode="markers+text",
            marker=dict(size=8, color="#0284C7", symbol="diamond"),
            text=[f" ∇ GWL -{gw_depth:.2f} m"],
            textposition="top right",
            textfont=dict(color="#38BDF8", size=11),
            name="Titik Elevasi GWL",
            showlegend=False
        ))

    # 3. TITIK INVESTIGASI 3D (BOREHOLE / CPT VERTICAL COLUMN)
    # Lokasi titik bor di tengah koordinat (0, 0)
    col_x, col_y = 0.0, 0.0

    if test_type == "SPT" or cpt_points is None:
        # Tampilkan kolom pemboran N-SPT dengan indikator warna nilai penetrasi
        for lyr in layers:
            z_t = -float(lyr.get("depth_top", 0.0))
            z_b = -float(lyr.get("depth_bot", z_t - 1.5))
            n_spt = int(lyr.get("n_spt", 10))

            # Warna penetrasi: Merah (<4), Oranye (4-10), Kuning (10-25), Hijau (25-40), Biru (>40)
            if n_spt < 4:
                pipe_color = "#EF4444"
                dens_desc = "Sangat Lunak / Sangat Lepas"
            elif n_spt <= 10:
                pipe_color = "#F97316"
                dens_desc = "Lunak s/d Sedang"
            elif n_spt <= 25:
                pipe_color = "#FBBF24"
                dens_desc = "Teguh / Sedang"
            elif n_spt <= 40:
                pipe_color = "#10B981"
                dens_desc = "Kaku / Padat"
            else:
                pipe_color = "#3B82F6"
                dens_desc = "Sangat Keras / Sangat Padat"

            fig.add_trace(go.Scatter3d(
                x=[col_x, col_x],
                y=[col_y, col_y],
                z=[z_t, z_b],
                mode="lines+markers",
                line=dict(color=pipe_color, width=12),
                marker=dict(size=[6, 6], color=pipe_color),
                name=f"{borehole_id} N-SPT={n_spt}",
                hoverinfo="text",
                hovertext=(
                    f"<b>{borehole_id} (ASTM D1586)</b><br>"
                    f"Kedalaman: {-z_t:.2f} - {-z_b:.2f} m<br>"
                    f"N-SPT: <b>{n_spt} pukulan/30cm</b> ({dens_desc})<br>"
                    f"Tanah: {lyr.get('soil_type', '-')}"
                ),
                showlegend=(lyr == layers[0])
            ))
    else:
        # Tampilkan profil CPT 3D
        cpt_depths = [-float(pt.get("depth", 0.0)) for pt in cpt_points]
        cpt_qc = [float(pt.get("qc", 0.0)) for pt in cpt_points]
        cpt_soil = [pt.get("soil_type", "Tanah") for pt in cpt_points]

        fig.add_trace(go.Scatter3d(
            x=[col_x] * len(cpt_depths),
            y=[col_y] * len(cpt_depths),
            z=cpt_depths,
            mode="lines+markers",
            line=dict(color="#06B6D4", width=6),
            marker=dict(
                size=5,
                color=cpt_qc,
                colorscale="Viridis",
                colorbar=dict(title="qc (kg/cm²)", len=0.6, x=0.9),
                showscale=True
            ),
            name="Sondir CPT (qc)",
            hoverinfo="text",
            hovertext=[
                f"Kedalaman: {-z:.2f} m<br>qc: {qc:.1f} kg/cm² ({qc*98.07:.0f} kPa)<br>Jenis: {s}"
                for z, qc, s in zip(cpt_depths, cpt_qc, cpt_soil)
            ]
        ))

    # Rig / Penanda Permukaan Titik Penyelidikan
    fig.add_trace(go.Scatter3d(
        x=[col_x], y=[col_y], z=[0.8],
        mode="markers+text",
        marker=dict(size=10, color="#EF4444", symbol="cross"),
        text=[f"📍 {borehole_id} (EL ±0.00)"],
        textposition="top center",
        textfont=dict(color="#FFFFFF", size=12),
        name="Titik Investigasi",
        showlegend=True
    ))

    # Tiang Rangka Pemboran / Alat Sondir (Derrick Stand)
    fig.add_trace(go.Scatter3d(
        x=[col_x - 0.4, col_x, col_x + 0.4, col_x],
        y=[col_y - 0.4, col_y + 0.4, col_y - 0.4, col_y],
        z=[0.0, 0.8, 0.0, 0.8],
        mode="lines",
        line=dict(color="#E2E8F0", width=3),
        showlegend=False,
        hoverinfo="skip"
    ))

    # 4. LAYOUT & STYLING DARK SLATE GEOTECHNICAL
    fig.update_layout(
        title=dict(
            text=f"<b>🌍 Model Blok 3D Bawah Permukaan: Penyelidikan {borehole_id} ({test_type})</b>",
            font=dict(size=14, color="#F8FAFC", family="Plus Jakarta Sans")
        ),
        scene=dict(
            xaxis=dict(
                title="Lebar X (m)",
                backgroundcolor="#090E17",
                gridcolor="#1E293B",
                showbackground=True,
                color="#94A3B8",
                range=[-half_w * 1.2, half_w * 1.2]
            ),
            yaxis=dict(
                title="Panjang Y (m)",
                backgroundcolor="#090E17",
                gridcolor="#1E293B",
                showbackground=True,
                color="#94A3B8",
                range=[-half_l * 1.2, half_l * 1.2]
            ),
            zaxis=dict(
                title="Elevasi Z (m)",
                backgroundcolor="#090E17",
                gridcolor="#1E293B",
                showbackground=True,
                color="#94A3B8",
                range=[-max_depth - 1.0, 1.5]
            ),
            aspectratio=dict(x=1.0, y=1.0, z=1.35),
            camera=dict(
                eye=dict(x=1.8, y=-1.8, z=1.1)
            )
        ),
        paper_bgcolor="rgba(15, 23, 42, 0.95)",
        margin=dict(l=10, r=10, t=45, b=10),
        height=580,
        showlegend=True,
        legend=dict(
            font=dict(color="#CBD5E1", size=10),
            bgcolor="rgba(15, 23, 42, 0.8)",
            bordercolor="#334155"
        )
    )

    return fig
