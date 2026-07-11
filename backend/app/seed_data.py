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
