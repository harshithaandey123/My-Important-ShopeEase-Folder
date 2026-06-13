"""
Product catalog for ShopEase Copilot
Includes multilingual product information (English, Telugu, Hindi)
"""

PRODUCTS = [
    {
        "id": 1,
        "name": "Noise Buds VS102",
        "name_te": "నాయిజ్ బడ్‌స్ VS102",
        "name_hi": "नॉइज़ बड्स VS102",
        "brand": "Noise",
        "price": 1299,
        "rating": 4.2,
        "reviews": 124,
        "description": "Lightweight earbuds with immersive sound quality and excellent battery life.",
        "description_te": "తెలిసిన శబ్ద నిర్ణయం కలిగిన తేలికైన ఇయర్‌బడ్‌లు.",
        "description_hi": "हल्के ईयरबड्स जिसमें शानदार ध्वनि गुणवत्ता है।",
    },
    {
        "id": 2,
        "name": "boAt Airdopes 141",
        "name_te": "బోట్ ఎయిర్‌డోప్‌లు 141",
        "name_hi": "बोट एयरडोप्स 141",
        "brand": "boAt",
        "price": 999,
        "rating": 4.0,
        "reviews": 98,
        "description": "Affordable true wireless earbuds with punchy bass and long playback.",
        "description_te": "చవకైన ట్రూ వైర్‌లెస్ ఇయర్‌బడ్‌లు శక్తివంతమైన బాసుతో.",
        "description_hi": "सस्ते ट्रू वायरलेस ईयरबड्स शक्तिशाली बास के साथ।",
    },
    {
        "id": 3,
        "name": "Realme Buds T300",
        "name_te": "రియల్‌మీ బడ్‌స్ T300",
        "name_hi": "रियलमी बड्स T300",
        "brand": "Realme",
        "price": 1499,
        "rating": 4.3,
        "reviews": 76,
        "description": "Comfortable fit with long battery life and active noise cancellation.",
        "description_te": "సుఖవంతమైన ఫిట్ సుదీర్ఘ ఆయువు కలిగిన ఇయర్‌బడ్‌లు.",
        "description_hi": "आरामदायक फिट लंबी बैटरी लाइफ के साथ।",
    },
    {
        "id": 4,
        "name": "OnePlus Nord Buds 2r",
        "name_te": "వన్‌ప్లస్ నార్డ్ బడ్‌స్ 2r",
        "name_hi": "वनप्लस नॉर्ड बड्स 2r",
        "brand": "OnePlus",
        "price": 2299,
        "rating": 4.4,
        "reviews": 210,
        "description": "Balanced sound profile with low latency mode and premium build.",
        "description_te": "సమతుల్య ధ్వని ప్రొఫైల్ తక్కువ జిల్లీ మోడ్ కలిగిన ఉన్నత నిర్మాణ ఇయర్‌బడ్‌లు.",
        "description_hi": "संतुलित ध्वनि प्रोफाइल कम विलंबता मोड के साथ।",
    },
    {
        "id": 5,
        "name": "Samsung Galaxy Buds FE",
        "name_te": "శామ్‌సంగ్ గాలక్సీ బడ్‌స్ FE",
        "name_hi": "सैमसंग गैलेक्सी बड्स FE",
        "brand": "Samsung",
        "price": 3499,
        "rating": 4.1,
        "reviews": 65,
        "description": "Reliable everyday earbuds from Samsung with great connectivity.",
        "description_te": "సैమ్‌సంగ్ నుండి విశ్వసనీయ రోజువారీ ఇయర్‌బడ్‌లు గొప్ప కనెక్టివిటీ కలిగిన.",
        "description_hi": "सैमसंग से विश्वसनीय रोज़मर्रा के ईयरबड्स।",
    },
]


def get_product_by_id(product_id: int) -> dict | None:
    """Get product by ID."""
    for product in PRODUCTS:
        if product["id"] == product_id:
            return product
    return None


def get_product_by_name(name: str) -> dict | None:
    """Get product by name (case-insensitive)."""
    name_lower = name.lower()
    for product in PRODUCTS:
        if name_lower in product["name"].lower() or name_lower in product["brand"].lower():
            return product
    return None


def get_top_products(limit: int = 3) -> list:
    """Get top products sorted by rating."""
    return sorted(PRODUCTS, key=lambda x: x["rating"], reverse=True)[:limit]
