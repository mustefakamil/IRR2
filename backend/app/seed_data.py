"""Default reference databases (crops, soils, irrigation systems).

All values are explicit FAO-56 defaults and are editable by the user once
loaded into the database (spec section 37: "any default value must be clearly
defined and user-editable").

Crop fields:
  l_ini/l_dev/l_mid/l_late : stage lengths (days)   -- FAO-56 Table 11
  kc_ini/kc_mid/kc_end     : crop coefficients        -- FAO-56 Table 12
  zr_min/zr_max            : root depth (m)           -- FAO-56 Table 22
  p                        : depletion fraction (MAD) -- FAO-56 Table 22
  ky                       : yield response factor    -- FAO-33
  source                   : 'workbook' (Riyadh model) or 'fao56'
"""

# name_en, name_ar, scientific, category, Lini, Ldev, Lmid, Llate,
# Kcini, Kcmid, Kcend, Zrmin, Zrmax, p, height_m, Ky, source
CROPS = [
    # --- Crops carried over exactly from the reference Riyadh workbook -------
    ("Tomato", "الطماطم", "Solanum lycopersicum", "Vegetable",
     30, 40, 45, 30, 0.60, 1.15, 0.80, 0.25, 1.00, 0.40, 0.6, 1.05, "workbook"),
    ("Sweet Pepper", "الفلفل الحلو", "Capsicum annuum", "Vegetable",
     30, 35, 40, 20, 0.60, 1.05, 0.90, 0.25, 0.80, 0.30, 0.7, 1.10, "workbook"),
    ("Potato", "البطاطس", "Solanum tuberosum", "Vegetable",
     25, 30, 45, 30, 0.50, 1.15, 0.75, 0.30, 0.60, 0.35, 0.6, 1.10, "workbook"),
    ("Alfalfa", "البرسيم", "Medicago sativa", "Field",
     10, 30, 15, 10, 0.40, 0.95, 0.90, 0.40, 1.20, 0.55, 0.7, 1.10, "workbook"),
    ("Small Vegetables (Leafy)", "خضروات ورقية", "—", "Vegetable",
     20, 30, 30, 15, 0.70, 1.05, 0.95, 0.25, 0.65, 0.30, 0.3, 1.05, "workbook"),

    # --- FAO-56 field crops -------------------------------------------------
    ("Wheat", "القمح", "Triticum aestivum", "Field",
     30, 40, 40, 30, 0.40, 1.15, 0.35, 0.20, 1.50, 0.55, 1.0, 1.05, "fao56"),
    ("Barley", "الشعير", "Hordeum vulgare", "Field",
     20, 25, 60, 30, 0.30, 1.15, 0.25, 0.20, 1.30, 0.55, 1.0, 1.00, "fao56"),
    ("Maize", "الذرة", "Zea mays", "Field",
     30, 40, 50, 30, 0.30, 1.20, 0.35, 0.30, 1.30, 0.55, 1.0, 1.25, "fao56"),
    ("Sorghum", "الذرة الرفيعة", "Sorghum bicolor", "Field",
     20, 35, 40, 30, 0.30, 1.05, 0.55, 0.40, 1.50, 0.55, 1.0, 0.90, "fao56"),
    ("Rice", "الأرز", "Oryza sativa", "Field",
     30, 30, 60, 30, 1.05, 1.20, 0.75, 0.30, 0.60, 0.20, 1.0, 1.00, "fao56"),
    ("Cotton", "القطن", "Gossypium hirsutum", "Field",
     30, 50, 60, 55, 0.35, 1.18, 0.60, 0.40, 1.50, 0.65, 1.2, 0.85, "fao56"),
    ("Sunflower", "دوار الشمس", "Helianthus annuus", "Field",
     25, 35, 45, 25, 0.35, 1.10, 0.35, 0.40, 1.20, 0.45, 1.5, 0.95, "fao56"),
    ("Safflower", "القرطم", "Carthamus tinctorius", "Field",
     20, 35, 45, 25, 0.35, 1.10, 0.25, 0.40, 1.20, 0.60, 1.0, 0.80, "fao56"),
    ("Soybean", "فول الصويا", "Glycine max", "Field",
     20, 30, 60, 25, 0.40, 1.15, 0.50, 0.30, 1.00, 0.50, 0.75, 0.85, "fao56"),
    ("Groundnut", "الفول السوداني", "Arachis hypogaea", "Field",
     25, 35, 45, 25, 0.40, 1.15, 0.60, 0.30, 0.70, 0.50, 0.4, 0.70, "fao56"),
    ("Sesame", "السمسم", "Sesamum indicum", "Field",
     20, 30, 40, 20, 0.35, 1.10, 0.25, 0.50, 1.50, 0.60, 1.0, 0.90, "fao56"),
    ("Millet", "الدخن", "Pennisetum glaucum", "Field",
     15, 25, 40, 25, 0.30, 1.00, 0.30, 0.40, 1.20, 0.55, 1.5, 0.90, "fao56"),
    ("Chickpea", "الحمص", "Cicer arietinum", "Field",
     20, 30, 40, 20, 0.40, 1.00, 0.35, 0.30, 0.80, 0.50, 0.4, 0.80, "fao56"),
    ("Lentil", "العدس", "Lens culinaris", "Field",
     20, 30, 40, 20, 0.40, 1.10, 0.30, 0.30, 0.80, 0.50, 0.5, 0.80, "fao56"),
    ("Faba Bean", "الفول", "Vicia faba", "Field",
     15, 25, 35, 15, 0.50, 1.15, 0.30, 0.50, 0.70, 0.45, 0.8, 1.00, "fao56"),
    ("Quinoa", "الكينوا", "Chenopodium quinoa", "Field",
     15, 25, 40, 20, 0.35, 1.00, 0.30, 0.30, 0.80, 0.50, 1.0, 0.90, "fao56"),
    ("Buckwheat", "الحنطة السوداء", "Fagopyrum esculentum", "Field",
     15, 20, 30, 15, 0.35, 1.05, 0.30, 0.30, 0.60, 0.55, 0.7, 0.90, "fao56"),

    # --- Additional cereals & grains ---------------------------------------
    ("Durum Wheat", "القمح الصلب", "Field", "Triticum durum",
     25, 35, 45, 30, 0.40, 1.15, 0.35, 0.20, 1.50, 0.55, 1.0, 1.05, "fao56"),
    ("Oats", "الشوفان", "Field", "Avena sativa",
     20, 30, 45, 25, 0.30, 1.15, 0.25, 0.20, 1.30, 0.55, 1.0, 1.00, "fao56"),
    ("Rye", "الجاودار", "Field", "Secale cereale",
     20, 30, 45, 25, 0.30, 1.10, 0.25, 0.30, 1.50, 0.55, 1.2, 1.00, "fao56"),
    ("Triticale", "التريتيكال", "Field", "x Triticosecale",
     25, 35, 45, 30, 0.35, 1.15, 0.30, 0.20, 1.40, 0.55, 1.0, 1.00, "fao56"),
    ("Pearl Millet", "الدخن اللؤلؤي", "Field", "Pennisetum glaucum",
     15, 25, 40, 25, 0.30, 1.00, 0.30, 0.40, 1.20, 0.55, 2.0, 0.90, "fao56"),
    ("Finger Millet", "الدخن الإصبعي", "Field", "Eleusine coracana",
     20, 30, 40, 20, 0.30, 1.00, 0.30, 0.30, 1.00, 0.55, 1.0, 0.90, "fao56"),
    ("Teff", "التيف", "Field", "Eragrostis tef",
     15, 25, 40, 20, 0.30, 1.00, 0.30, 0.20, 0.80, 0.55, 0.8, 0.90, "fao56"),
    ("Spelt", "القمح المقشور", "Field", "Triticum spelta",
     25, 35, 45, 30, 0.40, 1.15, 0.35, 0.20, 1.40, 0.55, 1.1, 1.00, "fao56"),

    # --- Additional industrial / field crops -------------------------------
    ("Sugar Beet", "بنجر السكر", "Field", "Beta vulgaris",
     30, 45, 60, 30, 0.35, 1.20, 0.70, 0.70, 1.20, 0.55, 0.5, 1.10, "fao56"),
    ("Sugarcane (ratoon)", "قصب السكر", "Field", "Saccharum officinarum",
     30, 60, 180, 60, 0.40, 1.25, 0.75, 1.20, 2.00, 0.65, 3.0, 1.20, "fao56"),
    ("Canola / Rapeseed", "الكانولا / اللفت الزيتي", "Field", "Brassica napus",
     25, 35, 45, 25, 0.35, 1.10, 0.35, 0.40, 1.20, 0.60, 1.0, 0.90, "fao56"),
    ("Flax / Linseed", "الكتان", "Field", "Linum usitatissimum",
     25, 35, 50, 40, 0.35, 1.10, 0.25, 0.40, 1.20, 0.50, 1.0, 0.90, "fao56"),
    ("Mustard", "الخردل", "Field", "Brassica juncea",
     20, 30, 35, 20, 0.35, 1.10, 0.35, 0.40, 1.20, 0.55, 1.0, 0.90, "fao56"),
    ("Tobacco", "التبغ", "Field", "Nicotiana tabacum",
     10, 30, 60, 30, 0.35, 1.10, 0.80, 0.50, 1.00, 0.35, 1.0, 0.90, "fao56"),
    ("Sweet Potato", "البطاطا الحلوة", "Field", "Ipomoea batatas",
     15, 30, 50, 30, 0.50, 1.15, 0.65, 1.00, 1.50, 0.65, 0.4, 1.00, "fao56"),
    ("Cassava", "الكسافا", "Field", "Manihot esculenta",
     20, 40, 90, 60, 0.30, 0.90, 0.50, 0.50, 0.80, 0.35, 1.0, 1.00, "fao56"),
    ("Cowpea", "اللوبيا", "Field", "Vigna unguiculata",
     20, 30, 30, 20, 0.40, 1.05, 0.60, 0.60, 1.00, 0.45, 0.4, 0.85, "fao56"),
    ("Mung Bean", "الماش", "Field", "Vigna radiata",
     20, 30, 30, 15, 0.40, 1.05, 0.35, 0.30, 0.60, 0.45, 0.4, 0.85, "fao56"),
    ("Pigeon Pea", "البازلاء الحمامية", "Field", "Cajanus cajan",
     20, 40, 60, 30, 0.40, 1.05, 0.35, 0.50, 1.00, 0.45, 1.5, 0.85, "fao56"),
    ("Field Pea", "البازلاء الحقلية", "Field", "Pisum arvense",
     20, 25, 35, 15, 0.50, 1.15, 0.30, 0.60, 1.00, 0.40, 0.5, 1.00, "fao56"),
    ("Guar", "الجوار", "Field", "Cyamopsis tetragonoloba",
     20, 30, 40, 20, 0.35, 1.05, 0.45, 0.40, 1.00, 0.50, 0.8, 0.90, "fao56"),

    # --- FAO-56 vegetables --------------------------------------------------
    ("Cucumber", "الخيار", "Cucumis sativus", "Vegetable",
     20, 30, 40, 15, 0.60, 1.00, 0.75, 0.30, 1.00, 0.50, 0.3, 1.10, "fao56"),
    ("Hot Pepper", "الفلفل الحار", "Capsicum frutescens", "Vegetable",
     30, 35, 40, 20, 0.60, 1.05, 0.90, 0.25, 0.80, 0.30, 0.7, 1.10, "fao56"),
    ("Eggplant", "الباذنجان", "Solanum melongena", "Vegetable",
     30, 40, 40, 20, 0.60, 1.05, 0.90, 0.30, 1.00, 0.45, 0.8, 1.10, "fao56"),
    ("Onion", "البصل", "Allium cepa", "Vegetable",
     15, 25, 70, 40, 0.70, 1.05, 0.75, 0.20, 0.60, 0.30, 0.4, 1.10, "fao56"),
    ("Garlic", "الثوم", "Allium sativum", "Vegetable",
     20, 30, 40, 20, 0.70, 1.00, 0.70, 0.20, 0.50, 0.30, 0.3, 1.05, "fao56"),
    ("Carrot", "الجزر", "Daucus carota", "Vegetable",
     20, 30, 30, 20, 0.70, 1.05, 0.95, 0.30, 1.00, 0.35, 0.3, 1.10, "fao56"),
    ("Lettuce", "الخس", "Lactuca sativa", "Vegetable",
     20, 30, 15, 10, 0.70, 1.00, 0.95, 0.20, 0.50, 0.30, 0.3, 1.05, "fao56"),
    ("Cabbage", "الملفوف", "Brassica oleracea capitata", "Vegetable",
     20, 30, 40, 15, 0.70, 1.05, 0.95, 0.40, 0.60, 0.45, 0.4, 0.95, "fao56"),
    ("Cauliflower", "القرنبيط", "Brassica oleracea botrytis", "Vegetable",
     20, 30, 40, 15, 0.70, 1.05, 0.95, 0.40, 0.70, 0.45, 0.4, 0.95, "fao56"),
    ("Broccoli", "البروكلي", "Brassica oleracea italica", "Vegetable",
     20, 30, 40, 15, 0.70, 1.05, 0.95, 0.40, 0.60, 0.45, 0.4, 0.95, "fao56"),
    ("Watermelon", "البطيخ", "Citrullus lanatus", "Vegetable",
     20, 30, 30, 30, 0.40, 1.00, 0.75, 0.80, 1.50, 0.40, 0.4, 1.10, "fao56"),
    ("Melon", "الشمام", "Cucumis melo", "Vegetable",
     25, 35, 40, 20, 0.50, 1.05, 0.75, 0.80, 1.50, 0.40, 0.4, 1.10, "fao56"),
    ("Pumpkin", "القرع", "Cucurbita maxima", "Vegetable",
     20, 30, 30, 20, 0.50, 1.00, 0.80, 0.50, 1.20, 0.35, 0.4, 1.05, "fao56"),
    ("Zucchini", "الكوسة", "Cucurbita pepo", "Vegetable",
     20, 30, 25, 15, 0.50, 0.95, 0.75, 0.40, 1.00, 0.50, 0.3, 1.05, "fao56"),
    ("Okra", "البامية", "Abelmoschus esculentus", "Vegetable",
     25, 35, 40, 20, 0.60, 1.15, 0.75, 0.40, 1.00, 0.45, 0.8, 1.05, "fao56"),
    ("Green Bean", "الفاصوليا", "Phaseolus vulgaris", "Vegetable",
     20, 30, 30, 10, 0.50, 1.05, 0.90, 0.30, 0.70, 0.45, 0.4, 1.15, "fao56"),

    # --- FAO-56 fruit trees (perennial; near-flat Kc, full-year cycle) ------
    ("Mango", "المانجو", "Mangifera indica", "Fruit",
     90, 90, 120, 65, 0.45, 0.90, 0.90, 0.90, 1.50, 0.50, 4.0, 1.00, "fao56"),
    ("Banana", "الموز", "Musa spp.", "Fruit",
     60, 90, 120, 95, 0.50, 1.10, 1.00, 0.50, 0.90, 0.35, 3.0, 1.20, "fao56"),
    ("Avocado", "الأفوكادو", "Persea americana", "Fruit",
     90, 90, 120, 65, 0.60, 0.85, 0.75, 0.60, 1.00, 0.70, 4.0, 1.00, "fao56"),
    ("Date Palm", "نخيل التمر", "Phoenix dactylifera", "Fruit",
     90, 90, 120, 65, 0.90, 0.95, 0.95, 1.50, 2.50, 0.50, 8.0, 1.00, "fao56"),
    ("Grape", "العنب", "Vitis vinifera", "Fruit",
     30, 60, 90, 60, 0.30, 0.85, 0.45, 1.00, 2.00, 0.45, 2.0, 0.85, "fao56"),
    ("Apple", "التفاح", "Malus domestica", "Fruit",
     60, 90, 120, 95, 0.45, 0.95, 0.70, 1.00, 2.00, 0.50, 4.0, 1.00, "fao56"),
    ("Pear", "الكمثرى", "Pyrus communis", "Fruit",
     60, 90, 120, 95, 0.45, 0.95, 0.70, 1.00, 2.00, 0.50, 4.0, 1.00, "fao56"),
    ("Peach", "الخوخ", "Prunus persica", "Fruit",
     30, 50, 130, 30, 0.45, 0.90, 0.65, 1.00, 2.00, 0.50, 3.0, 1.00, "fao56"),
    ("Apricot", "المشمش", "Prunus armeniaca", "Fruit",
     30, 50, 130, 30, 0.45, 0.90, 0.65, 1.00, 2.00, 0.50, 3.0, 1.00, "fao56"),
    ("Plum", "البرقوق", "Prunus domestica", "Fruit",
     30, 50, 130, 30, 0.45, 0.90, 0.65, 1.00, 2.00, 0.50, 3.0, 1.00, "fao56"),
    ("Fig", "التين", "Ficus carica", "Fruit",
     60, 90, 120, 95, 0.40, 0.85, 0.70, 0.80, 1.50, 0.50, 3.0, 1.00, "fao56"),
    ("Pomegranate", "الرمان", "Punica granatum", "Fruit",
     60, 90, 120, 95, 0.40, 0.85, 0.70, 0.80, 1.50, 0.50, 3.0, 1.00, "fao56"),
    ("Guava", "الجوافة", "Psidium guajava", "Fruit",
     90, 90, 120, 65, 0.50, 0.90, 0.80, 0.80, 1.50, 0.50, 3.0, 1.00, "fao56"),
    ("Papaya", "البابايا", "Carica papaya", "Fruit",
     90, 90, 120, 65, 0.50, 1.00, 0.90, 0.50, 1.00, 0.40, 2.5, 1.00, "fao56"),
    ("Dragon Fruit", "فاكهة التنين", "Hylocereus undatus", "Fruit",
     90, 90, 120, 65, 0.40, 0.70, 0.60, 0.30, 0.60, 0.50, 2.0, 1.00, "fao56"),

    # --- FAO-56 citrus (70% canopy, no ground cover; near-flat Kc) ----------
    ("Orange", "البرتقال", "Citrus sinensis", "Citrus",
     60, 90, 120, 95, 0.65, 0.60, 0.65, 1.20, 1.50, 0.50, 3.0, 1.00, "fao56"),
    ("Mandarin", "اليوسفي", "Citrus reticulata", "Citrus",
     60, 90, 120, 95, 0.65, 0.60, 0.65, 1.20, 1.50, 0.50, 3.0, 1.00, "fao56"),
    ("Lemon", "الليمون", "Citrus limon", "Citrus",
     60, 90, 120, 95, 0.65, 0.60, 0.65, 1.20, 1.50, 0.50, 3.0, 1.00, "fao56"),
    ("Lime", "اللايم", "Citrus aurantifolia", "Citrus",
     60, 90, 120, 95, 0.65, 0.60, 0.65, 1.20, 1.50, 0.50, 2.5, 1.00, "fao56"),
    ("Grapefruit", "الجريب فروت", "Citrus paradisi", "Citrus",
     60, 90, 120, 95, 0.65, 0.60, 0.65, 1.20, 1.50, 0.50, 3.0, 1.00, "fao56"),
    ("Pomelo", "البوملي", "Citrus maxima", "Citrus",
     60, 90, 120, 95, 0.65, 0.60, 0.65, 1.20, 1.50, 0.50, 3.5, 1.00, "fao56"),
    ("Clementine", "الكلمنتينا", "Citrus clementina", "Citrus",
     60, 90, 120, 95, 0.65, 0.60, 0.65, 1.20, 1.50, 0.50, 2.5, 1.00, "fao56"),
]

CROP_FIELDS = ["name_en", "name_ar", "scientific_name", "category",
               "l_ini", "l_dev", "l_mid", "l_late",
               "kc_ini", "kc_mid", "kc_end", "zr_min", "zr_max", "p",
               "height", "ky", "source"]


# --- Soil textures (FAO-56 Table 19; theta as volumetric fraction) ----------
# name_en, name_ar, theta_fc, theta_wp, bulk_density, infiltration_mm_hr
SOILS = [
    ("Sand", "رملية", 0.12, 0.05, 1.65, 50.0),
    ("Loamy Sand", "رملية طينية", 0.15, 0.07, 1.60, 35.0),
    ("Sandy Loam", "طميية رملية", 0.21, 0.09, 1.55, 25.0),
    ("Loam", "طميية", 0.31, 0.14, 1.40, 13.0),
    ("Silt Loam", "طميية غرينية", 0.33, 0.13, 1.35, 8.0),
    ("Silt", "غرينية", 0.34, 0.12, 1.35, 5.0),
    ("Sandy Clay Loam", "طميية رملية طينية", 0.32, 0.17, 1.45, 8.0),
    ("Clay Loam", "طميية طينية", 0.36, 0.18, 1.35, 5.0),
    ("Silty Clay Loam", "طميية غرينية طينية", 0.38, 0.19, 1.30, 3.0),
    ("Sandy Clay", "طينية رملية", 0.37, 0.20, 1.35, 3.0),
    ("Silty Clay", "طينية غرينية", 0.40, 0.20, 1.28, 2.0),
    ("Clay", "طينية", 0.44, 0.21, 1.25, 1.5),
]

SOIL_FIELDS = ["name_en", "name_ar", "theta_fc", "theta_wp",
               "bulk_density", "infiltration_mm_hr"]


# --- Irrigation systems (spec section 21; default efficiencies) -------------
# name_en, name_ar, default_efficiency_pct
SYSTEMS = [
    ("Drip Irrigation", "ري بالتنقيط", 90),
    ("Subsurface Drip (SDI)", "تنقيط تحت سطحي", 95),
    ("Sprinkler Irrigation", "ري بالرش", 75),
    ("Center Pivot", "محوري", 85),
    ("Linear Move", "خطي متحرك", 85),
    ("Micro Sprinkler", "رذاذ دقيق", 85),
    ("Bubbler Irrigation", "ري فقاعي", 80),
    ("Surface Irrigation", "ري سطحي", 60),
]

SYSTEM_FIELDS = ["name_en", "name_ar", "default_efficiency_pct"]


# --- Saudi Arabia cities (all 13 regions) ----------------------------------
# name_en, name_ar, region, latitude, longitude, elevation_m
CITIES = [
    # Riyadh Region
    ("Riyadh", "الرياض", "Riyadh", 24.7136, 46.6753, 612),
    ("Al Kharj", "الخرج", "Riyadh", 24.1554, 47.3346, 435),
    ("Al Majma'ah", "المجمعة", "Riyadh", 25.9038, 45.3450, 725),
    ("Az Zulfi", "الزلفي", "Riyadh", 26.2833, 44.8145, 600),
    ("Ad Dawadmi", "الدوادمي", "Riyadh", 24.5074, 44.3925, 970),
    ("Afif", "عفيف", "Riyadh", 23.9065, 42.9182, 1050),
    ("Al Quwayiyah", "القويعية", "Riyadh", 24.0720, 45.2760, 900),
    ("Wadi ad-Dawasir", "وادي الدواسر", "Riyadh", 20.4489, 44.7896, 700),
    ("As Sulayyil", "السليل", "Riyadh", 20.4607, 45.5680, 620),
    ("Hotat Bani Tamim", "حوطة بني تميم", "Riyadh", 23.5170, 46.8500, 540),
    ("Layla (Al Aflaj)", "ليلى (الأفلاج)", "Riyadh", 22.2833, 46.7400, 520),
    ("Shaqra", "شقراء", "Riyadh", 25.2445, 45.2520, 720),
    ("Huraymila", "حريملاء", "Riyadh", 25.1110, 46.1030, 700),
    ("Al Muzahimiyah", "المزاحمية", "Riyadh", 24.4700, 46.2700, 650),
    ("Marat", "مرات", "Riyadh", 25.0700, 45.4700, 850),
    ("Diriyah", "الدرعية", "Riyadh", 24.7370, 46.5750, 610),
    # Makkah Region
    ("Makkah", "مكة المكرمة", "Makkah", 21.3891, 39.8579, 277),
    ("Jeddah", "جدة", "Makkah", 21.5433, 39.1728, 12),
    ("Ta'if", "الطائف", "Makkah", 21.2703, 40.4158, 1879),
    ("Al Qunfudhah", "القنفذة", "Makkah", 19.1264, 41.0789, 10),
    ("Rabigh", "رابغ", "Makkah", 22.7986, 39.0349, 10),
    ("Al Lith", "الليث", "Makkah", 20.1500, 40.2667, 20),
    ("Khulais", "خليص", "Makkah", 22.1560, 39.3140, 180),
    ("Turbah", "تربة", "Makkah", 21.2130, 41.6290, 1100),
    ("Ranyah", "رنية", "Makkah", 21.2700, 42.8300, 960),
    ("Al Khurmah", "الخرمة", "Makkah", 21.9210, 42.0490, 980),
    # Madinah Region
    ("Madinah", "المدينة المنورة", "Madinah", 24.4686, 39.6142, 631),
    ("Yanbu", "ينبع", "Madinah", 24.0895, 38.0637, 7),
    ("Al Ula", "العلا", "Madinah", 26.6180, 37.9210, 679),
    ("Badr", "بدر", "Madinah", 23.7800, 38.7900, 120),
    ("Khaybar", "خيبر", "Madinah", 25.7000, 39.2900, 780),
    ("Mahd adh Dhahab", "مهد الذهب", "Madinah", 23.4900, 40.8600, 940),
    ("Al Henakiyah", "الحناكية", "Madinah", 24.8700, 40.5200, 720),
    # Eastern Province
    ("Dammam", "الدمام", "Eastern Province", 26.4207, 50.0888, 10),
    ("Al Khobar", "الخبر", "Eastern Province", 26.2794, 50.2083, 5),
    ("Dhahran", "الظهران", "Eastern Province", 26.2886, 50.1500, 17),
    ("Al Hofuf (Al Ahsa)", "الهفوف (الأحساء)", "Eastern Province", 25.3833, 49.5867, 150),
    ("Al Mubarraz", "المبرز", "Eastern Province", 25.4100, 49.5900, 155),
    ("Jubail", "الجبيل", "Eastern Province", 27.0046, 49.6461, 5),
    ("Qatif", "القطيف", "Eastern Province", 26.5650, 49.9960, 5),
    ("Hafr Al Batin", "حفر الباطن", "Eastern Province", 28.4342, 45.9636, 360),
    ("Al Khafji", "الخفجي", "Eastern Province", 28.4390, 48.4910, 5),
    ("Ras Tanura", "رأس تنورة", "Eastern Province", 26.7000, 50.1600, 5),
    ("Abqaiq", "بقيق", "Eastern Province", 25.9340, 49.6670, 120),
    ("An Nairyah", "النعيرية", "Eastern Province", 27.4800, 48.4800, 60),
    # Asir Region
    ("Abha", "أبها", "Asir", 18.2164, 42.5053, 2270),
    ("Khamis Mushait", "خميس مشيط", "Asir", 18.3060, 42.7290, 2000),
    ("Bisha", "بيشة", "Asir", 19.9980, 42.6070, 1160),
    ("Muhayil Asir", "محايل عسير", "Asir", 18.5500, 42.0500, 480),
    ("An Namas", "النماص", "Asir", 19.1500, 42.1200, 2500),
    ("Ahad Rafidah", "أحد رفيدة", "Asir", 18.2000, 42.8500, 2100),
    ("Tathleeth", "تثليث", "Asir", 19.5500, 43.5200, 1100),
    ("Dhahran Al Janub", "ظهران الجنوب", "Asir", 17.6600, 43.5100, 1550),
    ("Rijal Alma", "رجال ألمع", "Asir", 18.1900, 42.2800, 700),
    # Tabuk Region
    ("Tabuk", "تبوك", "Tabuk", 28.3835, 36.5662, 768),
    ("Duba", "ضباء", "Tabuk", 27.3500, 35.6900, 10),
    ("Haql", "حقل", "Tabuk", 29.2900, 34.9400, 10),
    ("Umluj", "أملج", "Tabuk", 25.0200, 37.2700, 10),
    ("Al Wajh", "الوجه", "Tabuk", 26.2400, 36.4600, 20),
    ("Tayma", "تيماء", "Tabuk", 27.6300, 38.5500, 830),
    # Hail Region
    ("Hail", "حائل", "Hail", 27.5219, 41.6907, 1000),
    ("Baqaa", "بقعاء", "Hail", 27.9800, 42.8700, 650),
    ("Ash Shamli", "الشملي", "Hail", 26.9000, 40.5500, 900),
    # Northern Borders
    ("Arar", "عرعر", "Northern Borders", 30.9753, 41.0381, 555),
    ("Rafha", "رفحاء", "Northern Borders", 29.6270, 43.4990, 445),
    ("Turaif", "طريف", "Northern Borders", 31.6725, 38.6637, 850),
    ("Al Uwayqilah", "العويقيلة", "Northern Borders", 30.3300, 42.2400, 470),
    # Jazan Region
    ("Jazan", "جازان", "Jazan", 16.8894, 42.5511, 5),
    ("Sabya", "صبيا", "Jazan", 17.1490, 42.6250, 40),
    ("Abu Arish", "أبو عريش", "Jazan", 16.9690, 42.8320, 50),
    ("Samtah", "صامطة", "Jazan", 16.5980, 42.9430, 20),
    ("Ahad al Masarihah", "أحد المسارحة", "Jazan", 16.7090, 42.9540, 25),
    ("Baish", "بيش", "Jazan", 17.3780, 42.5510, 50),
    ("Farasan", "فرسان", "Jazan", 16.7000, 42.1200, 5),
    ("Fifa", "فيفاء", "Jazan", 17.2600, 43.1000, 1500),
    # Najran Region
    ("Najran", "نجران", "Najran", 17.4917, 44.1277, 1290),
    ("Sharurah", "شرورة", "Najran", 17.4700, 47.1100, 725),
    ("Hubuna", "حبونا", "Najran", 17.7500, 44.1000, 1350),
    # Al Bahah Region
    ("Al Bahah", "الباحة", "Al Bahah", 20.0129, 41.4677, 2155),
    ("Baljurashi", "بلجرشي", "Al Bahah", 19.8600, 41.5700, 2100),
    ("Al Mandaq", "المندق", "Al Bahah", 20.1500, 41.2800, 2000),
    ("Al Mikhwah", "المخواة", "Al Bahah", 19.7900, 41.4400, 600),
    ("Qilwah", "قلوة", "Al Bahah", 19.9000, 41.6300, 700),
    ("Al Aqiq", "العقيق", "Al Bahah", 20.2700, 41.6500, 1800),
    # Al Jouf Region
    ("Sakaka", "سكاكا", "Al Jouf", 29.9697, 40.2064, 550),
    ("Al Qurayyat", "القريات", "Al Jouf", 31.3320, 37.3420, 530),
    ("Dumat Al Jandal", "دومة الجندل", "Al Jouf", 29.8120, 39.8670, 600),
    ("Tabarjal", "طبرجل", "Al Jouf", 30.5000, 38.2200, 700),
    # Qassim Region
    ("Buraydah", "بريدة", "Qassim", 26.3260, 43.9750, 600),
    ("Unayzah", "عنيزة", "Qassim", 26.0840, 43.9940, 650),
    ("Ar Rass", "الرس", "Qassim", 25.8670, 43.4970, 700),
    ("Al Mithnab", "المذنب", "Qassim", 25.8600, 44.2200, 680),
    ("Al Bukayriyah", "البكيرية", "Qassim", 26.1400, 43.6600, 630),
    ("Al Badai", "البدائع", "Qassim", 26.0200, 43.7700, 640),
    ("Riyadh Al Khabra", "رياض الخبراء", "Qassim", 26.5000, 43.5100, 620),
]

CITY_FIELDS = ["name_en", "name_ar", "region", "latitude", "longitude", "elevation"]
