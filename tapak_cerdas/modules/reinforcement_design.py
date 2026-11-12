"""
=============================================================================
TAPAK CERDAS - ENGINE DESAIN PENULANGAN PONDASI DANGKAL (SNI 2847:2019)
=============================================================================
File: modules/reinforcement_design.py
Deskripsi: Perhitungan desain tulangan lentur, kontrol geser satu arah (beam shear),
           kontrol geser dua arah (punching shear), panjang penyaluran (development length),
           dan estimasi volume beton serta berat besi tulangan sesuai SNI 2847:2019
           (Persyaratan Beton Struktural untuk Bangunan Gedung).
=============================================================================
"""

import math

def design_footing_reinforcement(
    B_m,
    L_m,
    hf_m,
    col_b_m,
    col_h_m,
    Pu_kN,
    Mux_kNm=0.0,
    Muy_kNm=0.0,
    fc_MPa=25.0,
    fy_MPa=420.0,
    cover_mm=75.0,
    bar_dia_mm=16.0,
    target_spacing_mm=150.0,
    standard="SNI 2847:2019"
):
    """
    Menghitung penulangan pondasi telapak secara komprehensif berdasarkan SNI 2847:2019 / ACI 318M.

    Parameter Input:
    - B_m, L_m        : Lebar dan panjang fondasi (meter)
    - hf_m            : Tebal pelat fondasi (meter)
    - col_b_m, col_h_m: Dimensi kolom pedestal arah X dan Y (meter)
    - Pu_kN           : Beban aksial terfaktor (kN)
    - Mux_kNm, Muy_kNm: Momen terfaktor arah X dan Y (kNm)
    - fc_MPa          : Kuat tekan beton f'c (MPa)
    - fy_MPa          : Kuat leleh baja tulangan fy (MPa)
    - cover_mm        : Selimut beton bersih (mm), SNI menetapkan min 75 mm untuk kontak tanah
    - bar_dia_mm      : Diameter tulangan utama yang dipilih (mm), misal 13, 16, 19
    - target_spacing_mm: Target jarak tulangan awal (mm)
    - standard        : Standar acuan perencanaan

    Mengembalikan dictionary hasil perhitungan terstruktur dan status verifikasi keamanan.
    """
    # Konversi satuan dasar ke mm dan N
    B = B_m * 1000.0
    L = L_m * 1000.0
    hf = hf_m * 1000.0
    col_b = col_b_m * 1000.0
    col_h = col_h_m * 1000.0
    Pu = Pu_kN * 1000.0
    Mux = Mux_kNm * 1e6
    Muy = Muy_kNm * 1e6
    cc = cover_mm
    db = bar_dia_mm

    # 1. TINGGI EFEKTIF (d)
    # Tulangan bawah lapis 1 (arah X):
    dx = hf - cc - db / 2.0
    # Tulangan bawah lapis 2 (arah Y):
    dy = hf - cc - db - db / 2.0
    d_avg = (dx + dy) / 2.0

    # 2. TEGANGAN KONTAK TANAH TERFAKTOR NETTO (qu_net)
    area_f = B * L
    qu_uniform = Pu / area_f  # N/mm2 = MPa

    # Eksentrisitas pembebanan
    ex = abs(Mux / Pu) if Pu > 0 else 0.0  # mm
    ey = abs(Muy / Pu) if Pu > 0 else 0.0  # mm

    # Tahanan modulus penampang dasar tapak
    Wx = (B * (L**2)) / 6.0
    Wy = (L * (B**2)) / 6.0

    qu_max = qu_uniform + (abs(Mux) / Wx if Wx > 0 else 0.0) + (abs(Muy) / Wy if Wy > 0 else 0.0)
    qu_min = qu_uniform - (abs(Mux) / Wx if Wx > 0 else 0.0) - (abs(Muy) / Wy if Wy > 0 else 0.0)

    # Pemeriksaan tegangan tarik tanah (kern limit)
    is_uplift = (qu_min < 0.0)
    kern_limit_L = L / 6.0
    kern_limit_B = B / 6.0
    eccentricity_ok = (ex <= kern_limit_L) and (ey <= kern_limit_B)

    # Nilai tegangan acuan untuk desain lentur dan geser (gunakan qu_max untuk keamanan desain)
    qu_design = max(qu_uniform, qu_max)  # MPa (N/mm2)

    # 3. KONTROL GESER DUA ARAH (PUNCHING SHEAR / GESER PONS) - SNI 2847:2019 Pasal 22.6
    # Penampang kritis pons berjarak d_avg/2 dari sisi kolom
    b1_crit = col_b + d_avg  # mm
    b2_crit = col_h + d_avg  # mm
    bo = 2.0 * (b1_crit + b2_crit)  # Perimeter geser pons (mm)
    area_punch = b1_crit * b2_crit  # Luas area dalam perimeter pons (mm2)

    # Gaya geser pons terfaktor Vu2
    Vu2 = max(0.0, Pu - (qu_design * area_punch))  # N

    # Rasio sisi panjang terhadap sisi pendek kolom (beta)
    beta_col = max(col_b, col_h) / min(col_b, col_h) if min(col_b, col_h) > 0 else 1.0

    # Koefisien posisi kolom alpha_s (40 untuk kolom dalam/interior, 30 untuk tepi, 20 untuk sudut)
    alpha_s = 40.0

    lambda_c = 1.0  # Beton berat normal
    sqrt_fc = math.sqrt(fc_MPa)

    # Tiga persamaan kapasitas geser pons nominal Vc2 sesuai SNI 2847:2019 Tabel 22.6.5.2
    Vc2_a = 0.17 * (1.0 + 2.0 / beta_col) * lambda_c * sqrt_fc * bo * d_avg
    Vc2_b = 0.083 * (2.0 + (alpha_s * d_avg) / bo) * lambda_c * sqrt_fc * bo * d_avg
    Vc2_c = 0.33 * lambda_c * sqrt_fc * bo * d_avg

    Vc2 = min(Vc2_a, Vc2_b, Vc2_c)  # N
    phi_v = 0.75  # Faktor reduksi kekuatan geser SNI 2847:2019
    phi_Vc2 = phi_v * Vc2  # N

    ratio_punch = Vu2 / phi_Vc2 if phi_Vc2 > 0 else 999.0
    punch_ok = (Vu2 <= phi_Vc2)

    # 4. KONTROL GESER SATU ARAH (BEAM SHEAR) - SNI 2847:2019 Pasal 22.5
    # Penampang kritis berjarak d dari muka kolom
    # Arah X (kantilever arah B):
    cant_x = (B - col_b) / 2.0  # mm
    crit_x_dist = cant_x - dx   # mm
    if crit_x_dist > 0:
        Vu1_x = qu_design * L * crit_x_dist  # N
    else:
        Vu1_x = 0.0

    Vc1_x = 0.17 * lambda_c * sqrt_fc * L * dx  # N
    phi_Vc1_x = phi_v * Vc1_x
    ratio_shear_x = Vu1_x / phi_Vc1_x if phi_Vc1_x > 0 else 0.0
    shear_x_ok = (Vu1_x <= phi_Vc1_x)

    # Arah Y (kantilever arah L):
    cant_y = (L - col_h) / 2.0  # mm
    crit_y_dist = cant_y - dy   # mm
    if crit_y_dist > 0:
        Vu1_y = qu_design * B * crit_y_dist  # N
    else:
        Vu1_y = 0.0

    Vc1_y = 0.17 * lambda_c * sqrt_fc * B * dy  # N
    phi_Vc1_y = phi_v * Vc1_y
    ratio_shear_y = Vu1_y / phi_Vc1_y if phi_Vc1_y > 0 else 0.0
    shear_y_ok = (Vu1_y <= phi_Vc1_y)

    shear_one_way_ok = shear_x_ok and shear_y_ok

    # 5. DESAIN PENULANGAN LENTUR (FLEXURAL DESIGN) - SNI 2847:2019 Pasal 13.2.7 & 22.2
    # Momen pada muka kolom:
    # Arah X (momen di muka kolom arah kantilever B):
    Mux_face = (qu_design * L * (cant_x**2)) / 2.0  # N.mm
    # Arah Y (momen di muka kolom arah kantilever L):
    Muy_face = (qu_design * B * (cant_y**2)) / 2.0  # N.mm

    phi_f = 0.90  # Faktor reduksi lentur SNI 2847:2019

    # Luas 1 batang tulangan
    area_1bar = (math.pi / 4.0) * (db**2)

    # Batas rasio tulangan minimum (SNI 2847:2019 Pasal 13.3.3.1 untuk pelat fondasi)
    # Digunakan rasio tulangan susut dan suhu: 0.0018 untuk fy = 420 MPa
    rho_min = 0.0018 * (420.0 / fy_MPa) if fy_MPa > 0 else 0.0018
    # Batas rasio tulangan balok lentur jika ditinjau sebagai balok:
    rho_min_beam = max(0.25 * sqrt_fc / fy_MPa, 1.4 / fy_MPa)

    # Fungsi pembantu hitung tulangan lentur
    def _calc_flexure(Mu_val, b_dim, d_val):
        Rn = Mu_val / (phi_f * b_dim * (d_val**2)) if (b_dim * (d_val**2)) > 0 else 0.0
        term = 1.0 - (2.0 * Rn) / (0.85 * fc_MPa)
        if term < 0:
            # Over-reinforced / perlu tebal diperbesar
            rho_calc = 0.025
        else:
            rho_calc = (0.85 * fc_MPa / fy_MPa) * (1.0 - math.sqrt(max(0.0, term)))

        # Luas tulangan susut suhu minimum per lebar penampang
        As_min_shrinkage = rho_min * b_dim * hf
        As_min_flexure = rho_min_beam * b_dim * d_val
        As_min_governing = max(As_min_shrinkage, As_min_flexure)

        As_req = max(rho_calc * b_dim * d_val, As_min_governing)

        # Jumlah batang tulangan
        n_bars = max(3, math.ceil(As_req / area_1bar))

        # Jarak tulangan aktual
        actual_width = b_dim - 2.0 * cc - db
        spacing = actual_width / (n_bars - 1) if n_bars > 1 else actual_width

        # Kontrol spasi maksimum SNI: min(3*hf, 450 mm)
        s_max = min(3.0 * hf, 450.0)
        if spacing > s_max:
            spacing = s_max
            n_bars = math.ceil(actual_width / spacing) + 1

        As_provided = n_bars * area_1bar

        # Cek kapasitas momen desain phi_Mn
        a = (As_provided * fy_MPa) / (0.85 * fc_MPa * b_dim)
        Mn = As_provided * fy_MPa * (d_val - a / 2.0)
        phi_Mn = phi_f * Mn
        moment_ok = (phi_Mn >= Mu_val)

        return {
            "Mu": Mu_val,
            "Rn": Rn,
            "rho_calc": rho_calc,
            "rho_min": rho_min,
            "As_min": As_min_governing,
            "As_req": As_req,
            "As_provided": As_provided,
            "n_bars": n_bars,
            "spacing_mm": round(spacing, 1),
            "s_max": s_max,
            "phi_Mn": phi_Mn,
            "ratio_Mu": Mu_val / phi_Mn if phi_Mn > 0 else 0.0,
            "moment_ok": moment_ok
        }

    reinf_x = _calc_flexure(Mux_face, L, dx)
    reinf_y = _calc_flexure(Muy_face, B, dy)

    # 6. DISTRIBUSI TULANGAN ARAH PENDEK UNTUK PONDASI PERSEGI PANJANG (SNI 2847:2019 Pasal 13.3.3.3)
    # Jika L != B, sebagian tulangan arah pendek harus terkonsentrasi di jalur pusat selebar B
    beta_footing = max(L, B) / min(L, B)
    gamma_s = 2.0 / (beta_footing + 1.0) if beta_footing > 1.0 else 1.0

    # 7. PANJANG PENYALURAN TULANGAN (DEVELOPMENT LENGTH) - SNI 2847:2019 Pasal 25.4
    # Formulasi standar SNI untuk tulangan tarik berkait atau lurus:
    psi_t = 1.0  # Posisi tulangan bawah
    psi_e = 1.0  # Tulangan tanpa pelapis epoksi
    psi_s = 0.8 if db <= 19.0 else 1.0  # Faktor ukuran tulangan
    lambda_val = 1.0

    # Panjang penyaluran lurus ld (mm)
    ld = ((fy_MPa * psi_t * psi_e * psi_s) / (1.1 * lambda_val * sqrt_fc)) * db
    ld = max(300.0, ld)

    # Panjang penyaluran dengan kait standar 90 derajat (ldh)
    ldh = (0.24 * fy_MPa * psi_e / (lambda_val * sqrt_fc)) * db
    ldh = max(150.0, max(8.0 * db, ldh))

    # Panjang tersedia pada kantilever fondasi
    L_avail_x = cant_x - cc
    L_avail_y = cant_y - cc
    min_L_avail = min(L_avail_x, L_avail_y)

    dev_length_straight_ok = (min_L_avail >= ld)
    hook_needed = not dev_length_straight_ok

    # 8. ESTIMASI VOLUME BETON & BERAT BAJA TULANGAN (BILL OF QUANTITIES RINGKAS)
    vol_concrete_m3 = (B_m * L_m * hf_m)  # m3

    # Panjang tulangan per batang (dengan tambahan kait 90 derajat jika diperlukan atau standar)
    hook_len_mm = 12.0 * db if hook_needed else 0.0
    len_bar_x_m = ((B - 2.0 * cc + 2.0 * hook_len_mm) / 1000.0)
    len_bar_y_m = ((L - 2.0 * cc + 2.0 * hook_len_mm) / 1000.0)

    total_len_x_m = reinf_x["n_bars"] * len_bar_x_m
    total_len_y_m = reinf_y["n_bars"] * len_bar_y_m
    total_rebar_len_m = total_len_x_m + total_len_y_m

    # Berat jenis baja tulangan (SNI / nominal): w = 0.006165 * db^2 (kg/m)
    unit_weight_rebar = 0.006165 * (db**2)  # kg/m
    total_rebar_weight_kg = total_rebar_len_m * unit_weight_rebar

    # Rasio penulangan per volume beton (kg besi / m3 beton)
    steel_ratio_kg_m3 = total_rebar_weight_kg / vol_concrete_m3 if vol_concrete_m3 > 0 else 0.0

    # 9. EVALUASI KESELURUHAN STATUS DESAIN STRUKTUR
    all_structural_safe = (
        punch_ok and
        shear_one_way_ok and
        reinf_x["moment_ok"] and
        reinf_y["moment_ok"] and
        eccentricity_ok
    )

    # Ringkasan Rekomendasi Notasi Desain
    callout_x = f"D{int(db)}-{int(reinf_x['spacing_mm'])} mm ({reinf_x['n_bars']} batang)"
    callout_y = f"D{int(db)}-{int(reinf_y['spacing_mm'])} mm ({reinf_y['n_bars']} batang)"

    return {
        "standard": standard,
        "parameters": {
            "B_m": B_m, "L_m": L_m, "hf_m": hf_m,
            "col_b_m": col_b_m, "col_h_m": col_h_m,
            "Pu_kN": Pu_kN, "Mux_kNm": Mux_kNm, "Muy_kNm": Muy_kNm,
            "fc_MPa": fc_MPa, "fy_MPa": fy_MPa,
            "cover_mm": cover_mm, "bar_dia_mm": bar_dia_mm,
            "dx_mm": dx, "dy_mm": dy, "d_avg_mm": d_avg
        },
        "soil_pressures": {
            "qu_uniform_kPa": qu_uniform * 1000.0,
            "qu_max_kPa": qu_max * 1000.0,
            "qu_min_kPa": qu_min * 1000.0,
            "ex_mm": ex, "ey_mm": ey,
            "is_uplift": is_uplift,
            "eccentricity_ok": eccentricity_ok
        },
        "punching_shear": {
            "bo_mm": bo,
            "area_punch_m2": area_punch / 1e6,
            "Vu2_kN": Vu2 / 1000.0,
            "Vc2_nominal_kN": Vc2 / 1000.0,
            "phi_Vc2_kN": phi_Vc2 / 1000.0,
            "ratio": ratio_punch,
            "is_safe": punch_ok,
            "status": "AMAN (OK)" if punch_ok else "TIDAK AMAN (Perlu Pertebal hf)"
        },
        "one_way_shear": {
            "shear_x": {
                "Vu1_kN": Vu1_x / 1000.0,
                "phi_Vc1_kN": phi_Vc1_x / 1000.0,
                "ratio": ratio_shear_x,
                "is_safe": shear_x_ok
            },
            "shear_y": {
                "Vu1_kN": Vu1_y / 1000.0,
                "phi_Vc1_kN": phi_Vc1_y / 1000.0,
                "ratio": ratio_shear_y,
                "is_safe": shear_y_ok
            },
            "is_safe": shear_one_way_ok,
            "status": "AMAN (OK)" if shear_one_way_ok else "TIDAK AMAN (Perlu Pertebal hf)"
        },
        "flexure_rebar": {
            "dir_x": {
                "Mux_kNm": Mux_face / 1e6,
                "As_req_mm2": reinf_x["As_req"],
                "As_provided_mm2": reinf_x["As_provided"],
                "n_bars": reinf_x["n_bars"],
                "spacing_mm": reinf_x["spacing_mm"],
                "callout": callout_x,
                "phi_Mn_kNm": reinf_x["phi_Mn"] / 1e6,
                "ratio": reinf_x["ratio_Mu"],
                "is_safe": reinf_x["moment_ok"]
            },
            "dir_y": {
                "Muy_kNm": Muy_face / 1e6,
                "As_req_mm2": reinf_y["As_req"],
                "As_provided_mm2": reinf_y["As_provided"],
                "n_bars": reinf_y["n_bars"],
                "spacing_mm": reinf_y["spacing_mm"],
                "callout": callout_y,
                "phi_Mn_kNm": reinf_y["phi_Mn"] / 1e6,
                "ratio": reinf_y["ratio_Mu"],
                "is_safe": reinf_y["moment_ok"]
            },
            "gamma_s_center_band": gamma_s
        },
        "development_length": {
            "ld_mm": ld,
            "ldh_hook_mm": ldh,
            "L_avail_min_mm": min_L_avail,
            "is_straight_ok": dev_length_straight_ok,
            "hook_needed": hook_needed,
            "recommendation": "Gunakan tulangan lurus tanpa kait" if dev_length_straight_ok else "Wajib gunakan kait standar 90° (kait 150-200 mm)"
        },
        "quantities": {
            "vol_concrete_m3": round(vol_concrete_m3, 3),
            "total_rebar_len_m": round(total_rebar_len_m, 2),
            "unit_weight_kg_m": round(unit_weight_rebar, 3),
            "total_rebar_weight_kg": round(total_rebar_weight_kg, 1),
            "steel_ratio_kg_m3": round(steel_ratio_kg_m3, 1)
        },
        "summary": {
            "rebar_x": callout_x,
            "rebar_y": callout_y,
            "concrete_cover": f"{int(cover_mm)} mm",
            "footing_thickness": f"{hf_m:.2f} m ({int(hf)} mm)",
            "is_all_safe": all_structural_safe,
            "status": "DESAIN STRUKTURAL AMAN (OK)" if all_structural_safe else "PERLU PENYESUAIAN DESAIN (TIDAK MEMENUHI)",
            "action_needed": "Desain memenuhi seluruh persyaratan SNI 2847:2019" if all_structural_safe else "Pertebal fondasi (hf) atau perbesar mutu beton / dimensi tapak!"
        }
    }
