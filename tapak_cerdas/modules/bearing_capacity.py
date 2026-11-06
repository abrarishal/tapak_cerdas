"""
=============================================================================
TAPAK CERDAS - ENGINE KAPASITAS DUKUNG TANAH PONDASI DANGKAL
=============================================================================
File: modules/bearing_capacity.py
Deskripsi: Implementasi eksak 4 metode kapasitas dukung:
           1. Terzaghi (1943)
           2. Meyerhof (1963)
           3. Vesic (1975)
           4. Brinch Hansen (1970)
           Dilengkapi koreksi muka air tanah (MAT) terintegrasi.
=============================================================================
"""

import math

def calculate_terzaghi(c, phi_deg, gamma_moist, gamma_sat, B, L, Df, dw, shape="Bujur Sangkar", local_shear=False):
    """
    Kapasitas dukung Terzaghi (1943)
    Sesuai Bab 3.3.1 Buku Analisis dan Perancangan Fondasi - I (Hal 111-127).
    """
    phi = math.radians(phi_deg)
    
    # Reduksi jika keruntuhan geser lokal
    if local_shear:
        c = (2.0 / 3.0) * c
        phi = math.atan((2.0 / 3.0) * math.tan(phi))
        phi_deg = math.degrees(phi)

    # Faktor kapasitas dukung Terzaghi (Tabel 3.1)
    if phi_deg == 0:
        Nc, Nq, Ngamma = 5.7, 1.0, 0.0
    else:
        # Rumus analitis Terzaghi dengan pendekatan Cernica (1995)
        # a = exp((3*pi/4 - phi/2)*tan(phi))
        term_a = (0.75 * math.pi - phi / 2.0) * math.tan(phi)
        a = math.exp(term_a)
        cos_term = math.cos(math.radians(45.0) + phi / 2.0)
        
        Nq = (a**2) / (2.0 * (cos_term**2))
        Nc = (Nq - 1.0) / math.tan(phi)
        
        # Kpy Cernica (1995)
        kpy = 3.0 * (math.tan(math.radians(45.0 + 0.5 * (phi_deg + 33.0))))**2
        Ngamma = 0.5 * math.tan(phi) * (kpy / (math.cos(phi)**2) - 1.0)
        if Ngamma < 0:
            Ngamma = 0.0

    # Koreksi Muka Air Tanah (MAT)
    gamma_w = 9.81
    gamma_eff_sub = gamma_sat - gamma_w  # gamma apung
    
    # Suku ke-2 (Overburden po pada dasar fondasi)
    if dw >= Df:
        po = gamma_moist * Df
    elif dw <= 0:
        po = gamma_eff_sub * Df
    else:
        po = (gamma_moist * dw) + (gamma_eff_sub * (Df - dw))
        
    # Suku ke-3 (Berat tanah di bawah dasar fondasi)
    z = dw - Df
    if z >= B:
        gamma_below = gamma_moist
    elif z <= 0:
        gamma_below = gamma_eff_sub
    else:
        # Rata-rata terbobot (Persamaan 3.23b)
        gamma_below = gamma_eff_sub + (z / B) * (gamma_moist - gamma_eff_sub)

    # Pengaruh Bentuk Pondasi Terzaghi (Persamaan 3.21a, 3.21b, 3.21c)
    if shape == "Bujur Sangkar" or (shape == "Persegi Panjang" and B == L):
        qu = 1.3 * c * Nc + po * Nq + 0.4 * gamma_below * B * Ngamma
    elif shape == "Lingkaran":
        qu = 1.3 * c * Nc + po * Nq + 0.3 * gamma_below * B * Ngamma
    elif shape == "Persegi Panjang":
        qu = c * Nc * (1.0 + 0.3 * (B / L)) + po * Nq + 0.5 * gamma_below * B * Ngamma * (1.0 - 0.2 * (B / L))
    else:  # Memanjang / Strip Footing
        qu = c * Nc + po * Nq + 0.5 * gamma_below * B * Ngamma

    return {
        "metode": "Terzaghi (1943)",
        "Nc": round(Nc, 2), "Nq": round(Nq, 2), "Ngamma": round(Ngamma, 2),
        "po": round(po, 2), "gamma_eff": round(gamma_below, 2),
        "qu": round(qu, 2)
    }


def calculate_meyerhof(c, phi_deg, gamma_moist, gamma_sat, B, L, Df, dw, delta_deg=0.0, shape="Bujur Sangkar"):
    """
    Kapasitas dukung Meyerhof (1963)
    Sesuai Bab 3.3.4 Buku Analisis dan Perancangan Fondasi - I (Hal 147-167).
    """
    phi = math.radians(phi_deg)
    
    if phi_deg == 0:
        Nc, Nq, Ngamma = 5.14, 1.0, 0.0
    else:
        Nq = (math.tan(math.radians(45.0) + phi / 2.0)**2) * math.exp(math.pi * math.tan(phi))
        Nc = (Nq - 1.0) / math.tan(phi)
        Ngamma = (Nq - 1.0) * math.tan(math.radians(1.4 * phi_deg))

    # Tentukan Rasio B/L berdasarkan Bentuk Pondasi
    if "Memanjang" in shape or "Strip" in shape or "Jalur" in shape:
        ratio_BL = 0.0
    elif shape == "Lingkaran" or shape == "Bujur Sangkar" or B == L:
        ratio_BL = 1.0
    else:
        ratio_BL = min(1.0, B / L) if (L and L > 0) else 1.0

    # Faktor Bentuk Meyerhof (Tabel 3.4a)
    kp = math.tan(math.radians(45.0) + phi / 2.0)**2
    sc = 1.0 + 0.2 * ratio_BL * kp
    if phi_deg >= 10.0:
        sq = 1.0 + 0.1 * ratio_BL * kp
        sgamma = sq
    else:
        sq = 1.0
        sgamma = 1.0

    # Faktor Kedalaman Meyerhof (Tabel 3.4b)
    sqrt_kp = math.tan(math.radians(45.0) + phi / 2.0)
    dc = 1.0 + 0.2 * (Df / B) * sqrt_kp
    if phi_deg >= 10.0:
        dq = 1.0 + 0.1 * (Df / B) * sqrt_kp
        dgamma = dq
    else:
        dq = 1.0
        dgamma = 1.0

    # Faktor Kemiringan Beban (Tabel 3.4c)
    ic = (1.0 - delta_deg / 90.0)**2
    iq = ic
    if phi_deg >= 10.0:
        igamma = (1.0 - delta_deg / phi_deg)**2 if delta_deg <= phi_deg else 0.0
    else:
        igamma = 1.0

    # Koreksi Muka Air Tanah
    gamma_w = 9.81
    gamma_eff_sub = gamma_sat - gamma_w
    
    if dw >= Df:
        po = gamma_moist * Df
    elif dw <= 0:
        po = gamma_eff_sub * Df
    else:
        po = (gamma_moist * dw) + (gamma_eff_sub * (Df - dw))
        
    z = dw - Df
    if z >= B:
        gamma_below = gamma_moist
    elif z <= 0:
        gamma_below = gamma_eff_sub
    else:
        gamma_below = gamma_eff_sub + (z / B) * (gamma_moist - gamma_eff_sub)

    qu = (sc * dc * ic * c * Nc) + (sq * dq * iq * po * Nq) + (sgamma * dgamma * igamma * 0.5 * B * gamma_below * Ngamma)

    return {
        "metode": "Meyerhof (1963)",
        "Nc": round(Nc, 2), "Nq": round(Nq, 2), "Ngamma": round(Ngamma, 2),
        "sc": round(sc, 2), "sq": round(sq, 2), "sgamma": round(sgamma, 2),
        "dc": round(dc, 2), "dq": round(dq, 2), "dgamma": round(dgamma, 2),
        "po": round(po, 2), "gamma_eff": round(gamma_below, 2),
        "qu": round(qu, 2)
    }


def calculate_vesic(c, phi_deg, gamma_moist, gamma_sat, B, L, Df, dw, shape="Bujur Sangkar"):
    """
    Kapasitas dukung Vesic (1975)
    Sesuai Bab 3.3.6 Buku Analisis dan Perancangan Fondasi - I (Hal 176-180).
    """
    phi = math.radians(phi_deg)
    
    if phi_deg == 0:
        Nc, Nq, Ngamma = 5.14, 1.0, 0.0
    else:
        Nq = (math.tan(math.radians(45.0) + phi / 2.0)**2) * math.exp(math.pi * math.tan(phi))
        Nc = (Nq - 1.0) / math.tan(phi)
        Ngamma = 2.0 * (Nq + 1.0) * math.tan(phi)  # Caquot & Kerisel

    # Faktor Bentuk Vesic (Tabel 3.6a)
    if "Memanjang" in shape or "Strip" in shape or "Jalur" in shape:
        sc = 1.0
        sq = 1.0
        sgamma = 1.0
    elif shape == "Lingkaran" or shape == "Bujur Sangkar" or B == L:
        sc = 1.0 + (Nq / Nc) if Nc > 0 else 1.0
        sq = 1.0 + math.tan(phi)
        sgamma = 0.6
    else:
        ratio_BL = min(1.0, B / L) if (L and L > 0) else 1.0
        sc = 1.0 + ratio_BL * (Nq / Nc) if Nc > 0 else 1.0
        sq = 1.0 + ratio_BL * math.tan(phi)
        sgamma = max(0.6, 1.0 - 0.4 * ratio_BL)

    # Faktor Kedalaman Vesic (Tabel 3.6b)
    k = (Df / B) if (Df / B) <= 1.0 else math.atan(Df / B)
    dc = 1.0 + 0.4 * k
    dq = 1.0 + 2.0 * k * math.tan(phi) * ((1.0 - math.sin(phi))**2)
    dgamma = 1.0

    # Koreksi Muka Air Tanah
    gamma_w = 9.81
    gamma_eff_sub = gamma_sat - gamma_w
    
    if dw >= Df:
        po = gamma_moist * Df
    elif dw <= 0:
        po = gamma_eff_sub * Df
    else:
        po = (gamma_moist * dw) + (gamma_eff_sub * (Df - dw))
        
    z = dw - Df
    if z >= B:
        gamma_below = gamma_moist
    elif z <= 0:
        gamma_below = gamma_eff_sub
    else:
        gamma_below = gamma_eff_sub + (z / B) * (gamma_moist - gamma_eff_sub)

    qu = (sc * dc * c * Nc) + (sq * dq * po * Nq) + (sgamma * dgamma * 0.5 * B * gamma_below * Ngamma)

    return {
        "metode": "Vesic (1975)",
        "Nc": round(Nc, 2), "Nq": round(Nq, 2), "Ngamma": round(Ngamma, 2),
        "sc": round(sc, 2), "sq": round(sq, 2), "sgamma": round(sgamma, 2),
        "dc": round(dc, 2), "dq": round(dq, 2), "dgamma": round(dgamma, 2),
        "po": round(po, 2), "gamma_eff": round(gamma_below, 2),
        "qu": round(qu, 2)
    }


def calculate_hansen(c, phi_deg, gamma_moist, gamma_sat, B, L, Df, dw, shape="Bujur Sangkar"):
    """
    Kapasitas dukung Brinch Hansen (1970)
    Sesuai Bab 3.3.5 Buku Analisis dan Perancangan Fondasi - I (Hal 171-175).
    """
    phi = math.radians(phi_deg)
    
    # Koreksi Muka Air Tanah
    gamma_w = 9.81
    gamma_eff_sub = gamma_sat - gamma_w
    
    if dw >= Df:
        po = gamma_moist * Df
    elif dw <= 0:
        po = gamma_eff_sub * Df
    else:
        po = (gamma_moist * dw) + (gamma_eff_sub * (Df - dw))
        
    z = dw - Df
    if z >= B:
        gamma_below = gamma_moist
    elif z <= 0:
        gamma_below = gamma_eff_sub
    else:
        gamma_below = gamma_eff_sub + (z / B) * (gamma_moist - gamma_eff_sub)

    k = (Df / B) if (Df / B) <= 1.0 else math.atan(Df / B)

    # Tentukan rasio B/L
    if "Memanjang" in shape or "Strip" in shape or "Jalur" in shape:
        ratio_BL = 0.0
    elif shape == "Lingkaran" or shape == "Bujur Sangkar" or B == L:
        ratio_BL = 1.0
    else:
        ratio_BL = min(1.0, B / L) if (L and L > 0) else 1.0

    # Kasus lempung jenuh phi = 0
    if phi_deg == 0:
        Nc, Nq, Ngamma = 5.14, 1.0, 0.0
        sc_prime = 0.2 * ratio_BL
        dc_prime = 0.4 * k
        qu = 5.14 * c * (1.0 + sc_prime + dc_prime) + po
        sc, sq, sgamma = 1.0 + sc_prime, 1.0, 1.0
        dc, dq, dgamma = 1.0 + dc_prime, 1.0, 1.0
    else:
        Nq = (math.tan(math.radians(45.0) + phi / 2.0)**2) * math.exp(math.pi * math.tan(phi))
        Nc = (Nq - 1.0) / math.tan(phi)
        Ngamma = 1.5 * (Nq - 1.0) * math.tan(phi)
        
        sc = 1.0 + ratio_BL * (Nq / Nc)
        sq = 1.0 + ratio_BL * math.sin(phi)
        sgamma = max(0.6, 1.0 - 0.4 * ratio_BL)
        
        dc = 1.0 + 0.4 * k
        dq = 1.0 + 2.0 * k * math.tan(phi) * ((1.0 - math.sin(phi))**2)
        dgamma = 1.0
        
        qu = (sc * dc * c * Nc) + (sq * dq * po * Nq) + (sgamma * dgamma * 0.5 * B * gamma_below * Ngamma)

    return {
        "metode": "Hansen (1970)",
        "Nc": round(Nc, 2), "Nq": round(Nq, 2), "Ngamma": round(Ngamma, 2),
        "sc": round(sc, 2), "sq": round(sq, 2), "sgamma": round(sgamma, 2),
        "dc": round(dc, 2), "dq": round(dq, 2), "dgamma": round(dgamma, 2),
        "po": round(po, 2), "gamma_eff": round(gamma_below, 2),
        "qu": round(qu, 2)
    }
