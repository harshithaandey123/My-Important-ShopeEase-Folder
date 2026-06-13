from __future__ import annotations

import re
from difflib import SequenceMatcher, get_close_matches
from functools import lru_cache
from pathlib import Path


ASSET_DIR = Path(__file__).parent / "assets"


def _slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", value.lower()).strip("_")


def normalize_text(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", value.lower())


def _product(
    product_id: int,
    name: str,
    brand: str,
    category: str,
    price: int,
    rating: float,
    description: str,
    accent: str,
    tags: list[str] | None = None,
) -> dict:
    asset_path = ASSET_DIR / f"{_slug(name)}.svg"
    image = str(asset_path) if asset_path.exists() else make_product_svg(name, brand, accent)
    return {
        "id": product_id,
        "name": name,
        "brand": brand,
        "category": category,
        "price": price,
        "rating": rating,
        "description": description,
        "image": image,
        "tags": tags or [],
        "accent": accent,
    }


@lru_cache(maxsize=1)
def get_products() -> tuple[dict, ...]:
    products = [
        _product(1, "OnePlus Nord Buds 2r", "OnePlus", "earbuds", 2299, 4.6, "Bass-forward earbuds with low-latency gaming mode and fast charging.", "#0f766e", ["one plus buds", "nord buds"]),
        _product(2, "Realme Buds T300", "Realme", "earbuds", 1499, 4.5, "ANC earbuds with 12.4 mm drivers, clear calls, and long playback.", "#f59e0b", ["real me buds"]),
        _product(3, "Noise Buds VS102", "Noise", "earbuds", 1299, 4.4, "Lightweight everyday earbuds with crisp sound and dependable battery life.", "#7c3aed", ["noise buds vs 102", "noise buds"]),
        _product(4, "boAt Airdopes 141", "boAt", "earbuds", 999, 4.2, "Affordable true wireless earbuds with punchy bass and compact case.", "#dc2626", ["boat air dopes", "airdopes"]),
        _product(5, "Sony WF-C500", "Sony", "earbuds", 4490, 4.3, "Compact earbuds with detailed sound tuning and a secure, comfortable fit.", "#2563eb", ["sony earbuds"]),
        _product(6, "Samsung Galaxy Buds FE", "Samsung", "earbuds", 3499, 4.1, "Reliable Samsung earbuds with ergonomic wing-tip fit and easy pairing.", "#1f2937", ["galaxy buds"]),
        _product(7, "JBL Wave Beam", "JBL", "earbuds", 2999, 4.0, "Water-resistant earbuds with JBL Deep Bass and a pocketable case.", "#ea580c", ["jbl buds"]),
        _product(8, "Boult Z40 Pro", "Boult", "earbuds", 1199, 4.1, "Value earbuds with low latency mode, clear calling, and marathon battery.", "#0891b2", ["boult earbuds"]),
        _product(9, "CMF Buds Pro 2", "CMF", "earbuds", 4299, 4.6, "Dual-driver earbuds with smart dial case controls and rich ANC.", "#f97316", ["nothing buds", "cmf buds"]),
        _product(10, "Oppo Enco Buds 2", "Oppo", "earbuds", 1799, 4.2, "Balanced earbuds with Dolby tuning, lightweight shells, and quick controls.", "#16a34a", ["oppo buds"]),
        _product(11, "boAt Rockerz 450", "boAt", "headphones", 1499, 4.1, "Wireless on-ear headphones with plush cups and energetic bass.", "#be123c", ["boat headphones"]),
        _product(12, "Sony WH-CH520", "Sony", "headphones", 4490, 4.5, "Lightweight wireless headphones with long battery life and app EQ.", "#0284c7", ["sony headphones"]),
        _product(13, "JBL Tune 510BT", "JBL", "headphones", 3499, 4.3, "Foldable headphones with JBL Pure Bass and multipoint Bluetooth.", "#d97706", ["jbl headphones"]),
        _product(14, "Anker Soundcore Q20i", "Soundcore", "headphones", 4999, 4.4, "Hybrid ANC headphones with app presets and travel-ready battery life.", "#4338ca", ["anker headphones"]),
        _product(15, "Fire-Boltt Ninja Call Pro", "Fire-Boltt", "smartwatch", 1499, 4.0, "Bluetooth calling smartwatch with health tracking and bright display.", "#b91c1c", ["fire boltt watch"]),
        _product(16, "Noise ColorFit Pulse 4", "Noise", "smartwatch", 2499, 4.2, "Large display smartwatch with fitness modes and quick health insights.", "#9333ea", ["noise watch"]),
        _product(17, "Amazfit Bip 5", "Amazfit", "smartwatch", 6499, 4.4, "GPS smartwatch with Alexa support, long battery, and polished tracking.", "#0d9488", ["amazfit watch"]),
        _product(18, "Redmi Watch 3 Active", "Redmi", "smartwatch", 2999, 4.1, "Everyday smartwatch with calling, sleep tracking, and a lightweight body.", "#db2777", ["redmi watch"]),
        _product(19, "Mi Power Bank 20000mAh", "Xiaomi", "power bank", 2199, 4.4, "High-capacity power bank with 18W fast charging and dual USB output.", "#64748b", ["mi powerbank", "power bank"]),
        _product(20, "Anker PowerCore 10000", "Anker", "power bank", 2999, 4.5, "Compact premium power bank with reliable charging and travel-friendly size.", "#334155", ["anker power bank"]),
    ]
    return tuple(products)


def make_product_svg(name: str, brand: str, accent: str) -> str:
    title = name.replace("&", "and")
    initials = "".join(word[0] for word in brand.split()[:2]).upper()
    return f"""
    <svg xmlns='http://www.w3.org/2000/svg' width='640' height='420' viewBox='0 0 640 420'>
      <rect width='640' height='420' rx='28' fill='#f8fafc'/>
      <rect x='36' y='36' width='568' height='348' rx='26' fill='{accent}' opacity='0.14'/>
      <circle cx='320' cy='182' r='88' fill='{accent}' opacity='0.92'/>
      <circle cx='278' cy='184' r='18' fill='#ffffff' opacity='0.9'/>
      <circle cx='362' cy='184' r='18' fill='#ffffff' opacity='0.9'/>
      <rect x='254' y='244' width='132' height='34' rx='17' fill='#ffffff' opacity='0.9'/>
      <text x='320' y='190' text-anchor='middle' font-family='Arial, sans-serif' font-size='40' font-weight='700' fill='#ffffff'>{initials}</text>
      <text x='320' y='332' text-anchor='middle' font-family='Arial, sans-serif' font-size='26' font-weight='700' fill='#111827'>{title}</text>
    </svg>
    """


def find_product(query: str, products: list[dict] | tuple[dict, ...] | None = None) -> dict | None:
    products = products or get_products()
    query_norm = normalize_text(query)
    if not query_norm:
        return None

    candidates: list[tuple[float, dict]] = []
    for product in products:
        names = [product["name"], product["brand"], *product.get("tags", [])]
        best = 0.0
        for name in names:
            norm_name = normalize_text(name)
            if not norm_name:
                continue
            if norm_name in query_norm or query_norm in norm_name:
                best = max(best, 1.0)
            else:
                best = max(best, SequenceMatcher(None, query_norm, norm_name).ratio())
        candidates.append((best, product))

    candidates.sort(key=lambda item: item[0], reverse=True)
    return candidates[0][1] if candidates and candidates[0][0] >= 0.58 else None


def category_from_text(text: str) -> str | None:
    category_aliases = {
        "earbuds": ["earbud", "earbuds", "buds", "airdopes", "tws", "wireless earphone"],
        "headphones": ["headphone", "headphones", "headset"],
        "smartwatch": ["watch", "smartwatch", "smart watch"],
        "power bank": ["power bank", "powerbank", "charger"],
    }
    cleaned = text.lower()
    for category, aliases in category_aliases.items():
        if any(alias in cleaned for alias in aliases):
            return category

    close = get_close_matches(cleaned, category_aliases.keys(), n=1, cutoff=0.72)
    return close[0] if close else None


def recommend_products(
    products: list[dict] | tuple[dict, ...],
    category: str | None = None,
    limit: int = 3,
    max_price: int | None = None,
) -> list[dict]:
    filtered = list(products)
    if category:
        filtered = [product for product in filtered if product["category"] == category]
    if max_price is not None:
        filtered = [product for product in filtered if product["price"] <= max_price]
    return sorted(filtered, key=lambda product: (product["rating"], -product["price"]), reverse=True)[:limit]


def product_line(product: dict) -> str:
    return f"{product['name']} by {product['brand']} - Rs. {product['price']:,}, rated {product['rating']:.1f}"
