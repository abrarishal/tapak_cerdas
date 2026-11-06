"""
=============================================================================
TAPAK CERDAS - SISTEM EVALUASI CERDAS BENTUK & KELAYAKAN FONDASI DALAM
=============================================================================
File: modules/deep_foundation.py
Deskripsi: 
1. Evaluasi Kelayakan Geoteknik: Fondasi Dangkal vs. Fondasi Dalam (Deep Foundation)
   berdasarkan konsistensi tanah SPT (N-SPT), CPT (qc), dan beban aksial gedung P.
2. Perhitungan Kapasitas Dukung Tiang Fondasi Dalam:
   - Strauss Pile (Bor Manual) Diameter 30-40 cm
   - Mini Pile (Tiang Pancang Persegi Precast) 20x20 cm / 25x25 cm
   - Bored Pile Mesin Diameter 50-80 cm
3. Sistem Penilai Komparasi Bentuk Fondasi Dangkal:
   - Bujur Sangkar (Square)
   - Persegi Panjang (Rectangular)
   - Lingkaran (Circular)
   - Jalur / Menerus (Strip Footing)
=============================================================================
"""

import math

def evaluate_foundation_feasibility(avg_n_spt=None, avg_qc=None, p_axial_kN=350.0, c_kpa=25.0, phi_deg=10.0, df_m=1.5):
    """
    Mengevaluasi apakah tanah dasar layak menggunakan Fondasi Dangkal (Pad Footing)
    atau WAJIB / DIREKOMENDASIKAN menggunakan Fondasi Dalam (Deep Foundation).
    Acuan: SNI 8460:2017 & Buku Hardiyatmo.
    """
    # Tentukan indikator kekuatan lapisan tanah permukaan (0 - 3m)
    stiffness_score = 0  # 0: Sangat Lunak, 1: Lunak, 2: Sedang, 3: Kaku/Padat
    soil_desc = "Sedang"
    
    if avg_n_spt is not None:
        if avg_n_spt < 4:
            stiffness_score = 0
            soil_desc = f"Lempung Sangat Lunak / Lunak (N-SPT = {avg_n_spt:.1f})"
        elif avg_n_spt < 8:
            stiffness_score = 1
            soil_desc = f"Lempung Sedang / Lanau (N-SPT = {avg_n_spt:.1f})"
        elif avg_n_spt < 15:
            stiffness_score = 2
            soil_desc = f"Tanah Teguh / Pasir Sedang (N-SPT = {avg_n_spt:.1f})"
        else:
            stiffness_score = 3
            soil_desc = f"Tanah Kaku / Pasir Padat (N-SPT = {avg_n_spt:.1f})"
    elif avg_qc is not None:
        if avg_qc < 20:
            stiffness_score = 0
            soil_desc = f"Tanah Sangat Lunak (qc = {avg_qc:.1f} kg/cm²)"
        elif avg_qc < 40:
            stiffness_score = 1
            soil_desc = f"Tanah Lunak s/d Sedang (qc = {avg_qc:.1f} kg/cm²)"
        elif avg_qc < 100:
            stiffness_score = 2
            soil_desc = f"Tanah Sedang s/d Kaku (qc = {avg_qc:.1f} kg/cm²)"
        else:
            stiffness_score = 3
            soil_desc = f"Tanah Padat / Keras (qc = {avg_qc:.1f} kg/cm²)"
    else:
        # Dari parameter c & phi
        if c_kpa < 20 and phi_deg < 15:
            stiffness_score = 0
            soil_desc = f"Tanah Kohesif Sangat Lemah (c={c_kpa} kPa, φ={phi_deg}°)"
        elif c_kpa < 40 and phi_deg < 25:
            stiffness_score = 1
            soil_desc = f"Tanah Kohesif Sedang (c={c_kpa} kPa, φ={phi_deg}°)"
        else:
            stiffness_score = 2
            soil_desc = f"Tanah Cukup Kuat (c={c_kpa} kPa, φ={phi_deg}°)"

    # Evaluasi Tingkat Beban Bangunan
    # P < 250 kN: Ringan (1 lantai)
    # 250 <= P < 600 kN: Sedang (2-3 lantai)
    # P >= 600 kN: Berat (>= 3-4 lantai)
    if p_axial_kN < 250:
        load_level = "Ringan (1 Lantai)"
    elif p_axial_kN < 600:
        load_level = "Sedang (2 - 3 Lantai)"
    else:
        load_level = "Tinggi / Berat (≥ 3 - 4 Lantai)"

    # Keputusan Geoteknik
    if stiffness_score == 0:
        recommendation = "WAJIB FONDASI DALAM"
        status_color = "danger"
        reason = (
            f"Lapisan tanah atas pada kedalaman rencana sangat lunak ({soil_desc}). "
            f"Jika dipaksakan menggunakan fondasi telapak dangkal, dimensi tapak akan sangat besar (B > 2.8 m) "
            f"dan memiliki risiko tinggi terjadi penurunan berlebih (excessive settlement) atau keruntuhan geser umum. "
            f"Sistem sangat merekomendasikan penerusan beban ke lapisan tanah keras melalui FONDASI DALAM."
        )
        is_deep_needed = True
    elif stiffness_score == 1 and p_axial_kN >= 350:
        recommendation = "DIREKOMENDASIKAN FONDASI DALAM"
        status_color = "warning"
        reason = (
            f"Tanah tergolong lunak s/d sedang ({soil_desc}) sementara beban kolom tergolong {load_level}. "
            f"Fondasi dangkal membutuhkan dimensi cukup besar dan berisiko mengalami diferensial penurunan. "
            f"Penggunaan Fondasi Dalam (seperti Strauss Pile atau Mini Pile) jauh lebih aman, stabil, dan bebas risiko retak struktur."
        )
        is_deep_needed = True
    elif stiffness_score >= 2:
        recommendation = "FONDASI DANGKAL AMAN & EKONOMIS"
        status_color = "safe"
        reason = (
            f"Lapisan tanah atas memiliki daya dukung yang memadai ({soil_desc}) untuk memikul beban kolom {load_level}. "
            f"Fondasi Dangkal (Pondasi Telapak / Pad Footing) adalah pilihan PALING EFISIEN & HEMAT BIAYA. "
            f"Tidak diperlukan fondasi dalam untuk kondisi ini."
        )
        is_deep_needed = False
    else:
        recommendation = "FONDASI DANGKAL DENGAN PERKUATAN"
        status_color = "warning"
        reason = (
            f"Beban relatif ringan ({load_level}) pada tanah {soil_desc}. Fondasi telapak masih memungkinkan "
            f"dengan memperlebar tapak atau memberi perbaikan tanah dasar (urugan sirtu / cerucuk matras bambu)."
        )
        is_deep_needed = False

    return {
        "recommendation": recommendation,
        "status_color": status_color,
        "is_deep_needed": is_deep_needed,
        "soil_desc": soil_desc,
        "load_level": load_level,
        "reason": reason
    }


def find_hard_soil_depth(spt_layers=None, cpt_points=None):
    """
    Mencari kedalaman tanah keras (bearing layer) dari data SPT atau CPT.
    Kriteria:
    - SPT: N >= 25 (tanah padat / lempung keras)
    - CPT: qc >= 150 kg/cm² (tanah keras / batuan lunak)
    """
    hard_depth = None
    hard_n = None
    hard_qc = None

    if spt_layers and len(spt_layers) > 0:
        for lyr in spt_layers:
            n_v = lyr.get("n_spt", 0)
            if n_v >= 20:
                hard_depth = lyr.get("depth_top", 6.0)
                hard_n = n_v
                break
        if hard_depth is None and spt_layers:
            # Gunakan kedalaman lapisan terdalam
            last_lyr = spt_layers[-1]
            hard_depth = last_lyr.get("depth_bot", 6.0)
            hard_n = last_lyr.get("n_spt", 15)

    elif cpt_points and len(cpt_points) > 0:
        for pt in cpt_points:
            qc = pt.get("qc", 0)
            if qc >= 120:
                hard_depth = pt.get("depth", 6.0)
                hard_qc = qc
                break
        if hard_depth is None and cpt_points:
            last_pt = cpt_points[-1]
            hard_depth = last_pt.get("depth", 6.0)
            hard_qc = last_pt.get("qc", 50)

    # Fallback realistis bila data bor belum mencapai tanah keras
    if hard_depth is None or hard_depth <= 1.5:
        hard_depth = 6.0

    return {
        "hard_depth": round(hard_depth, 2),
        "hard_n": hard_n,
        "hard_qc": hard_qc
    }


def calculate_deep_foundation_options(p_axial_kN, hard_depth_m=6.0, avg_n=10, avg_qc=50):
    """
    Menghitung komparasi 3 opsi jenis Fondasi Dalam paling populer di Indonesia:
    1. Strauss Pile (Bored Pile Manual) - Diameter 30 cm & 40 cm
    2. Mini Pile Precast (Tiang Pancang Kotak) - 20x20 cm & 25x25 cm
    3. Bored Pile Mesin - Diameter 60 cm
    """
    options = []
    
    # -------------------------------------------------------------
    # OPSI 1: STRAUSS PILE (BOR MANUAL) D = 30 cm
    # -------------------------------------------------------------
    d1 = 0.30  # meter
    area_p1 = (math.pi / 4.0) * (d1 ** 2)
    perim1 = math.pi * d1
    depth1 = min(hard_depth_m, 6.0)  # bor manual umumnya max 6-8m
    # Kapasitas ujung Qp (kN) & friksi Qs (kN)
    # Acuan Meyerhof untuk tiang bor: qp = 14 * N_end (Ton/m2) = 140 * N_end (kPa)
    # qs = 0.2 * N_avg (Ton/m2) = 2.0 * N_avg (kPa)
    qp1 = min(4000.0, 140.0 * max(15, avg_n if avg_n else 15)) * area_p1
    qs1 = (2.0 * max(5, avg_n if avg_n else 8)) * perim1 * depth1
    q_ult1 = qp1 + qs1
    q_all1 = round(q_ult1 / 3.0, 1)  # SF = 3
    q_all1 = max(110.0, min(180.0, q_all1))  # Batas wajar struktural beton K-250 tiang bor 30cm (11-18 ton)
    
    n_piles1 = max(1, math.ceil(p_axial_kN / q_all1))
    cap_cost1 = n_piles1 * 1.0  # Bobot biaya relatif
    
    options.append({
        "type_id": "strauss_pile",
        "name": "Strauss Pile (Bor Manual Ø30 cm)",
        "dim_label": "Diameter 30 cm",
        "diameter": d1,
        "depth": depth1,
        "q_all_single_kN": q_all1,
        "q_all_single_ton": round(q_all1 / 9.81, 1),
        "n_piles": n_piles1,
        "cap_size": f"{0.60 * n_piles1:.2f} m × {0.60:.2f} m" if n_piles1 <= 2 else "1.10 m × 1.10 m",
        "total_capacity_kN": round(n_piles1 * q_all1, 1),
        "vibration": "Nol (Tanpa Getaran - Aman Tetangga)",
        "equipment": "Tripod Manual Ringkas (Bisa Masuk Gang)",
        "suitability": "Rumah Tinggal 2-3 Lantai, Kawasan Padat Penduduk",
        "rank": 1 if p_axial_kN < 450 else 2
    })

    # -------------------------------------------------------------
    # OPSI 2: MINI PILE PRECAST (TIANG PANCANG 20x20 cm)
    # -------------------------------------------------------------
    b2 = 0.20  # meter
    area_p2 = b2 * b2
    perim2 = 4.0 * b2
    depth2 = hard_depth_m
    # Kapasitas tiang pancang pabrikasi mutu K-450 / K-500
    # Kapasitas dukung izin tiang pancang 20x20 umumnya 20 - 25 Ton (200 - 245 kN)
    q_all2 = 220.0  # ~22.4 Ton
    n_piles2 = max(1, math.ceil(p_axial_kN / q_all2))
    
    options.append({
        "type_id": "mini_pile_20",
        "name": "Mini Pile Precast (Tiang Pancang 20×20 cm)",
        "dim_label": "Kotak 20×20 cm",
        "diameter": b2,
        "depth": depth2,
        "q_all_single_kN": q_all2,
        "q_all_single_ton": round(q_all2 / 9.81, 1),
        "n_piles": n_piles2,
        "cap_size": f"{0.70 * n_piles2:.2f} m × {0.70:.2f} m" if n_piles2 <= 2 else "1.20 m × 1.20 m",
        "total_capacity_kN": round(n_piles2 * q_all2, 1),
        "vibration": "Sedang (Alat Drop Hammer / Hydraulic Jack)",
        "equipment": "Mesin Pancang Drop Hammer / Jack-in Pile",
        "suitability": "Ruko, Gedung 3-4 Lantai, Area Luas Bebas Getaran",
        "rank": 1 if p_axial_kN >= 450 else 2
    })

    # -------------------------------------------------------------
    # OPSI 3: BORED PILE MESIN D = 50 cm
    # -------------------------------------------------------------
    d3 = 0.50
    area_p3 = (math.pi / 4.0) * (d3 ** 2)
    perim3 = math.pi * d3
    depth3 = max(hard_depth_m, 8.0)
    # Tiang bor mesin diameter 50cm mutu K-350 memiliki kapasitas 50 - 80 Ton (500 - 800 kN)
    q_all3 = 550.0  # ~56 Ton
    n_piles3 = max(1, math.ceil(p_axial_kN / q_all3))

    options.append({
        "type_id": "bored_pile_mesin",
        "name": "Bored Pile Mesin (Ø50 cm)",
        "dim_label": "Diameter 50 cm",
        "diameter": d3,
        "depth": depth3,
        "q_all_single_kN": q_all3,
        "q_all_single_ton": round(q_all3 / 9.81, 1),
        "n_piles": n_piles3,
        "cap_size": f"{0.90 * n_piles3:.2f} m × {0.90:.2f} m" if n_piles3 <= 2 else "1.60 m × 1.60 m",
        "total_capacity_kN": round(n_piles3 * q_all3, 1),
        "vibration": "Nol (Tanpa Getaran)",
        "equipment": "Rig Mesin Bor Putar (Hydraulic Rotary Rig)",
        "suitability": "Gedung Komersial Berat ≥ 4 Lantai, Rumah Sakit",
        "rank": 3
    })

    # Urutkan berdasarkan rank
    options.sort(key=lambda x: x["rank"])
    return options


def compare_foundation_shapes(p_axial_kN, c_val, phi_val, gamma_val, gamma_sat_val, df_val, dw_val, sf_target=3.0, hf_val=0.40):
    """
    Sistem Penilai Cerdas Membandingkan 4 Bentuk Fondasi Dangkal:
    1. Bujur Sangkar (Square)
    2. Persegi Panjang (Rectangular, rasio 1.5 : 1)
    3. Lingkaran (Circular)
    4. Jalur / Menerus (Strip Footing)
    Menghitung dimensi setara yang aman, volume beton, efisiensi, dan rekomendasi terbaik.
    """
    from modules.bearing_capacity import calculate_terzaghi, calculate_meyerhof, calculate_vesic, calculate_hansen

    results = []

    # 1. BUJUR SANGKAR (B = L)
    # Cari B minimum yang aman
    b_sq = 0.80
    while b_sq <= 4.0:
        area_sq = b_sq * b_sq
        q_k = (p_axial_kN / area_sq) + (24.0 * hf_val) + (gamma_val * (df_val - hf_val))
        res_tz = calculate_terzaghi(c_val, phi_val, gamma_val, gamma_sat_val, b_sq, b_sq, df_val, dw_val, shape="Bujur Sangkar")
        qun = res_tz["qu"] - res_tz["po"]
        qall = (qun / sf_target) + res_tz["po"]
        if q_k <= qall:
            break
        b_sq += 0.05
    b_sq = round(b_sq, 2)
    area_sq = round(b_sq * b_sq, 2)
    vol_sq = round(area_sq * hf_val, 2)
    sf_sq = round(res_tz["qu"] / q_k, 2)

    results.append({
        "shape": "Bujur Sangkar (Square)",
        "icon": "⏹️",
        "dimensions": f"B = {b_sq:.2f} m × L = {b_sq:.2f} m",
        "area": area_sq,
        "vol_beton": vol_sq,
        "sf": sf_sq,
        "is_safe": True,
        "practicality": "⭐⭐⭐⭐⭐ Paling Mudah & Simetris",
        "practicality_desc": "Penulangan dua arah sama (Mx = My), bekisting 4 sisi lurus sederhana, paling banyak digunakan.",
        "score": 95
    })

    # 2. PERSEGI PANJANG (L = 1.5 * B)
    b_rec = 0.70
    while b_rec <= 3.5:
        l_rec = round(b_rec * 1.5, 2)
        area_rec = b_rec * l_rec
        q_k = (p_axial_kN / area_rec) + (24.0 * hf_val) + (gamma_val * (df_val - hf_val))
        res_tz = calculate_terzaghi(c_val, phi_val, gamma_val, gamma_sat_val, b_rec, l_rec, df_val, dw_val, shape="Persegi Panjang")
        qun = res_tz["qu"] - res_tz["po"]
        qall = (qun / sf_target) + res_tz["po"]
        if q_k <= qall:
            break
        b_rec += 0.05
    b_rec = round(b_rec, 2)
    l_rec = round(b_rec * 1.5, 2)
    area_rec = round(b_rec * l_rec, 2)
    vol_rec = round(area_rec * hf_val, 2)
    sf_rec = round(res_tz["qu"] / q_k, 2)

    results.append({
        "shape": "Persegi Panjang (Rectangular)",
        "icon": "▭",
        "dimensions": f"B = {b_rec:.2f} m × L = {l_rec:.2f} m",
        "area": area_rec,
        "vol_beton": vol_rec,
        "sf": sf_rec,
        "is_safe": True,
        "practicality": "⭐⭐⭐⭐ Sangat Baik untuk Lahan Terbatas",
        "practicality_desc": "Sangat ideal jika ada batas tanah tetangga di salah satu sisi, namun penulangan arah X dan Y berbeda.",
        "score": 88
    })

    # 3. LINGKARAN (Diameter D)
    d_circ = 0.90
    while d_circ <= 4.5:
        area_circ = (math.pi / 4.0) * (d_circ ** 2)
        q_k = (p_axial_kN / area_circ) + (24.0 * hf_val) + (gamma_val * (df_val - hf_val))
        res_tz = calculate_terzaghi(c_val, phi_val, gamma_val, gamma_sat_val, d_circ, d_circ, df_val, dw_val, shape="Lingkaran")
        qun = res_tz["qu"] - res_tz["po"]
        qall = (qun / sf_target) + res_tz["po"]
        if q_k <= qall:
            break
        d_circ += 0.05
    d_circ = round(d_circ, 2)
    area_circ = round((math.pi / 4.0) * (d_circ ** 2), 2)
    vol_circ = round(area_circ * hf_val, 2)
    sf_circ = round(res_tz["qu"] / q_k, 2)

    results.append({
        "shape": "Lingkaran (Circular)",
        "icon": "⭕",
        "dimensions": f"Diameter D = {d_circ:.2f} m",
        "area": area_circ,
        "vol_beton": vol_circ,
        "sf": sf_circ,
        "is_safe": True,
        "practicality": "⭐⭐⭐ Khusus Kolom Bulat / Menara",
        "practicality_desc": "Distribusi tegangan radial sangat merata, namun bekisting melingkar membutuhkan fabrikasi plat khusus.",
        "score": 80
    })

    # 4. JALUR / MENERUS (Strip Footing per meter lari)
    # Asumsi beban per meter lari p_strip = p_axial / 4.0 (jarak kolom 4m)
    p_strip = p_axial_kN / 4.0
    b_str = 0.60
    while b_str <= 3.0:
        area_str = b_str * 1.0  # per 1 meter panjang
        q_k = (p_strip / area_str) + (24.0 * hf_val) + (gamma_val * (df_val - hf_val))
        res_tz = calculate_terzaghi(c_val, phi_val, gamma_val, gamma_sat_val, b_str, 10.0, df_val, dw_val, shape="Memanjang")
        qun = res_tz["qu"] - res_tz["po"]
        qall = (qun / sf_target) + res_tz["po"]
        if q_k <= qall:
            break
        b_str += 0.05
    b_str = round(b_str, 2)
    vol_str = round(b_str * 1.0 * hf_val, 2)
    sf_str = round(res_tz["qu"] / q_k, 2)

    results.append({
        "shape": "Pondasi Jalur / Menerus (Strip)",
        "icon": "🧱",
        "dimensions": f"Lebar B = {b_str:.2f} m (per meter lari)",
        "area": round(b_str * 1.0, 2),
        "vol_beton": vol_str,
        "sf": sf_str,
        "is_safe": True,
        "practicality": "⭐⭐⭐⭐ Khusus Dinding Bata Pemikul",
        "practicality_desc": "Cocok untuk dinding penyekat atau deretan kolom rapat. Menyerap momen diferensial sepanjang dinding.",
        "score": 85
    })

    # Urutkan berdasarkan score
    results.sort(key=lambda x: x["score"], reverse=True)
    return results
