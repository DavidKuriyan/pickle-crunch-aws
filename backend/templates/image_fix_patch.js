/**
 * ============================================================
 *  Pickle & Crunch — Product Image Fix Patch
 *  Drop this <script> block at the END of base.html (before </body>)
 *  OR include as a separate <script src="image_fix_patch.js">
 * ============================================================
 *
 *  HOW IT WORKS:
 *  After the product grid renders, this script scans every
 *  <img> inside .product-img and replaces broken / wrong images
 *  with the correct Unsplash URL matched by the product name
 *  shown in the same card.
 * ============================================================
 */

const PRODUCT_IMAGES = {
  /* ── NON-VEG PICKLES ─────────────────────────────────── */
  "Chicken Pickle":        "https://images.unsplash.com/photo-1604908176997-125f25cc6f3d?w=600",
  "Mutton Pickle":         "https://images.unsplash.com/photo-1574894709920-11b28e7367e3?w=600",
  "Fish Pickle":           "https://images.unsplash.com/photo-1519708227418-c8fd9a32b7a2?w=600",
  "Prawn Pickle":          "https://images.unsplash.com/photo-1565680018434-b513d5e5fd47?w=600",
  "Gongura Mutton":        "https://images.unsplash.com/photo-1574894709920-11b28e7367e3?w=600",
  "Rohu Fish Pickle":      "https://images.unsplash.com/photo-1485704686097-ed47f7263ca4?w=600",
  "Crab Pickle":           "https://images.unsplash.com/photo-1559737558-2f5a35f4523b?w=600",
  "Boneless Chicken Pickle":"https://images.unsplash.com/photo-1604908176997-125f25cc6f3d?w=600",

  /* ── VEG PICKLES ──────────────────────────────────────── */
  "Mango Pickle":          "https://images.unsplash.com/photo-1601493700631-2b16ec4b4716?w=600",
  "Lemon Pickle":          "https://images.unsplash.com/photo-1587486936739-78a3a6d4a176?w=600",
  "Tomato Pickle":         "https://images.unsplash.com/photo-1558818498-28c1e002b655?w=600",
  "Gongura Pickle":        "https://images.unsplash.com/photo-1512621776951-a57141f2eefd?w=600",
  "Mixed Veg Pickle":      "https://images.unsplash.com/photo-1567306226416-28f0efdc88ce?w=600",
  "Amla Pickle":           "https://images.unsplash.com/photo-1596591868231-05e808fd131d?w=600",
  "Green Chilli Pickle":   "https://images.unsplash.com/photo-1583119022894-919a68a3d0e3?w=600",
  "Garlic Pickle":         "https://images.unsplash.com/photo-1615485290382-441e4d049cb5?w=600",
  "Ginger Pickle":         "https://images.unsplash.com/photo-1615485290382-441e4d049cb5?w=600",
  "Tamarind Pickle":       "https://images.unsplash.com/photo-1601493700631-2b16ec4b4716?w=600",

  /* ── SNACKS ───────────────────────────────────────────── */
  "Banana Chips":          "https://images.unsplash.com/photo-1621447504864-d8686e12698c?w=600",
  "Crispy Aam-Papad":      "https://images.unsplash.com/photo-1568702846914-96b305d2aaeb?w=600",
  "Crispy Chekka Pakodi":  "https://images.unsplash.com/photo-1606923829579-0cb981a83e2e?w=600",
  "Boondhi Acchu":         "https://images.unsplash.com/photo-1606923829579-0cb981a83e2e?w=600",
  "Chekkalu":              "https://images.unsplash.com/photo-1558961363-fa8fdf82db35?w=600",
  "Ragi Laddu":            "https://images.unsplash.com/photo-1601050690597-df0568f70950?w=600",
  "Dry Fruit Laddu":       "https://images.unsplash.com/photo-1601050690597-df0568f70950?w=600",
  "Kara Boondi":           "https://images.unsplash.com/photo-1606923829579-0cb981a83e2e?w=600",
  "Murukku":               "https://images.unsplash.com/photo-1558961363-fa8fdf82db35?w=600",
  "Chakli":                "https://images.unsplash.com/photo-1558961363-fa8fdf82db35?w=600",
  "Groundnut Chikki":      "https://images.unsplash.com/photo-1559622214-f8a9850965bb?w=600",
  "Sesame Chikki":         "https://images.unsplash.com/photo-1559622214-f8a9850965bb?w=600",
  "Coconut Laddu":         "https://images.unsplash.com/photo-1601050690597-df0568f70950?w=600",
  "Besan Laddu":           "https://images.unsplash.com/photo-1601050690597-df0568f70950?w=600",
  "Ribbon Pakoda":         "https://images.unsplash.com/photo-1606923829579-0cb981a83e2e?w=600",
  "Aloo Bhujia":           "https://images.unsplash.com/photo-1558961363-fa8fdf82db35?w=600",
  "Mixture":               "https://images.unsplash.com/photo-1558961363-fa8fdf82db35?w=600",
  "Thattai":               "https://images.unsplash.com/photo-1606923829579-0cb981a83e2e?w=600",
};

/**
 * Fallback images by category (used when product name not found above)
 */
const CATEGORY_FALLBACKS = {
  "non_veg_pickles": "https://images.unsplash.com/photo-1604908176997-125f25cc6f3d?w=600",
  "veg_pickles":     "https://images.unsplash.com/photo-1601493700631-2b16ec4b4716?w=600",
  "snacks":          "https://images.unsplash.com/photo-1558961363-fa8fdf82db35?w=600",
  "pickles":         "https://images.unsplash.com/photo-1601493700631-2b16ec4b4716?w=600",
};

/**
 * Fix all product card images on the page.
 * Runs once immediately and then watches for dynamically added cards.
 */
function fixProductImages() {
  document.querySelectorAll('.product-card').forEach(card => {
    const img     = card.querySelector('.product-img img');
    const nameEl  = card.querySelector('.product-name');
    const catEl   = card.querySelector('.product-cat');
    if (!img || !nameEl) return;

    const name    = nameEl.textContent.trim();
    const cat     = (catEl ? catEl.textContent.trim().toLowerCase().replace(/\s+/g,'_') : '');

    // Check if current src is the same broken placeholder image
    const BROKEN_PLACEHOLDER = "avocado"; // keyword from the broken Unsplash avocado-toast image
    const isBroken = img.src.includes(BROKEN_PLACEHOLDER) ||
                     img.src.includes("photo-1588137378633") || // the exact broken URL
                     img.naturalWidth === 0;

    if (!isBroken && img.src && !img.src.includes('unsplash.com/photo-1588137378633')) return;

    // Try exact name match first
    const correctUrl = PRODUCT_IMAGES[name]
      || PRODUCT_IMAGES[Object.keys(PRODUCT_IMAGES).find(k => name.toLowerCase().includes(k.toLowerCase()))]
      || CATEGORY_FALLBACKS[cat]
      || CATEGORY_FALLBACKS['pickles'];

    if (correctUrl) {
      img.src = correctUrl;
    }
  });
}

/**
 * Also patch the product data returned from the API before rendering.
 * Override the global renderProducts / addToSession functions to inject
 * correct images at data level so cart images are also correct.
 */
function patchProductData(products) {
  return products.map(p => {
    const name = p.name || '';
    const cat  = (p.category || '').toLowerCase();

    const correctUrl = PRODUCT_IMAGES[name]
      || PRODUCT_IMAGES[Object.keys(PRODUCT_IMAGES).find(k => name.toLowerCase().includes(k.toLowerCase()))]
      || CATEGORY_FALLBACKS[cat]
      || p.img; // keep original as last resort

    return { ...p, img: correctUrl };
  });
}

// ── Intercept renderProducts (used in index.html) ─────────────────────────
if (typeof renderProducts !== 'undefined') {
  const _origRender = renderProducts;
  window.renderProducts = function(products) {
    _origRender(patchProductData(products));
  };
}

// ── Intercept loadProducts to patch data before render ────────────────────
if (typeof loadProducts !== 'undefined') {
  const _origLoad = loadProducts;
  window.loadProducts = async function(category) {
    await _origLoad(category);
    setTimeout(fixProductImages, 100);
  };
}

// ── MutationObserver: fix images whenever new cards are added to the DOM ──
const observer = new MutationObserver(() => fixProductImages());
observer.observe(document.body, { childList: true, subtree: true });

// ── Run immediately on page load ──────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  fixProductImages();
  setTimeout(fixProductImages, 500);  // catch lazy-loaded cards
  setTimeout(fixProductImages, 1500); // final catch
});
