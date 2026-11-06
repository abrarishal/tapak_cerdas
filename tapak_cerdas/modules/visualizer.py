"""
=============================================================================
TAPAK CERDAS - VISUALISASI GAMBAR TEKNIK CAD & SIMULASI 3D INTERAKTIF
=============================================================================
File: modules/visualizer.py
Deskripsi: Modul rendering grafis interaktif Geoteknik & Struktur:
           - Model 3D Interaktif CAD (Bujur Sangkar, Persegi Panjang, Lingkaran 3D Silinder, Strip/Jalur Bata)
           - Gambar Kerja 2D Tampak Atas (Plan View) & Penampang Potongan Melintang
           - Kontur Sebaran Tegangan Boussinesq (Isobar Tekanan Tanah)
           - Speedometer Gauge Faktor Keamanan (SF)
           - Profil Stratigrafi Lapisan Tanah Dinamis
=============================================================================
"""

import math
import numpy as np
import plotly.graph_objects as go


# =============================================================================
# 1. SIMULASI 3D INTERAKTIF CAD FONDASI TELAPAK (PLOTLY 3D MESH)
# =============================================================================

def _make_box_mesh(x0, x1, y0, y1, z0, z1, color='#38BDF8', opacity=0.92, name="Blok"):
    """Membuat mesh 3D berbentuk balok kuboid."""
    x = [x0, x1, x1, x0, x0, x1, x1, x0]
    y = [y0, y0, y1, y1, y0, y0, y1, y1]
    z = [z0, z0, z0, z0, z1, z1, z1, z1]
    i = [7, 0, 0, 0, 4, 4, 6, 6, 4, 0, 3, 2]
    j = [3, 4, 1, 2, 5, 6, 5, 2, 0, 1, 6, 3]
    k = [0, 7, 2, 3, 6, 7, 1, 1, 5, 5, 7, 6]
    return go.Mesh3d(
        x=x, y=y, z=z, i=i, j=j, k=k,
        color=color, opacity=opacity,
        flatshading=True, name=name,
        hoverinfo="name"
    )


def _make_cylinder_mesh(r, z0, z1, n=36, color='#00E5FF', opacity=0.92, name="Silinder"):
    """Membuat mesh 3D berbentuk silinder bundar (untuk Fondasi Lingkaran)."""
    theta = np.linspace(0, 2 * np.pi, n, endpoint=False)
    x = list(r * np.cos(theta)) + list(r * np.cos(theta)) + [0, 0]
    y = list(r * np.sin(theta)) + list(r * np.sin(theta)) + [0, 0]
    z = [z0] * n + [z1] * n + [z0, z1]
    top_c = 2 * n + 1
    bot_c = 2 * n
    i, j, k = [], [], []
    for idx in range(n):
        nxt = (idx + 1) % n
        # dinding samping (2 segitiga per segmen)
        i.append(idx); j.append(nxt); k.append(idx + n)
        i.append(nxt); j.append(nxt + n); k.append(idx + n)
        # tutup atas
        i.append(top_c); j.append(idx + n); k.append(nxt + n)
        # tutup bawah
        i.append(bot_c); j.append(nxt); k.append(idx)
        
    return go.Mesh3d(
        x=x, y=y, z=z, i=i, j=j, k=k,
        color=color, opacity=opacity,
        flatshading=True, name=name,
        hoverinfo="name"
    )


def plot_foundation_3d(shape, B, L, Df, dw, P_kN, hf=0.40, soil_name="Tanah Lempung Sedang"):
    """
    Menghasilkan model 3D Interaktif CAD yang menyesuaikan dengan bentuk fondasi yang dipilih:
    - Bujur Sangkar: Pelat balok persegi sama sisi (B x B)
    - Persegi Panjang: Pelat balok memanjang (B x L)
    - Lingkaran: SILINDER ASLI 3D berdiameter D = B
    - Menerus / Jalur: Pelat lajur beton panjang dengan dinding bata merah di atasnya
    """
    fig = go.Figure()

    # Koordinat vertikal
    z_bot = -Df
    z_top = -Df + hf
    z_col_top = 0.50  # Kolom mencuat 0.5m di atas permukaan tanah

    # Batas grid tanah
    r_ground = max(3.0, max(B, L) * 1.5)

    # 1. Permukaan Tanah 3D (Ground Surface z = 0)
    xg = [-r_ground, r_ground, r_ground, -r_ground]
    yg = [-r_ground, -r_ground, r_ground, r_ground]
    zg = [0, 0, 0, 0]
    fig.add_trace(go.Mesh3d(
        x=xg, y=yg, z=zg,
        i=[0, 0], j=[1, 2], k=[2, 3],
        color="#15803D", opacity=0.18,
        name="Permukaan Tanah (±0.00)"
    ))

    # 2. Bidang Muka Air Tanah 3D (z = -dw)
    if dw <= (Df + 2.0):
        fig.add_trace(go.Mesh3d(
            x=xg, y=yg, z=[-dw, -dw, -dw, -dw],
            i=[0, 0], j=[1, 2], k=[2, 3],
            color="#0284C7", opacity=0.22,
            name=f"Muka Air Tanah (dw = -{dw:.2f} m)"
        ))

    # 3. Elemen Geometri Fondasi Sesuai Bentuk Terpilih
    if "Lingkaran" in shape:
        radius = B / 2.0
        # Pelat Fondasi Silinder 3D
        fig.add_trace(_make_cylinder_mesh(
            r=radius, z0=z_bot, z1=z_top,
            color="#00E5FF", opacity=0.92,
            name=f"Fondasi Silinder Lingkaran (Ø = {B:.2f} m, h = {hf:.2f} m)"
        ))
        # Kolom Silinder di atasnya
        col_r = min(0.25, radius * 0.45)
        fig.add_trace(_make_cylinder_mesh(
            r=col_r, z0=z_top, z1=z_col_top,
            color="#38BDF8", opacity=0.95,
            name="Kolom Pedestal Bulat"
        ))

    elif "Persegi Panjang" in shape:
        x0, x1 = -B / 2.0, B / 2.0
        y0, y1 = -L / 2.0, L / 2.0
        fig.add_trace(_make_box_mesh(
            x0, x1, y0, y1, z_bot, z_top,
            color="#38BDF8", opacity=0.92,
            name=f"Fondasi Telapak Persegi Panjang ({B:.2f} x {L:.2f} m)"
        ))
        # Kolom Pedestal Persegi
        cw_x = min(0.35, B * 0.35)
        cw_y = min(0.50, L * 0.35)
        fig.add_trace(_make_box_mesh(
            -cw_x/2, cw_x/2, -cw_y/2, cw_y/2, z_top, z_col_top,
            color="#0284C7", opacity=0.95,
            name="Kolom Pedestal Persegi"
        ))

    elif "Menerus" in shape or "Jalur" in shape:
        strip_len = 4.5
        x0, x1 = -B / 2.0, B / 2.0
        y0, y1 = -strip_len / 2.0, strip_len / 2.0
        # Pelat Lajur Beton Bawah
        fig.add_trace(_make_box_mesh(
            x0, x1, y0, y1, z_bot, z_top,
            color="#0284C7", opacity=0.90,
            name=f"Pondasi Lajur Beton (Lebar B = {B:.2f} m)"
        ))
        # Dinding Pasangan Bata Merah / Sloof di atas fondasi lajur
        wall_w = 0.25
        fig.add_trace(_make_box_mesh(
            -wall_w/2, wall_w/2, y0, y1, z_top, z_col_top,
            color="#EF4444", opacity=0.88,
            name="Dinding Pasangan Bata / Sloof"
        ))

    else:  # Bujur Sangkar
        x0, x1 = -B / 2.0, B / 2.0
        y0, y1 = -B / 2.0, B / 2.0
        fig.add_trace(_make_box_mesh(
            x0, x1, y0, y1, z_bot, z_top,
            color="#00E5FF", opacity=0.92,
            name=f"Fondasi Telapak Bujur Sangkar ({B:.2f} x {B:.2f} m)"
        ))
        col_w = min(0.40, B * 0.3)
        fig.add_trace(_make_box_mesh(
            -col_w/2, col_w/2, -col_w/2, col_w/2, z_top, z_col_top,
            color="#38BDF8", opacity=0.95,
            name="Kolom Pedestal Beton"
        ))

    # 4. Panah Vektor Gaya Aksial P (Warna Emas / Merah)
    p_arrow_top = z_col_top + 0.9
    fig.add_trace(go.Scatter3d(
        x=[0, 0], y=[0, 0], z=[p_arrow_top, z_col_top],
        mode="lines+markers",
        line=dict(color="#FBBF24", width=8),
        marker=dict(size=[0, 10], color="#FBBF24", symbol="diamond"),
        name=f"Vektor Beban Aksial P = {P_kN:.1f} kN",
        hovertext=[f"P = {P_kN:.1f} kN (~{P_kN/9.81:.1f} Ton)", "Titik Masuk Beban Kolom"]
    ))

    # 5. Gelembung Sebaran Tegangan Boussinesq Bawah (Wireframe Glow)
    theta_b = np.linspace(0, 2*np.pi, 24)
    for depth_step in [0.8, 1.6, 2.4]:
        r_step = (B / 2.0) + depth_step * 0.4
        xb = r_step * np.cos(theta_b)
        yb = r_step * np.sin(theta_b)
        zb = [z_bot - depth_step] * len(theta_b)
        fig.add_trace(go.Scatter3d(
            x=xb, y=yb, z=zb,
            mode="lines",
            line=dict(color="rgba(245, 158, 11, 0.4)", width=3, dash="dot"),
            name=f"Isobar Tekanan Bawah Fondasi (z = -{Df+depth_step:.1f}m)",
            hoverinfo="name"
        ))

    # Layout 3D Styling (Dark Slate Blueprint)
    fig.update_layout(
        title=dict(
            text=f"<b>🏛️ Model 3D Interaktif CAD: Fondasi {shape.split('(')[0]} (Bisa Diputar 360°)</b>",
            font=dict(size=14, color="#F8FAFC", family="Plus Jakarta Sans")
        ),
        scene=dict(
            xaxis=dict(title="Sumbu X (m)", backgroundcolor="#081122", gridcolor="#1E293B", showbackground=True, color="#94A3B8"),
            yaxis=dict(title="Sumbu Y (m)", backgroundcolor="#081122", gridcolor="#1E293B", showbackground=True, color="#94A3B8"),
            zaxis=dict(title="Elevasi Z (m)", backgroundcolor="#081122", gridcolor="#1E293B", showbackground=True, color="#94A3B8"),
            aspectmode="data",
            camera=dict(
                eye=dict(x=1.6, y=-1.8, z=1.2)
            )
        ),
        paper_bgcolor="rgba(15, 23, 42, 0.85)",
        margin=dict(l=10, r=10, t=45, b=10),
        height=520,
        showlegend=True,
        legend=dict(
            font=dict(color="#CBD5E1", size=10),
            bgcolor="rgba(15, 23, 42, 0.7)",
            bordercolor="#334155"
        )
    )

    return fig


# =============================================================================
# 2. GAMBAR KERJA 2D TAMPAK ATAS (PLAN VIEW & REBAR LAYOUT)
# =============================================================================

def plot_foundation_plan_view(shape, B, L, hf=0.40, P_kN=350.0):
    """
    Menggambar tampak atas (Plan View) teknis 2D lengkap dengan penulangan dan dimensi:
    - Lingkaran: Tampak lingkaran sempurna dengan tulangan sengkang melingkar dan jari-jari radial.
    - Bujur Sangkar: Tampak bujur sangkar dengan jaring tulangan 2 arah.
    - Persegi Panjang: Tampak persegi panjang dengan tulangan memanjang dan melintang.
    - Menerus / Jalur: Tampak lajur memanjang dengan arsiran dinding bata.
    """
    fig = go.Figure()
    
    limit_xy = max(2.5, max(B, L) * 0.85)

    if "Lingkaran" in shape:
        radius = B / 2.0
        theta = np.linspace(0, 2*np.pi, 100)
        xc = radius * np.cos(theta)
        yc = radius * np.sin(theta)
        
        # Garis tepi pondasi lingkaran
        fig.add_trace(go.Scatter(
            x=xc, y=yc, fill="toself",
            fillcolor="rgba(6, 182, 212, 0.15)",
            line=dict(color="#00E5FF", width=3.5),
            name=f"Tepi Fondasi Lingkaran (Ø = {B:.2f} m)"
        ))
        
        # Tulangan sengkang konsentris
        for r_bar in [radius * 0.45, radius * 0.75]:
            fig.add_trace(go.Scatter(
                x=r_bar * np.cos(theta), y=r_bar * np.sin(theta),
                mode="lines", line=dict(color="#38BDF8", width=1.5, dash="dash"),
                showlegend=False, hoverinfo="skip"
            ))
            
        # 8 Jari-jari tulangan radial
        for ang in np.linspace(0, 2*np.pi, 8, endpoint=False):
            fig.add_trace(go.Scatter(
                x=[0, radius * 0.95 * np.cos(ang)],
                y=[0, radius * 0.95 * np.sin(ang)],
                mode="lines", line=dict(color="#60A5FA", width=1.5),
                showlegend=False, hoverinfo="skip"
            ))
            
        # Kolom bulat di tengah
        col_r = min(0.25, radius * 0.4)
        fig.add_trace(go.Scatter(
            x=col_r * np.cos(theta), y=col_r * np.sin(theta),
            fill="toself", fillcolor="rgba(244, 63, 94, 0.4)",
            line=dict(color="#F43F5E", width=2.5),
            name="Kolom Pedestal Ø40 cm"
        ))
        
        # Dimensi Diameter
        fig.add_annotation(
            x=0, y=-radius - 0.35,
            text=f"<b>DIAMETER D = {B:.2f} m (Luas = {math.pi*radius**2:.2f} m²)</b>",
            showarrow=False,
            font=dict(color="#00E5FF", size=12, family="Plus Jakarta Sans"),
            bgcolor="rgba(15, 23, 42, 0.8)", bordercolor="#00E5FF", borderwidth=1
        )

    elif "Persegi Panjang" in shape:
        x0, x1 = -B / 2.0, B / 2.0
        y0, y1 = -L / 2.0, L / 2.0
        
        # Blok Fondasi Persegi Panjang
        fig.add_shape(
            type="rect", x0=x0, x1=x1, y0=y0, y1=y1,
            fillcolor="rgba(56, 189, 248, 0.15)",
            line=dict(color="#38BDF8", width=3.5)
        )
        
        # Jaring tulangan memanjang & melintang
        for xi in np.linspace(x0 + 0.1, x1 - 0.1, 7):
            fig.add_shape(type="line", x0=xi, x1=xi, y0=y0 + 0.1, y1=y1 - 0.1, line=dict(color="#60A5FA", width=1.2, dash="dot"))
        for yi in np.linspace(y0 + 0.1, y1 - 0.1, 9):
            fig.add_shape(type="line", x0=x0 + 0.1, x1=x1 - 0.1, y0=yi, y1=yi, line=dict(color="#60A5FA", width=1.2, dash="dot"))
            
        # Kolom Persegi
        col_w = min(0.35, B * 0.4)
        col_l = min(0.50, L * 0.4)
        fig.add_shape(
            type="rect", x0=-col_w/2, x1=col_w/2, y0=-col_l/2, y1=col_l/2,
            fillcolor="rgba(244, 63, 94, 0.4)", line=dict(color="#F43F5E", width=2.5)
        )
        
        fig.add_annotation(
            x=0, y=y1 + 0.35,
            text=f"<b>LEBAR B = {B:.2f} m &times; PANJANG L = {L:.2f} m (Luas = {B*L:.2f} m²)</b>",
            showarrow=False,
            font=dict(color="#38BDF8", size=12, family="Plus Jakarta Sans"),
            bgcolor="rgba(15, 23, 42, 0.8)", bordercolor="#38BDF8", borderwidth=1
        )

    elif "Menerus" in shape or "Jalur" in shape:
        strip_len = 3.8
        x0, x1 = -B / 2.0, B / 2.0
        y0, y1 = -strip_len / 2.0, strip_len / 2.0
        
        fig.add_shape(
            type="rect", x0=x0, x1=x1, y0=y0, y1=y1,
            fillcolor="rgba(16, 185, 129, 0.15)",
            line=dict(color="#10B981", width=3.5)
        )
        
        # Garis dinding bata di tengah
        wall_w = 0.25
        fig.add_shape(
            type="rect", x0=-wall_w/2, x1=wall_w/2, y0=y0, y1=y1,
            fillcolor="rgba(239, 68, 68, 0.35)",
            line=dict(color="#EF4444", width=2.5)
        )
        
        fig.add_annotation(
            x=0, y=y1 + 0.35,
            text=f"<b>FONDASI JALUR / MENERUS (Lebar B = {B:.2f} m, Dinding t = 25 cm)</b>",
            showarrow=False,
            font=dict(color="#10B981", size=12, family="Plus Jakarta Sans"),
            bgcolor="rgba(15, 23, 42, 0.8)", bordercolor="#10B981", borderwidth=1
        )

    else:  # Bujur Sangkar
        x0, x1 = -B / 2.0, B / 2.0
        y0, y1 = -B / 2.0, B / 2.0
        
        fig.add_shape(
            type="rect", x0=x0, x1=x1, y0=y0, y1=y1,
            fillcolor="rgba(0, 229, 255, 0.15)",
            line=dict(color="#00E5FF", width=3.5)
        )
        
        for xi in np.linspace(x0 + 0.1, x1 - 0.1, 7):
            fig.add_shape(type="line", x0=xi, x1=xi, y0=y0 + 0.1, y1=y1 - 0.1, line=dict(color="#38BDF8", width=1.2, dash="dot"))
        for yi in np.linspace(y0 + 0.1, y1 - 0.1, 7):
            fig.add_shape(type="line", x0=x0 + 0.1, x1=x1 - 0.1, y0=yi, y1=yi, line=dict(color="#38BDF8", width=1.2, dash="dot"))
            
        col_w = min(0.40, B * 0.35)
        fig.add_shape(
            type="rect", x0=-col_w/2, x1=col_w/2, y0=-col_w/2, y1=col_w/2,
            fillcolor="rgba(244, 63, 94, 0.4)", line=dict(color="#F43F5E", width=2.5)
        )
        
        fig.add_annotation(
            x=0, y=y1 + 0.35,
            text=f"<b>BUJUR SANGKAR: B = {B:.2f} m &times; L = {B:.2f} m (Luas = {B*B:.2f} m²)</b>",
            showarrow=False,
            font=dict(color="#00E5FF", size=12, family="Plus Jakarta Sans"),
            bgcolor="rgba(15, 23, 42, 0.8)", bordercolor="#00E5FF", borderwidth=1
        )

    # Layout Blueprint Dark Mode
    fig.update_layout(
        title=dict(
            text=f"<b>📐 Tampak Atas (Plan View) & Rencana Tulangan: {shape.split('(')[0]}</b>",
            font=dict(size=14, color="#F8FAFC", family="Plus Jakarta Sans")
        ),
        xaxis=dict(
            title="Lebar X (meter)",
            range=[-limit_xy, limit_xy],
            gridcolor="#1E293B",
            zerolinecolor="#334155",
            color="#94A3B8"
        ),
        yaxis=dict(
            title="Panjang Y (meter)",
            range=[-limit_xy, limit_xy],
            gridcolor="#1E293B",
            zerolinecolor="#334155",
            color="#94A3B8",
            scaleanchor="x",
            scaleratio=1
        ),
        plot_bgcolor="#0A1428",
        paper_bgcolor="rgba(15, 23, 42, 0.85)",
        height=480,
        margin=dict(l=40, r=40, t=50, b=40)
    )

    return fig


# =============================================================================
# 3. KONTUR TEGANGAN BOUSSINESQ (SEBARAN TEKANAN DALAM TANAH)
# =============================================================================

def plot_boussinesq_stress_bulb(B, L, Df, q_contact, shape="Bujur Sangkar"):
    """
    Menghitung dan memvisualisasikan kontur sebaran tegangan vertikal tambahan (Δσz)
    di bawah dasar pondasi menggunakan rumus Geoteknik Boussinesq (Isobar Tekanan Tanah).
    """
    fig = go.Figure()

    # Domain analisis di bawah dasar pondasi
    x = np.linspace(-B * 2.2, B * 2.2, 70)
    z = np.linspace(0.05, max(3.5, B * 2.8), 70)
    X, Z = np.meshgrid(x, z)
    
    # Perhitungan Boussinesq 2D untuk pondasi dangkal
    R2 = X**2 + Z**2
    # Faktor intensitas tegangan Boussinesq
    I_z = (3.0 / (2.0 * np.pi)) * (Z**3 / (R2**(5.0/2.0) + 1e-6))
    # Tegangan aktual sigma_z (kPa)
    sigma_z = q_contact * B * I_z
    sigma_z = np.clip(sigma_z, 0, q_contact * 1.1)

    # Plot Kontur Turbo / Heatmap Tekanan
    fig.add_trace(go.Contour(
        x=x, y=-Df - z, z=sigma_z,
        colorscale="Turbo",
        contours=dict(
            start=round(q_contact * 0.1, 1),
            end=round(q_contact * 0.95, 1),
            size=round(q_contact * 0.1, 1),
            showlabels=True,
            labelfont=dict(size=10, color="#FFFFFF")
        ),
        colorbar=dict(
            title=dict(text="Tegangan Δσz (kPa)", font=dict(color="#CBD5E1", size=11)),
            tickfont=dict(color="#94A3B8")
        ),
        name="Isobar Tegangan Tanah"
    ))

    # Gambarkan blok dasar pondasi di atas kontur
    fig.add_shape(
        type="rect",
        x0=-B/2.0, x1=B/2.0,
        y0=-Df, y1=-Df + 0.35,
        fillcolor="#00E5FF",
        line=dict(color="#FFFFFF", width=2.5)
    )
    fig.add_annotation(
        x=0, y=-Df + 0.18,
        text=f"<b>Dasar Fondasi (q = {q_contact:.1f} kPa)</b>",
        showarrow=False,
        font=dict(color="#0B1329", size=11, family="Plus Jakarta Sans")
    )

    fig.update_layout(
        title=dict(
            text="<b>🌊 Gelembung Sebaran Tegangan Boussinesq (Isobar Tekanan Tanah di Bawah Pondasi)</b>",
            font=dict(size=14, color="#F8FAFC", family="Plus Jakarta Sans")
        ),
        xaxis=dict(title="Jarak Horizontal x (m)", gridcolor="#1E293B", color="#94A3B8"),
        yaxis=dict(title="Kedalaman Tanah z (m)", gridcolor="#1E293B", color="#94A3B8"),
        plot_bgcolor="#081122",
        paper_bgcolor="rgba(15, 23, 42, 0.85)",
        height=450,
        margin=dict(l=45, r=35, t=50, b=45)
    )

    return fig


# =============================================================================
# 4. GAMBAR PENAMPANG 2D POTONGAN TEKNIS LENGKAP (CROSS SECTION)
# =============================================================================

def plot_foundation_cross_section(B, L, Df, dw, P_kN, soil_name="Tanah Lempung", c=35.0, phi=12.0, gamma=17.5, hf=0.40, shape="Bujur Sangkar"):
    """
    Gambar penampang 2D potongan melintang fondasi dan lapisan tanah dalam Dark Slate CAD Blueprint.
    Bentuk disesuaikan (Lingkaran, Persegi, Jalur Bata).
    """
    fig = go.Figure()

    x_half = max(2.6, B * 1.6)
    y_bottom = max(Df + B * 1.3, Df + 2.2)

    # 1. Lapisan Tanah Bawah
    fig.add_shape(
        type="rect",
        x0=-x_half, x1=x_half, y0=0, y1=-y_bottom,
        fillcolor="#0F172A",
        line=dict(color="#1E293B", width=1),
        layer="below"
    )

    # 2. Garis Muka Air Tanah
    fig.add_shape(
        type="line",
        x0=-x_half, x1=x_half, y0=-dw, y1=-dw,
        line=dict(color="#00E5FF", width=2.5, dash="dash")
    )
    fig.add_annotation(
        x=x_half * 0.68, y=-dw,
        text=f"<b>▼ Muka Air Tanah (dw = {dw:.2f} m)</b>",
        showarrow=False, yshift=12,
        font=dict(color="#00E5FF", size=11, family="Plus Jakarta Sans"),
        bgcolor="rgba(15, 23, 42, 0.9)", bordercolor="#00E5FF", borderwidth=1
    )

    # 3. Blok Fondasi
    footing_x0 = -B / 2.0
    footing_x1 = B / 2.0
    footing_y0 = -Df
    footing_y1 = -Df + hf
    
    fill_f = "rgba(56, 189, 248, 0.35)" if "Lingkaran" not in shape else "rgba(6, 182, 212, 0.4)"
    border_f = "#38BDF8" if "Lingkaran" not in shape else "#00E5FF"

    fig.add_shape(
        type="rect",
        x0=footing_x0, x1=footing_x1, y0=footing_y0, y1=footing_y1,
        fillcolor=fill_f, line=dict(color=border_f, width=2.5),
        layer="above"
    )

    # Jika Fondasi Lingkaran, beri tanda tepi busur melengkung
    if "Lingkaran" in shape:
        fig.add_annotation(
            x=0, y=(footing_y0 + footing_y1) / 2.0,
            text=f"<b>Penampang Melintang Fondasi Lingkaran (Ø = {B:.2f} m)</b>",
            showarrow=False,
            font=dict(color="#00E5FF", size=11, family="Plus Jakarta Sans")
        )

    # 4. Kolom Struktur di atas fondasi
    col_width = min(0.40, B * 0.28)
    col_top = 0.55
    fig.add_shape(
        type="rect",
        x0=-col_width / 2.0, x1=col_width / 2.0, y0=footing_y1, y1=col_top,
        fillcolor="#1E293B", line=dict(color="#38BDF8", width=2),
        layer="above"
    )

    # Jika Fondasi Jalur, gambarkan dinding bata merah
    if "Menerus" in shape or "Jalur" in shape:
        fig.add_shape(
            type="rect",
            x0=-0.125, x1=0.125, y0=footing_y1, y1=col_top,
            fillcolor="rgba(239, 68, 68, 0.4)", line=dict(color="#EF4444", width=2),
            layer="above"
        )
        fig.add_annotation(
            x=0.55, y=0.1,
            text="<b>Pasangan Dinding Bata</b>",
            showarrow=False,
            font=dict(color="#F87171", size=10, family="Plus Jakarta Sans")
        )

    # 5. Garis Muka Tanah Alami (± 0.00)
    fig.add_shape(
        type="line",
        x0=-x_half, x1=x_half, y0=0, y1=0,
        line=dict(color="#10B981", width=3)
    )
    fig.add_annotation(
        x=-x_half * 0.68, y=0,
        text="<b>± 0.00 Muka Tanah Alami</b>",
        showarrow=False, yshift=12,
        font=dict(color="#34D399", size=11, family="Plus Jakarta Sans")
    )

    # 6. Panah Beban Aksial P
    fig.add_annotation(
        x=0, y=col_top, ax=0, ay=-55,
        xref="x", yref="y", axref="pixel", ayref="pixel",
        showarrow=True, arrowhead=3, arrowsize=1.5, arrowwidth=3.5,
        arrowcolor="#F59E0B"
    )
    fig.add_annotation(
        x=0, y=col_top + 0.62,
        text=f"<b>P = {P_kN:.1f} kN</b> (~{P_kN/9.81:.1f} Ton)",
        showarrow=False,
        font=dict(color="#FBBF24", size=12, family="Plus Jakarta Sans"),
        bgcolor="rgba(15, 23, 42, 0.9)", bordercolor="#F59E0B", borderwidth=1.5, borderpad=4
    )

    # 7. Dimensi Fondasi
    if "Lingkaran" in shape:
        dim_str = f"<b>Diameter D = {B:.2f} m</b> (Tebal h = {hf:.2f} m, Df = {Df:.2f} m)"
    elif "Menerus" in shape or "Jalur" in shape:
        dim_str = f"<b>Lebar Jalur B = {B:.2f} m</b> (Pondasi Menerus / Jalur Df = {Df:.2f} m)"
    else:
        dim_str = f"<b>B = {B:.2f} m &times; L = {L:.2f} m</b> (Tebal h = {hf:.2f} m, Df = {Df:.2f} m)"

    fig.add_annotation(
        x=0, y=-Df - 0.28,
        text=dim_str,
        showarrow=False,
        font=dict(color="#F8FAFC", size=11, family="Plus Jakarta Sans"),
        bgcolor="rgba(15, 23, 42, 0.9)", bordercolor="#38BDF8", borderwidth=1, borderpad=4
    )

    # Layout Dark Mode
    fig.update_layout(
        title=dict(
            text=f"<b>📐 Potongan Melintang Geoteknik 2D: {shape.split('(')[0]}</b>",
            font=dict(size=14, color="#F8FAFC", family="Plus Jakarta Sans")
        ),
        xaxis=dict(title="Posisi Horizontal (m)", range=[-x_half, x_half], gridcolor="#1E293B", color="#94A3B8"),
        yaxis=dict(title="Kedalaman Tanah (m)", range=[-y_bottom, 1.2], gridcolor="#1E293B", color="#94A3B8"),
        plot_bgcolor="#081122",
        paper_bgcolor="rgba(15, 23, 42, 0.85)",
        height=460,
        margin=dict(l=45, r=35, t=55, b=45)
    )

    return fig


# =============================================================================
# 5. SPEEDOMETER GAUGE FAKTOR KEAMANAN (SF)
# =============================================================================

def plot_safety_gauge(sf_value, target_sf=3.0):
    """
    Indikator Speedometer Faktor Keamanan (SF) bernuansa Dark Slate Geoteknik.
    """
    gauge_max = max(6.0, round(sf_value + 1.5))
    
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=round(sf_value, 2),
        domain={'x': [0, 1], 'y': [0, 1]},
        delta={'reference': target_sf, 'increasing': {'color': "#10B981"}, 'decreasing': {'color': "#EF4444"}},
        title={'text': "<b>Faktor Keamanan Aktual (SF)</b><br><span style='font-size:0.8em;color:#94A3B8;'>Target Desain = " + str(target_sf) + "</span>", 'font': {'size': 13, 'family': 'Plus Jakarta Sans', 'color': '#F8FAFC'}},
        gauge={
            'axis': {'range': [0, gauge_max], 'tickwidth': 1.5, 'tickcolor': "#64748B"},
            'bar': {'color': "#00E5FF", 'thickness': 0.3},
            'bgcolor': "rgba(15, 23, 42, 0.7)",
            'borderwidth': 1.5,
            'bordercolor': "#334155",
            'steps': [
                {'range': [0, 2.0], 'color': 'rgba(239, 68, 68, 0.25)'},
                {'range': [2.0, target_sf], 'color': 'rgba(245, 158, 11, 0.25)'},
                {'range': [target_sf, gauge_max], 'color': 'rgba(16, 185, 129, 0.25)'}
            ],
            'threshold': {
                'line': {'color': "#EF4444", 'width': 3.5},
                'thickness': 0.75,
                'value': target_sf
            }
        }
    ))
    
    fig.update_layout(
        height=260,
        margin=dict(l=25, r=25, t=35, b=20),
        paper_bgcolor="rgba(15, 23, 42, 0.85)",
        font={'family': "Plus Jakarta Sans", 'color': "#F8FAFC"}
    )
    
    return fig


# =============================================================================
# 6. PROFIL STRATIGRAFI LAPISAN TANAH INTERAKTIF (UNTUK ANALISIS TANAH)
# =============================================================================

def plot_soil_stratigraphy(layers, water_table=1.5):
    """
    Membuat grafik kolom lapisan tanah geoteknik interaktif untuk Bore Log SPT:
    Warna bergradasi sesuai jenis tanah (lempung cokelat/abu, pasir keemasan, dll).
    """
    fig = go.Figure()

    if not layers:
        return fig

    color_map = {
        "Lempung": "#854D0E",
        "Lanau": "#A16207",
        "Pasir": "#D97706",
        "Kerikil": "#475569",
        "Batuan": "#334155"
    }

    for idx, lyr in enumerate(layers):
        z_top = lyr.get("depth_top", 0.0)
        z_bot = lyr.get("depth_bot", z_top + 1.5)
        stype = lyr.get("soil_type", "Lempung")
        n_val = lyr.get("n_spt", 0)
        c_val = lyr.get("c", 0.0)
        phi_val = lyr.get("phi", 0.0)
        kons = lyr.get("konsistensi", "-")
        
        # Tentukan warna
        c_fill = "#A16207"
        for k, v in color_map.items():
            if k.lower() in stype.lower():
                c_fill = v
                break
                
        # Blok Lapisan
        fig.add_trace(go.Bar(
            x=[1],
            y=[z_bot - z_top],
            base=[-z_bot],
            orientation="v",
            marker=dict(color=c_fill, opacity=0.85, line=dict(color="#F8FAFC", width=1.5)),
            name=f"{lyr.get('interval_str', '')}: {stype}",
            hovertemplate=(
                f"<b>{stype}</b><br>"
                f"Kedalaman: {z_top:.2f} - {z_bot:.2f} m<br>"
                f"N-SPT: {n_val} pukulan ({kons})<br>"
                f"Kohesi c: {c_val} kPa | Sudut Geser φ: {phi_val}°<extra></extra>"
            )
        ))

    # Garis Muka Air Tanah
    fig.add_shape(
        type="line",
        x0=0.5, x1=1.5, y0=-water_table, y1=-water_table,
        line=dict(color="#00E5FF", width=3, dash="dash")
    )
    fig.add_annotation(
        x=1.35, y=-water_table,
        text=f"<b>▼ MAT ({water_table:.2f}m)</b>",
        showarrow=False, yshift=12,
        font=dict(color="#00E5FF", size=11, family="Plus Jakarta Sans")
    )

    max_depth = max([l.get("depth_bot", 6.0) for l in layers])
    fig.update_layout(
        title=dict(
            text="<b>📊 Kolom Stratigrafi Lapisan Tanah (Bore Log Interaktif)</b>",
            font=dict(size=14, color="#F8FAFC", family="Plus Jakarta Sans")
        ),
        yaxis=dict(title="Elevasi / Kedalaman (m)", range=[-max_depth - 1.0, 0.5], gridcolor="#1E293B", color="#94A3B8"),
        xaxis=dict(showticklabels=False, range=[0.4, 1.6], showgrid=False),
        plot_bgcolor="#081122",
        paper_bgcolor="rgba(15, 23, 42, 0.85)",
        height=500,
        showlegend=True,
        legend=dict(font=dict(color="#CBD5E1", size=10), bgcolor="rgba(15, 23, 42, 0.7)")
    )

    return fig
