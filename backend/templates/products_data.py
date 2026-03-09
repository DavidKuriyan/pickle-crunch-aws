"""
================================================================
  Pickle & Crunch — Corrected Product Image URLs
  Replace or merge this into your Flask app.py product data /
  DynamoDB seed script.
================================================================
"""

PRODUCTS = [

    # ── NON-VEG PICKLES ──────────────────────────────────────────
    {
        "ProductID": "NV001", "category": "non_veg_pickles",
        "name": "Chicken Pickle",
        "desc": "Tender chicken slow-cooked with red chilli, sesame and mustard oil.",
        "img":  "https://images.unsplash.com/photo-1604908176997-125f25cc6f3d?w=600",
        "tag":  "Bestseller",
        "weights": {"250": 280, "500": 520, "1000": 980},
        "rating": 4.8,
    },
    {
        "ProductID": "NV002", "category": "non_veg_pickles",
        "name": "Mutton Pickle",
        "desc": "Succulent mutton pieces marinated in Andhra-style spice blend.",
        "img":  "https://images.unsplash.com/photo-1574894709920-11b28e7367e3?w=600",
        "tag":  "Spicy",
        "weights": {"250": 320, "500": 600, "1000": 1100},
        "rating": 4.7,
    },
    {
        "ProductID": "NV003", "category": "non_veg_pickles",
        "name": "Gongura Mutton",
        "desc": "Classic sorrel-leaf mutton pickle — tangy, spicy, irresistible.",
        "img":  "https://images.unsplash.com/photo-1574894709920-11b28e7367e3?w=600",
        "tag":  "Premium",
        "weights": {"250": 350, "500": 650},
        "rating": 4.9,
    },
    {
        "ProductID": "NV004", "category": "non_veg_pickles",
        "name": "Fish Pickle",
        "desc": "Coastal-style fish pickle with raw mango and kokum.",
        "img":  "https://images.unsplash.com/photo-1519708227418-c8fd9a32b7a2?w=600",
        "tag":  "Coastal",
        "weights": {"250": 260, "500": 490},
        "rating": 4.6,
    },
    {
        "ProductID": "VP002",
        "category": "veg_pickles",
        "name": "Lemon Pickle",
        "desc": "Sun-soaked lemons with spices — bright, tangy and digestive.",
        "img": "Lemon Pickle": "/static/images/lime-pickle-hero_jpg.jpeg",
        "tag": "Tangy",
        "weights": {"250": 110, "500": 200},
        "rating": 4.6
   },
    {
        "ProductID": "NV005", "category": "non_veg_pickles",
        "name": "Prawn Pickle",
        "desc": "Sun-dried prawns tossed in mustard seeds, curry leaves and red chilli.",
        "img":  "https://images.unsplash.com/photo-1565680018434-b513d5e5fd47?w=600",
        "tag":  "Coastal",
        "weights": {"250": 300, "500": 560},
        "rating": 4.5,
    },

    # ── VEG PICKLES ───────────────────────────────────────────────
    {
        "ProductID": "VP001", "category": "veg_pickles",
        "name": "Mango Pickle",
        "desc": "Raw mango chunks tempered with mustard, fenugreek and chilli powder.",
        "img":  "https://images.unsplash.com/photo-1601493700631-2b16ec4b4716?w=600",
        "tag":  "Classic",
        "weights": {"250": 120, "500": 220, "1000": 400},
        "rating": 4.8,
    },
   {
        "ProductID": "VP002",
        "category": "veg_pickles",
        "name": "Lemon Pickle",
        "desc": "Sun-soaked lemons with spices — bright, tangy and digestive.",
        "img": "https://images.unsplash.com/photo-1601493700631-2b16ec4b4716?w=600",
        "tag": "Tangy",
        "weights": {"250": 110, "500": 200},
        "rating": 4.6
    },
    {
        "ProductID": "VP003", "category": "veg_pickles",
        "name": "Tomato Pickle",
        "desc": "Slow-cooked tomato relish with garlic and tamarind.",
        "img":  "https://images.unsplash.com/photo-1558818498-28c1e002b655?w=600",
        "tag":  "Fresh",
        "weights": {"250": 130, "500": 240},
        "rating": 4.5,
    },
    {
        "ProductID": "VP004", "category": "veg_pickles",
        "name": "Gongura Pickle",
        "desc": "Pure sorrel-leaf pickle — the soul of Andhra cuisine.",
        "img":  "https://images.unsplash.com/photo-1512621776951-a57141f2eefd?w=600",
        "tag":  "Andhra",
        "weights": {"250": 140, "500": 260},
        "rating": 4.7,
    },
    {
        "ProductID": "VP005", "category": "veg_pickles",
        "name": "Green Chilli Pickle",
        "desc": "Whole green chillies preserved in spiced mustard oil.",
        "img":  "https://images.unsplash.com/photo-1583119022894-919a68a3d0e3?w=600",
        "tag":  "Hot",
        "weights": {"250": 100, "500": 185},
        "rating": 4.4,
    },
    {
        "ProductID": "VP006", "category": "veg_pickles",
        "name": "Garlic Pickle",
        "desc": "Peeled garlic cloves in tangy tamarind and red chilli base.",
        "img":  "https://images.unsplash.com/photo-1615485290382-441e4d049cb5?w=600",
        "tag":  "Aromatic",
        "weights": {"250": 160, "500": 300},
        "rating": 4.6,
    },

    # ── SNACKS ────────────────────────────────────────────────────
    {
        "ProductID": "SN001", "category": "snacks",
        "name": "Banana Chips",
        "desc": "Thin-sliced raw banana chips fried to golden perfection.",
        "img":  "https://images.unsplash.com/photo-1621447504864-d8686e12698c?w=600",
        "tag":  "Popular",
        "weights": {"250": 300, "500": 560},
        "rating": 4.6,
    },
    {
        "ProductID": "SN002", "category": "snacks",
        "name": "Crispy Aam-Papad",
        "desc": "Sun-dried mango leather — sweet, tangy and chewy.",
        "img":  "https://images.unsplash.com/photo-1568702846914-96b305d2aaeb?w=600",
        "tag":  "Healthy",
        "weights": {"250": 150},
        "rating": 4.5,
    },
    {
        "ProductID": "SN003", "category": "snacks",
        "name": "Chekkalu",
        "desc": "Traditional rice crackers with cumin and green chilli.",
        "img":  "https://images.unsplash.com/photo-1558961363-fa8fdf82db35?w=600",
        "tag":  "Popular",
        "weights": {"250": 180, "500": 340},
        "rating": 4.7,
    },
    {
        "ProductID": "SN004", "category": "snacks",
        "name": "Dry Fruit Laddu",
        "desc": "Energy-packed laddus with dates, nuts and jaggery.",
        "img":  "https://images.unsplash.com/photo-1601050690597-df0568f70950?w=600",
        "tag":  "Premium",
        "weights": {"250": 380, "500": 720},
        "rating": 4.8,
    },
    {
        "ProductID": "SN005", "category": "snacks",
        "name": "Ragi Laddu",
        "desc": "Finger-millet laddus sweetened with jaggery — guilt-free snacking.",
        "img":  "https://images.unsplash.com/photo-1601050690597-df0568f70950?w=600",
        "tag":  "Healthy",
        "weights": {"250": 280, "500": 530},
        "rating": 4.5,
    },
    {
        "ProductID": "SN006", "category": "snacks",
        "name": "Kara Boondi",
        "desc": "Savoury gram-flour boondi with spiced seasoning.",
        "img":  "https://images.unsplash.com/photo-1606923829579-0cb981a83e2e?w=600",
        "tag":  "Spicy",
        "weights": {"250": 300, "500": 560},
        "rating": 4.5,
    },
    {
        "ProductID": "SN007", "category": "snacks",
        "name": "Murukku",
        "desc": "Classic spiral rice-flour crunchies with sesame and ajwain.",
        "img":  "https://images.unsplash.com/photo-1558961363-fa8fdf82db35?w=600",
        "tag":  "Classic",
        "weights": {"250": 220, "500": 420},
        "rating": 4.6,
    },
    {
        "ProductID": "SN008", "category": "snacks",
        "name": "Groundnut Chikki",
        "desc": "Crunchy peanut brittle made with pure jaggery.",
        "img":  "https://images.unsplash.com/photo-1559622214-f8a9850965bb?w=600",
        "tag":  "Sweet",
        "weights": {"250": 160, "500": 300},
        "rating": 4.4,
    },
]

# ── Helper: get products by category ────────────────────────────────────────
def get_products(category=None):
    if category and category != "all":
        return [p for p in PRODUCTS if p["category"] == category]
    return PRODUCTS

# ── Helper: get single product by ID ────────────────────────────────────────
def get_product_by_id(product_id):
    return next((p for p in PRODUCTS if p["ProductID"] == product_id), None)
