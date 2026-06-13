import hashlib
import html
import json
import os
import re
from typing import Any, Dict, List, Optional, Set
from urllib.parse import quote_plus

import requests
from dotenv import load_dotenv
load_dotenv()

import streamlit as st

from utils.recommendation import recommend_products

APP_TITLE = "ShopEase Copilot"
IMAGE_API_BASE = "https://image.pollinations.ai/prompt"
IMAGE_CACHE_FILENAME = "generated_image_cache.json"

ADD_KEYWORDS = {
    "add",
    "please add",
    "add to cart",
    "add to card",
    "put",
    "put in cart",
    "put in card",
    "జోడించు",
    "జోడించండి",
    "చేర్చు",
    "కార్ట్‌లో జోడించు",
    "కార్ట్ లో జోడించు",
    "కార్ట్‌కి జోడించు",
    "add karo",
    "जोड़ो",
    "जोड़ दें",
    "कार्ट में डालो",
    "कार्ट में जोड़ो",
    "डालो",
}
REMOVE_KEYWORDS = {
    "remove",
    "delete",
    "remove from cart",
    "తీసివేయి",
    "తీసేయి",
    "हटा",
    "निकालो",
    "हटाओ",
    "कार्ट से हटाओ",
}
SHOW_CART_KEYWORDS = {
    "show cart",
    "view cart",
    "cart status",
    "cart contents",
    "show my cart",
    "కార్ట్",
    "कार्ट",
    "చూపించు",
    "दिखाओ",
}
CHECKOUT_KEYWORDS = {
    "checkout",
    "place order",
    "buy now",
    "purchase",
    "pay now",
    "order చేయి",
    "ऑर्डर",
}
DETAIL_KEYWORDS = {
    "detail",
    "details",
    "cheppu",
    "cheppandi",
    "bataye",
    "batao",
    "vivaralu",
    "వివరాలు",
    "विवरण",
}
COMPARE_KEYWORDS = {
    "compare",
    "which one",
    "better",
    "versus",
    "vs",
    "ఎక్కువ మంచిది",
    "कौन सा",
}

CATEGORY_TOKENS = {
    "earbuds": "Earbuds",
    "earbud": "Earbuds",
    "earphones": "Earbuds",
    "earpods": "Earbuds",
    "buds": "Earbuds",
    "ఇయర్": "Earbuds",
    "ఈయర్": "Earbuds",
    "బడ్స్": "Earbuds",
    "बड्स": "Earbuds",
    "ईयर": "Earbuds",
    "headphones": "Headphones",
    "headphone": "Headphones",
    "headset": "Headphones",
    "హెడ్‌ఫోన్": "Headphones",
    "హెడ్‌ఫోన్లు": "Headphones",
    "వాచ్": "Smartwatches",
    "స్మార్ట్‌వాచ్": "Smartwatches",
    "స్మార్ట్ వాచ్": "Smartwatches",
    "స్మార్ట్ వాచెస్": "Smartwatches",
    "స్మార్ట్‌వాచెస్": "Smartwatches",
    "watch": "Smartwatches",
    "smartwatch": "Smartwatches",
    "smartwatches": "Smartwatches",
    "स्मार्टवॉच": "Smartwatches",
    "स्मार्ट वॉच": "Smartwatches",
    "ఫోన్": "Smartphones",
    "స్మార్ట్‌ఫోన్": "Smartphones",
    "phone": "Smartphones",
    "smartphone": "Smartphones",
    "smartphones": "Smartphones",
    "फोन": "Smartphones",
    "स्मार्टफोन": "Smartphones",
}

ORDINAL_TOKENS = {
    "first": 0,
    "second": 1,
    "third": 2,
    "fourth": 3,
    "1": 0,
    "2": 1,
    "3": 2,
    "4": 3,
    "1st": 0,
    "2nd": 1,
    "3rd": 2,
    "4th": 3,
    "one": 0,
    "two": 1,
    "three": 2,
    "four": 3,
    "రెండవ": 1,
    "రెండో": 1,
    "రెండవది": 1,
    "రెండోది": 1,
    "మొదటి": 0,
    "మొదటిది": 0,
    "మూడవ": 2,
    "మూడో": 2,
    "మూడోది": 2,
    "पहला": 0,
    "पहले": 0,
    "दूसरा": 1,
    "दूसरे": 1,
    "दूसरी": 1,
    "तीसरा": 2,
    "तीसरे": 2,
    "चौथा": 3,
}

SUPPORTED_VOICE_LANGUAGES = {"en-IN", "te-IN", "hi-IN"}
VOICE_LANGUAGE_FALLBACK_ORDER = ["en-IN", "te-IN", "hi-IN"]
VOICE_LANGUAGE_NAMES = {
    "en-IN": "English",
    "te-IN": "Telugu",
    "hi-IN": "Hindi",
}
VOICE_STATUS_LABELS = {
    "listening": "🎤 Listening",
    "processing": "🧠 Processing",
    "speaking": "🔊 Speaking",
    "ready": "✅ Ready for next command",
}


def render_page_style() -> None:
    st.markdown(
        """
        <style>
        :root {
            color-scheme: light;
            font-family: Inter, sans-serif;
        }

        .block-container {
            padding: 1.5rem 2rem 2rem 2rem;
            max-width: 1500px;
            margin: 0 auto;
        }

        .page-title {
            color: #232F3E;
            font-size: 3rem;
            font-weight: 800;
            margin-bottom: 0.2rem;
        }

        .page-subtitle {
            color: #4B5563;
            font-size: 1rem;
            margin-top: 0;
            margin-bottom: 1.75rem;
        }

        .search-header {
            display: flex;
            flex-wrap: wrap;
            gap: 1rem;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 1.5rem;
        }

        .search-header h2 {
            margin: 0;
            color: #232F3E;
        }

        .search-input input {
            border-radius: 999px !important;
            border: 2px solid #E5E7EB !important;
            padding: 0.95rem 1.2rem !important;
            box-shadow: inset 0 8px 20px rgba(35, 47, 62, 0.08) !important;
            background: white !important;
            font-size: 1rem !important;
            width: 100% !important;
        }

        .search-input input:focus {
            border-color: #FF9900 !important;
            box-shadow: 0 0 0 4px rgba(255, 153, 0, 0.15) !important;
        }

        .hero-card {
            background: #fff;
            border-radius: 24px;
            padding: 1.5rem 1.75rem;
            box-shadow: 0 24px 60px rgba(35, 47, 62, 0.08);
            margin-bottom: 1.75rem;
        }

        .hero-pill {
            display: inline-block;
            background: #FF9900;
            color: white;
            border-radius: 999px;
            padding: 0.35rem 0.85rem;
            font-size: 0.85rem;
            font-weight: 700;
            margin-bottom: 1rem;
        }

        .shop-card {
            background: white;
            border-radius: 22px;
            padding: 0.85rem;
            overflow: hidden;
            transition: transform 0.25s ease, box-shadow 0.25s ease;
            box-shadow: 0 14px 35px rgba(35, 47, 62, 0.08);
            min-height: 100%;
        }

        .shop-card:hover {
            transform: translateY(-6px);
            box-shadow: 0 28px 50px rgba(35, 47, 62, 0.12);
        }

        .product-image {
            border-radius: 18px;
            width: 100%;
            height: 240px;
            object-fit: cover;
            margin-bottom: 1rem;
        }

        .product-title {
            font-size: 1.05rem;
            font-weight: 700;
            color: #232F3E;
            margin-bottom: 0.35rem;
        }

        .product-meta {
            font-size: 0.92rem;
            color: #6B7280;
            margin-bottom: 0.8rem;
            line-height: 1.5;
        }

        .product-price {
            color: #FF9900;
            font-size: 1.15rem;
            font-weight: 700;
            margin-bottom: 0.75rem;
        }

        .add-button {
            background: #FF9900;
            color: white;
            border: none;
            border-radius: 14px;
            width: 100%;
            padding: 0.95rem 1rem;
            font-weight: 700;
            cursor: pointer;
            transition: background 0.2s ease;
        }

        .add-button:hover {
            background: #e88c00;
        }

        .stSidebar .sidebar-content {
            padding-top: 1rem;
        }

        .sidebar-card {
            background: #ffffff;
            border-radius: 22px;
            padding: 1rem 1.1rem;
            box-shadow: 0 24px 50px rgba(35, 47, 62, 0.08);
        }

        .sidebar-title {
            color: #232F3E;
            font-size: 1.15rem;
            font-weight: 700;
            margin-bottom: 0.75rem;
        }

        .cart-item {
            margin-bottom: 0.9rem;
            padding-bottom: 0.8rem;
            border-bottom: 1px solid #E5E7EB;
        }

        .cart-item:last-child {
            border-bottom: none;
        }

        .cart-remove {
            background: transparent;
            border: none;
            color: #D9480F;
            font-weight: 700;
            cursor: pointer;
            padding: 0;
            margin-top: 0.4rem;
        }

        .cart-total {
            font-size: 1.05rem;
            font-weight: 700;
            margin-top: 1rem;
            color: #232F3E;
        }

        .assistant-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 1rem;
            margin-bottom: 1rem;
        }

        .assistant-title {
            font-size: 1.2rem;
            font-weight: 700;
            margin: 0;
            color: #232F3E;
        }

        .assistant-subtitle {
            color: #6B7280;
            margin: 0.2rem 0 0;
            font-size: 0.95rem;
        }

        .microphone-placeholder {
            width: 36px;
            height: 36px;
            border-radius: 50%;
            background: #FBBF24;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            color: #1F2937;
            font-weight: 700;
            cursor: not-allowed;
        }

        .chat-bubble {
            border-radius: 24px;
            padding: 0.9rem 1rem;
            margin-bottom: 0.85rem;
            line-height: 1.45;
            max-width: 92%;
            word-wrap: break-word;
        }

        .chat-bubble.user {
            background: #FF9900;
            color: white;
            margin-left: auto;
        }

        .chat-bubble.assistant {
            background: #F3F4F6;
            color: #111827;
            margin-right: auto;
        }

        .chat-area {
            max-height: 50vh;
            overflow-y: auto;
            margin-bottom: 1rem;
            padding-right: 0.5rem;
        }

        .chat-footer {
            display: grid;
            grid-template-columns: 1fr auto;
            gap: 0.75rem;
            align-items: center;
        }

        .stSidebar .st-key-assistant_input_row {
            margin-top: 0.9rem;
            padding: 0.15rem 0 0;
        }

        .stSidebar .st-key-assistant_input_row [data-testid="stHorizontalBlock"],
        .stSidebar [data-testid="stHorizontalBlock"]:has(input) {
            gap: 0 !important;
            align-items: stretch;
            flex-wrap: nowrap;
        }

        .stSidebar .st-key-assistant_input_row [data-testid="column"],
        .stSidebar [data-testid="stHorizontalBlock"]:has(input) [data-testid="column"] {
            min-width: 0 !important;
        }

        .stSidebar .st-key-assistant_input_row [data-testid="stTextInput"],
        .stSidebar .st-key-assistant_input_row div[data-testid="stButton"],
        .stSidebar [data-testid="stHorizontalBlock"]:has(input) [data-testid="stTextInput"],
        .stSidebar [data-testid="stHorizontalBlock"]:has(input) div[data-testid="stButton"] {
            margin-bottom: 0 !important;
        }

        .chat-footer input,
        .stSidebar .st-key-assistant_input_row input,
        .stSidebar [data-testid="stHorizontalBlock"]:has(input) input {
            min-height: 3rem !important;
            border-radius: 18px !important;
            border: 1px solid #D1D5DB !important;
            padding: 0.85rem 1rem !important;
            width: 100% !important;
            box-shadow: inset 0 4px 12px rgba(35, 47, 62, 0.08) !important;
        }

        .stSidebar .st-key-assistant_input_row input:focus,
        .stSidebar [data-testid="stHorizontalBlock"]:has(input) input:focus {
            border-color: #FF9900 !important;
            box-shadow: 0 0 0 4px rgba(255, 153, 0, 0.16) !important;
        }

        .stSidebar .st-key-assistant_input_row [data-testid="column"]:first-child input,
        .stSidebar [data-testid="stHorizontalBlock"]:has(input) [data-testid="column"]:first-child input {
            border-radius: 18px 0 0 18px !important;
            border-right: none !important;
        }

        .stSidebar .st-key-assistant_input_row div[data-testid="stButton"],
        .stSidebar [data-testid="stHorizontalBlock"]:has(input) div[data-testid="stButton"] {
            height: 100%;
        }

        .stSidebar .st-key-assistant_input_row div[data-testid="stButton"] button,
        .stSidebar [data-testid="stHorizontalBlock"]:has(input) div[data-testid="stButton"] button {
            width: 100%;
            min-width: 44px;
            min-height: 3rem;
            border-radius: 0 18px 18px 0;
            border: 1px solid #FF9900;
            background: #FF9900;
            color: white;
            font-size: 1.18rem;
            line-height: 1;
            padding: 0;
            box-shadow: 0 8px 20px rgba(255, 153, 0, 0.24);
        }

        .stSidebar .st-key-assistant_input_row div[data-testid="stButton"] button:hover,
        .stSidebar [data-testid="stHorizontalBlock"]:has(input) div[data-testid="stButton"] button:hover {
            background: #e88c00;
            border-color: #e88c00;
            color: white;
        }

        .voice-status {
            color: #2563EB;
            font-size: 0.9rem;
            font-weight: 700;
            margin: 0.35rem 0 0.65rem;
        }

        .voice-transcript {
            background: #ECFDF5;
            border: 1px solid #A7F3D0;
            border-radius: 16px;
            color: #065F46;
            font-size: 0.9rem;
            line-height: 1.45;
            margin: 0.4rem 0 0.8rem;
            padding: 0.75rem 0.85rem;
        }

        .voice-error {
            background: #FFF7ED;
            border: 1px solid #FDBA74;
            border-radius: 16px;
            color: #9A3412;
            font-size: 0.9rem;
            line-height: 1.45;
            margin: 0.4rem 0 0.8rem;
            padding: 0.75rem 0.85rem;
        }

        @media (max-width: 640px) {
            .stSidebar .st-key-assistant_input_row div[data-testid="stButton"] button,
            .stSidebar [data-testid="stHorizontalBlock"]:has(input) div[data-testid="stButton"] button {
                min-width: 42px;
                min-height: 2.85rem;
            }
        }

        [data-testid="InputInstructions"] {
            display: none;
        }

        .chat-send {
            background: #232F3E;
            color: white;
            border-radius: 999px;
            border: none;
            padding: 0.92rem 1.15rem;
            font-weight: 700;
            cursor: pointer;
        }

        .assistant-indicator {
            font-size: 0.95rem;
            color: #2563EB;
            margin-bottom: 0.8rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def load_products() -> List[Dict[str, Any]]:
    # Use a stable local earbuds dataset for offline demo
    root = os.path.dirname(__file__)
    assets_dir = os.path.join(root, "assets")
    # Ensure asset paths are relative for Streamlit to serve
    products: List[Dict[str, Any]] = [
        {"id": "nb_vs102", "name": "Noise Buds VS102", "brand": "Noise", "price": "₹1,299", "price_value": 1299.0, "image": os.path.join("assets", "noise_buds_vs102.svg"), "category": "Earbuds", "rating": 4.2, "reviewCount": 124, "description": "Lightweight earbuds with immersive sound."},
        {"id": "boat_141", "name": "boAt Airdopes 141", "brand": "boAt", "price": "₹999", "price_value": 999.0, "image": os.path.join("assets", "boat_airdopes_141.svg"), "category": "Earbuds", "rating": 4.0, "reviewCount": 98, "description": "Affordable true wireless earbuds with punchy bass."},
        {"id": "realme_t300", "name": "Realme Buds T300", "brand": "Realme", "price": "₹1,499", "price_value": 1499.0, "image": os.path.join("assets", "realme_buds_t300.svg"), "category": "Earbuds", "rating": 4.3, "reviewCount": 76, "description": "Comfortable fit with long battery life."},
        {"id": "oneplus_2r", "name": "OnePlus Nord Buds 2r", "brand": "OnePlus", "price": "₹2,299", "price_value": 2299.0, "image": os.path.join("assets", "oneplus_nord_buds_2r.svg"), "category": "Earbuds", "rating": 4.4, "reviewCount": 210, "description": "Balanced sound profile with low latency mode."},
        {"id": "samsung_fe", "name": "Samsung Galaxy Buds FE", "brand": "Samsung", "price": "₹3,499", "price_value": 3499.0, "image": os.path.join("assets", "samsung_galaxy_buds_fe.svg"), "category": "Earbuds", "rating": 4.1, "reviewCount": 65, "description": "Reliable everyday earbuds from Samsung."},
        {"id": "sony_c500", "name": "Sony WF-C500", "brand": "Sony", "price": "₹4,199", "price_value": 4199.0, "image": os.path.join("assets", "sony_wf_c500.svg"), "category": "Earbuds", "rating": 4.5, "reviewCount": 142, "description": "Signature Sony sound in a compact package."},
        {"id": "jbl_wave_beam", "name": "JBL Wave Beam", "brand": "JBL", "price": "₹2,799", "price_value": 2799.0, "image": os.path.join("assets", "jbl_wave_beam.svg"), "category": "Earbuds", "rating": 4.0, "reviewCount": 88, "description": "Vibrant sound and robust build quality."},
    ]

    # Ensure assets directory exists; Streamlit will serve relative asset paths.
    try:
        if not os.path.exists(assets_dir):
            os.makedirs(assets_dir, exist_ok=True)
    except Exception:
        pass

    return products


def _get_image_cache_path() -> str:
    root = os.path.dirname(__file__)
    return os.path.join(root, "data", IMAGE_CACHE_FILENAME)


def load_image_cache() -> Dict[str, str]:
    path = _get_image_cache_path()
    if not os.path.exists(path):
        return {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def save_image_cache(cache: Dict[str, str]) -> None:
    path = _get_image_cache_path()
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(cache, f, indent=2)
    except Exception:
        pass


def ensure_image_cache() -> Dict[str, str]:
    if "ai_image_cache" not in st.session_state:
        st.session_state.ai_image_cache = load_image_cache()
    return st.session_state.ai_image_cache


def _get_product_cache_key(product: Dict[str, Any]) -> str:
    if product.get("id"):
        return str(product["id"])
    fallback = " ".join(
        str(product.get(field, "")) for field in ("name", "brand", "category")
    )
    return hashlib.sha256(fallback.encode("utf-8")).hexdigest()


def build_image_prompt(product: Dict[str, Any]) -> str:
    name = product.get("name", "Product")
    brand = product.get("brand", "")
    category = product.get("category", "")
    parts = [name.strip(), brand.strip(), category.strip(), "high quality ecommerce product photo"]
    return ", ".join(part for part in parts if part)


def generate_product_image(prompt: str) -> str:
    try:
        return f"{IMAGE_API_BASE}/{quote_plus(prompt)}"
    except Exception:
        return "https://via.placeholder.com/300x200.png?text=Product"


def generate_ai_image(product: Dict[str, Any]) -> str:
    cache = ensure_image_cache()
    cache_key = _get_product_cache_key(product)
    if cache_key in cache:
        return cache[cache_key]

    prompt = build_image_prompt(product)
    image_url = generate_product_image(prompt)
    cache[cache_key] = image_url
    save_image_cache(cache)
    return image_url


def is_valid_image_url(url: Any) -> bool:
    return isinstance(url, str) and url.strip() and url.strip().lower().startswith("http")


def get_product_image(product: Dict[str, Any]) -> str:
    PLACEHOLDER_IMAGE = "https://via.placeholder.com/300x300?text=No+Image"

    image_url = product.get("image")
    if is_valid_image_url(image_url):
        return image_url.strip()

    # Try Unsplash first using product name/brand/category
    query_parts = [str(product.get("name", "")), str(product.get("brand", "")), str(product.get("category", ""))]
    query = " ".join(p for p in query_parts if p).strip()
    if query:
        unsplash_url = get_unsplash_image(query)
        if is_valid_image_url(unsplash_url) and unsplash_url != PLACEHOLDER_IMAGE:
            product["image"] = unsplash_url
            return unsplash_url

    # Fallback to AI generated image
    try:
        ai_url = generate_ai_image(product)
        if is_valid_image_url(ai_url):
            product["image"] = ai_url
            return ai_url
    except Exception:
        pass

    # Final placeholder
    product["image"] = PLACEHOLDER_IMAGE
    return PLACEHOLDER_IMAGE


def get_unsplash_image(query: str) -> str:
    """Return a single Unsplash image URL for the given query or a placeholder if none found."""
    placeholder = "https://via.placeholder.com/300x300?text=No+Image"
    access_key = os.getenv("UNSPLASH_ACCESS_KEY")
    if not access_key:
        return placeholder

    try:
        url = f"https://api.unsplash.com/search/photos?query={quote_plus(query)}&per_page=1"
        headers = {"Authorization": f"Client-ID {access_key}"}
        resp = requests.get(url, headers=headers, timeout=6)
        if resp.status_code != 200:
            return placeholder
        data = resp.json()
        results = data.get("results") or []
        if not results:
            return placeholder
        return results[0].get("urls", {}).get("regular") or placeholder
    except Exception:
        return placeholder


def initialize_session_state() -> None:
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "current_recommendations" not in st.session_state:
        st.session_state.current_recommendations = []
    if "selected_product" not in st.session_state:
        st.session_state.selected_product = None
    if "cart" not in st.session_state:
        st.session_state.cart = []
    if "search_query" not in st.session_state:
        st.session_state.search_query = ""
    if "assistant_input" not in st.session_state:
        st.session_state.assistant_input = ""
    if "ai_input" not in st.session_state:
        st.session_state.ai_input = ""
    if "ai_image_cache" not in st.session_state:
        st.session_state.ai_image_cache = load_image_cache()
    if "ai_typing" not in st.session_state:
        st.session_state.ai_typing = False
    if "ai_query_pending" not in st.session_state:
        st.session_state.ai_query_pending = ""
    if "voice_listening" not in st.session_state:
        st.session_state.voice_listening = False
    if "voice_request_id" not in st.session_state:
        st.session_state.voice_request_id = 0
    if "processed_voice_nonce" not in st.session_state:
        st.session_state.processed_voice_nonce = ""
    if "last_voice_transcript" not in st.session_state:
        st.session_state.last_voice_transcript = ""
    if "voice_error_message" not in st.session_state:
        st.session_state.voice_error_message = ""
    if "last_spoken_response" not in st.session_state:
        st.session_state.last_spoken_response = ""
    if "last_spoken_response_id" not in st.session_state:
        st.session_state.last_spoken_response_id = 0
    if "voice_session_id" not in st.session_state:
        st.session_state.voice_session_id = hashlib.sha256(os.urandom(16)).hexdigest()[:12]
    if "current_language" not in st.session_state:
        st.session_state.current_language = "en-IN"
    if "conversation_mode" not in st.session_state:
        st.session_state.conversation_mode = False
    if "auto_listening_enabled" not in st.session_state:
        st.session_state.auto_listening_enabled = False
    if "voice_status" not in st.session_state:
        st.session_state.voice_status = "ready"
    if "voice_language_probe_index" not in st.session_state:
        st.session_state.voice_language_probe_index = 0


def detect_language(text: str) -> str:
    """Detect supported voice language from script; default to English."""
    if not text:
        return "en-IN"

    for char in text:
        codepoint = ord(char)
        if 0x0C00 <= codepoint <= 0x0C7F:
            return "te-IN"
        if 0x0900 <= codepoint <= 0x097F:
            return "hi-IN"
    return "en-IN"


def translate_assistant_response(response: str, language: str) -> str:
    if language == "te-IN":
        return translate_response_to_telugu(response)
    if language == "hi-IN":
        return translate_response_to_hindi(response)
    return response


def _translate_recommendation_line(line: str, language: str) -> str:
    match = re.match(
        r"^(\d+)\.\s+(.+?) by (.+?) — (.+?), rating (.+?), (\d+) reviews$",
        line,
    )
    if not match:
        return line

    index, name, brand, price, rating, reviews = match.groups()
    if language == "te-IN":
        return f"{index}. {name} - బ్రాండ్: {brand}, ధర: {price}, రేటింగ్ {rating}, {reviews} రివ్యూలు"
    if language == "hi-IN":
        return f"{index}. {name} - ब्रांड: {brand}, कीमत: {price}, रेटिंग {rating}, {reviews} समीक्षाएँ"
    return line


def _translate_detail_line(line: str, language: str) -> str:
    labels = {
        "te-IN": {
            "Brand": "బ్రాండ్",
            "Category": "వర్గం",
            "Price": "ధర",
            "Rating": "రేటింగ్",
            "Reviews": "రివ్యూలు",
            "Description": "వివరణ",
        },
        "hi-IN": {
            "Brand": "ब्रांड",
            "Category": "श्रेणी",
            "Price": "कीमत",
            "Rating": "रेटिंग",
            "Reviews": "समीक्षाएँ",
            "Description": "विवरण",
        },
    }
    for english, translated in labels.get(language, {}).items():
        prefix = f"- {english}: "
        if line.startswith(prefix):
            return f"- {translated}: {line[len(prefix):]}"
    return line


def translate_response_to_telugu(response: str) -> str:
    if not response:
        return response

    replacements = {
        "Please type a message so I can help you shop.": "మీకు షాపింగ్‌లో సహాయం చేయడానికి దయచేసి ఒక సందేశం చెప్పండి.",
        "Your cart is empty.": "మీ కార్ట్ ఖాళీగా ఉంది.",
        "Your cart is empty. Add a product before checkout.": "మీ కార్ట్ ఖాళీగా ఉంది. చెకౌట్‌కు ముందు ఒక ఉత్పత్తిని జోడించండి.",
        "I couldn't find matching products. Try a different category or price range.": "సరిపోలే ఉత్పత్తులు కనబడలేదు. మరో వర్గం లేదా ధర పరిధిని ప్రయత్నించండి.",
        "I couldn't find any matching products. Can you try another request?": "సరిపోలే ఉత్పత్తులు కనబడలేదు. మరో అభ్యర్థన ప్రయత్నించగలరా?",
        "Please tell me which product to remove from your cart.": "మీ కార్ట్ నుండి ఏ ఉత్పత్తిని తీసివేయాలో చెప్పండి.",
        "I couldn't find that product in your cart. Please try using the full product name.": "ఆ ఉత్పత్తి మీ కార్ట్‌లో కనబడలేదు. దయచేసి పూర్తి ఉత్పత్తి పేరును చెప్పండి.",
        "Please tell me which product you want details for, like a product name or the first recommendation.": "ఏ ఉత్పత్తి వివరాలు కావాలో చెప్పండి, ఉదాహరణకు ఉత్పత్తి పేరు లేదా మొదటి సిఫార్సు.",
        "Please tell me which two products to compare, for example compare first and second from the same category.": "ఏ రెండు ఉత్పత్తులను పోల్చాలో చెప్పండి, ఉదాహరణకు అదే వర్గంలో మొదటి మరియు రెండవవి.",
        "I couldn't compare those products. Please try a more specific comparison request.": "ఆ ఉత్పత్తులను పోల్చలేకపోయాను. దయచేసి మరింత స్పష్టంగా అడగండి.",
        "Both products have similar ratings, so choose based on price or style preferences.": "రెండు ఉత్పత్తుల రేటింగ్‌లు దగ్గరగా ఉన్నాయి, కాబట్టి ధర లేదా మీ అభిరుచి ఆధారంగా ఎంచుకోండి.",
        "I can help you find products, compare them, add or remove items from your cart, show your cart, or checkout. Try asking for a category like 'best earbuds' or 'compare smartwatches'.": "నేను ఉత్పత్తులను కనుగొనడం, పోల్చడం, కార్ట్‌లో జోడించడం లేదా తీసివేయడం, కార్ట్ చూపించడం, చెకౌట్ చేయడంలో సహాయం చేస్తాను. 'బెస్ట్ ఇయర్‌బడ్స్' లేదా 'స్మార్ట్‌వాచెస్ పోల్చు' అని అడగండి.",
    }
    if response in replacements:
        return replacements[response]

    product_added = re.match(r"^(.+) has been added to your cart\.$", response)
    if product_added:
        return f"{product_added.group(1)} మీ కార్ట్‌లో జోడించబడింది."

    product_removed = re.match(r"^(.+) has been removed from your cart\.$", response)
    if product_removed:
        return f"{product_removed.group(1)} మీ కార్ట్ నుండి తీసివేయబడింది."

    order = re.match(r"^Your order is confirmed\. Total payment is (.+)\. Thank you for shopping with ShopEase Copilot!$", response)
    if order:
        return f"మీ ఆర్డర్ నిర్ధారించబడింది. మొత్తం చెల్లింపు {order.group(1)}. ShopEase Copilot తో షాపింగ్ చేసినందుకు ధన్యవాదాలు!"

    lines = response.splitlines()
    translated_lines = []
    for line in lines:
        if line.startswith("Here are the top"):
            translated_lines.append(line.replace("Here are the top", "ఇవి టాప్").replace("products", "ఉత్పత్తులు").replace("for", "వర్గం").replace("under", "లోపు"))
        elif line == "You can ask me to add one of these to your cart, compare products, or request more details.":
            translated_lines.append("ఇవిలో ఒకదాన్ని కార్ట్‌లో జోడించమని, ఉత్పత్తులను పోల్చమని, లేదా మరిన్ని వివరాలు అడగవచ్చు.")
        elif line.startswith("Here are the details for "):
            name = line.removeprefix("Here are the details for ").removesuffix(":")
            translated_lines.append(f"{name} వివరాలు ఇవి:")
        elif line.startswith("Comparing "):
            translated_lines.append(line.replace("Comparing", "పోల్చుతున్నాను").replace(" and ", " మరియు "))
        elif line.startswith("I recommend ") and " for a stronger overall rating." in line:
            name = line.removeprefix("I recommend ").removesuffix(" for a stronger overall rating.")
            translated_lines.append(f"మొత్తం రేటింగ్ మెరుగ్గా ఉండటం వల్ల {name} ను సిఫార్సు చేస్తున్నాను.")
        else:
            translated_lines.append(_translate_detail_line(_translate_recommendation_line(line, "te-IN"), "te-IN"))
    return "\n".join(translated_lines)


def translate_response_to_hindi(response: str) -> str:
    if not response:
        return response

    replacements = {
        "Please type a message so I can help you shop.": "खरीदारी में मदद के लिए कृपया एक संदेश बोलें या टाइप करें.",
        "Your cart is empty.": "आपकी कार्ट खाली है.",
        "Your cart is empty. Add a product before checkout.": "आपकी कार्ट खाली है. चेकआउट से पहले कोई उत्पाद जोड़ें.",
        "I couldn't find matching products. Try a different category or price range.": "मिलते-जुलते उत्पाद नहीं मिले. कोई दूसरी श्रेणी या कीमत सीमा आज़माएँ.",
        "I couldn't find any matching products. Can you try another request?": "मिलते-जुलते उत्पाद नहीं मिले. क्या आप दूसरा अनुरोध आज़माएँगे?",
        "Please tell me which product to remove from your cart.": "कृपया बताइए कि कार्ट से कौन सा उत्पाद हटाना है.",
        "I couldn't find that product in your cart. Please try using the full product name.": "वह उत्पाद आपकी कार्ट में नहीं मिला. कृपया पूरा उत्पाद नाम बोलें.",
        "Please tell me which product you want details for, like a product name or the first recommendation.": "कृपया बताइए किस उत्पाद की जानकारी चाहिए, जैसे उत्पाद का नाम या पहला सुझाव.",
        "Please tell me which two products to compare, for example compare first and second from the same category.": "कृपया बताइए किन दो उत्पादों की तुलना करनी है, जैसे उसी श्रेणी में पहले और दूसरे की तुलना.",
        "I couldn't compare those products. Please try a more specific comparison request.": "मैं उन उत्पादों की तुलना नहीं कर सका. कृपया थोड़ा और स्पष्ट अनुरोध करें.",
        "Both products have similar ratings, so choose based on price or style preferences.": "दोनों उत्पादों की रेटिंग लगभग समान है, इसलिए कीमत या अपनी पसंद के आधार पर चुनें.",
        "I can help you find products, compare them, add or remove items from your cart, show your cart, or checkout. Try asking for a category like 'best earbuds' or 'compare smartwatches'.": "मैं उत्पाद खोजने, तुलना करने, कार्ट में जोड़ने या हटाने, कार्ट दिखाने और चेकआउट में मदद कर सकता हूँ. 'बेस्ट ईयरबड्स' या 'स्मार्टवॉच तुलना करें' जैसा पूछें.",
    }
    if response in replacements:
        return replacements[response]

    product_added = re.match(r"^(.+) has been added to your cart\.$", response)
    if product_added:
        return f"{product_added.group(1)} आपकी कार्ट में जोड़ दिया गया है."

    product_removed = re.match(r"^(.+) has been removed from your cart\.$", response)
    if product_removed:
        return f"{product_removed.group(1)} आपकी कार्ट से हटा दिया गया है."

    order = re.match(r"^Your order is confirmed\. Total payment is (.+)\. Thank you for shopping with ShopEase Copilot!$", response)
    if order:
        return f"आपका ऑर्डर कन्फर्म हो गया है. कुल भुगतान {order.group(1)} है. ShopEase Copilot से खरीदारी करने के लिए धन्यवाद!"

    lines = response.splitlines()
    translated_lines = []
    for line in lines:
        if line.startswith("Here are the top"):
            translated_lines.append(line.replace("Here are the top", "ये टॉप").replace("products", "उत्पाद हैं").replace("for", "श्रेणी").replace("under", "से कम"))
        elif line == "You can ask me to add one of these to your cart, compare products, or request more details.":
            translated_lines.append("आप इनमें से किसी एक को कार्ट में जोड़ने, उत्पादों की तुलना करने, या और जानकारी माँगने के लिए कह सकते हैं.")
        elif line.startswith("Here are the details for "):
            name = line.removeprefix("Here are the details for ").removesuffix(":")
            translated_lines.append(f"{name} की जानकारी यह है:")
        elif line.startswith("Comparing "):
            translated_lines.append(line.replace("Comparing", "तुलना कर रहा हूँ:").replace(" and ", " और "))
        elif line.startswith("I recommend ") and " for a stronger overall rating." in line:
            name = line.removeprefix("I recommend ").removesuffix(" for a stronger overall rating.")
            translated_lines.append(f"बेहतर कुल रेटिंग के लिए मैं {name} की सलाह देता हूँ.")
        else:
            translated_lines.append(_translate_detail_line(_translate_recommendation_line(line, "hi-IN"), "hi-IN"))
    return "\n".join(translated_lines)


def get_query_param(name: str) -> str:
    try:
        value = st.query_params.get(name, "")
    except Exception:
        value = ""
    if isinstance(value, list):
        return str(value[0]) if value else ""
    return str(value or "")


def clear_voice_query_params() -> None:
    try:
        for key in ("voice_query", "voice_nonce", "voice_error", "voice_restart", "voice_status"):
            if key in st.query_params:
                del st.query_params[key]
    except Exception:
        pass


def submit_assistant_query(
    message: str,
    products: List[Dict[str, Any]],
    *,
    clear_input: bool = False,
) -> str:
    msg = (message or "").strip()
    if not msg:
        return ""

    detected_language = detect_language(msg)
    st.session_state.current_language = detected_language
    if detected_language in VOICE_LANGUAGE_FALLBACK_ORDER:
        st.session_state.voice_language_probe_index = VOICE_LANGUAGE_FALLBACK_ORDER.index(detected_language)

    st.session_state.chat_history.append({"role": "user", "text": msg})
    response = process_user_query(msg, products)
    response = translate_assistant_response(response, detected_language)
    st.session_state.chat_history.append({"role": "assistant", "text": response})
    st.session_state.last_spoken_response = response
    st.session_state.last_spoken_response_id = (
        f"{st.session_state.voice_session_id}-{len(st.session_state.chat_history)}"
    )

    if clear_input:
        st.session_state.ai_input = ""

    return response


def submit_typed_assistant_query(products: List[Dict[str, Any]]) -> None:
    submit_assistant_query(
        st.session_state.get("ai_input", ""),
        products,
        clear_input=True,
    )


def handle_voice_query(products: List[Dict[str, Any]]) -> None:
    transcript = get_query_param("voice_query").strip()
    nonce = get_query_param("voice_nonce").strip()
    error = get_query_param("voice_error").strip()
    restart = get_query_param("voice_restart").strip()
    status = get_query_param("voice_status").strip()

    if status in VOICE_STATUS_LABELS:
        st.session_state.voice_status = status

    if restart and restart != st.session_state.processed_voice_nonce:
        st.session_state.processed_voice_nonce = restart
        if st.session_state.get("auto_listening_enabled"):
            st.session_state.voice_listening = True
            st.session_state.voice_status = "ready"
            st.session_state.voice_request_id += 1
        clear_voice_query_params()
        st.rerun()
        return

    if error:
        recoverable_errors = {"no-speech", "network", "audio-capture", "no-match"}
        terminal_errors = {"not-allowed", "permission-denied", "service-not-allowed"}
        st.session_state.voice_listening = error in recoverable_errors and st.session_state.get("auto_listening_enabled")
        st.session_state.auto_listening_enabled = False if error in terminal_errors else st.session_state.get("auto_listening_enabled", False)
        st.session_state.conversation_mode = st.session_state.auto_listening_enabled
        st.session_state.voice_status = "ready" if st.session_state.voice_listening else "ready"
        st.session_state.last_voice_transcript = ""
        if error in {"no-speech", "no-match"} and st.session_state.voice_listening:
            probe_index = st.session_state.get("voice_language_probe_index", 0)
            probe_index = (probe_index + 1) % len(VOICE_LANGUAGE_FALLBACK_ORDER)
            st.session_state.voice_language_probe_index = probe_index
            st.session_state.current_language = VOICE_LANGUAGE_FALLBACK_ORDER[probe_index]
        if error in terminal_errors:
            st.session_state.voice_error_message = "Microphone permission is blocked. Please allow microphone access and tap the mic again."
        elif error == "audio-capture":
            st.session_state.voice_error_message = "I couldn't access the microphone. Please check your audio input."
        elif error == "network":
            st.session_state.voice_error_message = "Voice recognition had a network issue. I'll try listening again."
        else:
            st.session_state.voice_error_message = "I couldn't hear that clearly. I'll listen again."
        if st.session_state.voice_listening:
            st.session_state.voice_request_id += 1
        clear_voice_query_params()
        st.rerun()
        return

    if not transcript or not nonce or nonce == st.session_state.processed_voice_nonce:
        return

    st.session_state.processed_voice_nonce = nonce
    st.session_state.voice_listening = False
    st.session_state.voice_status = "processing"
    st.session_state.voice_error_message = ""
    st.session_state.last_voice_transcript = transcript
    st.session_state.ai_input = transcript
    st.session_state.current_language = detect_language(transcript)
    if st.session_state.current_language in VOICE_LANGUAGE_FALLBACK_ORDER:
        st.session_state.voice_language_probe_index = VOICE_LANGUAGE_FALLBACK_ORDER.index(st.session_state.current_language)
    submit_assistant_query(transcript, products)
    clear_voice_query_params()
    st.rerun()


def render_voice_recognition_bridge() -> None:
    if not st.session_state.get("voice_listening"):
        return

    request_id = st.session_state.get("voice_request_id", 0)
    current_language = st.session_state.get("current_language", "en-IN")
    if current_language not in SUPPORTED_VOICE_LANGUAGES:
        current_language = "en-IN"
    auto_listening_enabled = bool(st.session_state.get("auto_listening_enabled"))
    st.html(
        f"""
        <script>
        const requestId = {json.dumps(str(request_id))};
        const currentLanguage = {json.dumps(current_language)};
        const autoListeningEnabled = {json.dumps(auto_listening_enabled)};
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        const targetWindow = window.parent && window.parent !== window ? window.parent : window;
        targetWindow.__shopeaseVoiceShouldListen = true;

        const sendResult = (key, value) => {{
            const url = new URL(targetWindow.location.href);
            url.searchParams.set(key, value);
            url.searchParams.set("voice_nonce", `${{requestId}}-${{Date.now()}}`);
            targetWindow.location.href = url.toString();
        }};

        if (!SpeechRecognition) {{
            sendResult("voice_error", "Speech recognition is not supported in this browser.");
        }} else {{
            if (targetWindow.__shopeaseRecognition) {{
                try {{ targetWindow.__shopeaseRecognition.abort(); }} catch (error) {{}}
                targetWindow.__shopeaseRecognition = null;
            }}

            const recognition = new SpeechRecognition();
            targetWindow.__shopeaseRecognition = recognition;
            recognition.lang = currentLanguage;
            recognition.interimResults = false;
            recognition.continuous = false;
            recognition.maxAlternatives = 1;
            let hasResult = false;
            let hasError = false;

            recognition.onresult = (event) => {{
                hasResult = true;
                const transcript = event.results?.[0]?.[0]?.transcript || "";
                if (transcript.trim()) {{
                    targetWindow.__shopeaseVoiceShouldListen = false;
                    sendResult("voice_query", transcript.trim());
                }} else {{
                    sendResult("voice_error", "no-speech");
                }}
            }};

            recognition.onnomatch = () => {{
                hasError = true;
                sendResult("voice_error", "no-match");
            }};

            recognition.onerror = (event) => {{
                hasError = true;
                sendResult("voice_error", event.error || "speech-recognition-error");
            }};

            recognition.onend = () => {{
                if (targetWindow.__shopeaseRecognition === recognition) {{
                    targetWindow.__shopeaseRecognition = null;
                }}
                if (!hasResult && !hasError && targetWindow.__shopeaseVoiceShouldListen && autoListeningEnabled) {{
                    sendResult("voice_error", "no-speech");
                }}
            }};

            try {{
                recognition.start();
            }} catch (error) {{
                sendResult("voice_error", error?.name || "speech-recognition-start-error");
            }}
        }}
        </script>
        """,
        unsafe_allow_javascript=True,
    )


def render_speech_synthesis_bridge() -> None:
    response = st.session_state.get("last_spoken_response", "")
    response_id = st.session_state.get("last_spoken_response_id", 0)
    if not response or not response_id or st.session_state.get("voice_listening"):
        return

    current_language = st.session_state.get("current_language", "en-IN")
    if current_language not in SUPPORTED_VOICE_LANGUAGES:
        current_language = "en-IN"
    auto_listening_enabled = bool(st.session_state.get("auto_listening_enabled"))
    voice_session_id = st.session_state.get("voice_session_id", "default")
    st.session_state.voice_status = "speaking"
    st.html(
        f"""
        <script>
        const responseId = {json.dumps(str(response_id))};
        const text = {json.dumps(response)};
        const language = {json.dumps(current_language)};
        const autoListeningEnabled = {json.dumps(auto_listening_enabled)};
        const storageKey = "shopease_spoken_response_id_" + {json.dumps(str(voice_session_id))};
        const targetWindow = window.parent && window.parent !== window ? window.parent : window;
        let speechStarted = false;

        const sendRestart = () => {{
            if (!autoListeningEnabled) return;
            const url = new URL(targetWindow.location.href);
            url.searchParams.set("voice_restart", `${{responseId}}-${{Date.now()}}`);
            targetWindow.location.href = url.toString();
        }};

        const chooseVoice = (voices, lang) => {{
            const normalized = lang.toLowerCase();
            return (
                voices.find((voice) => voice.lang?.toLowerCase() === normalized) ||
                voices.find((voice) => voice.lang?.toLowerCase().startsWith(normalized.split("-")[0])) ||
                voices.find((voice) => voice.lang?.toLowerCase() === "en-in") ||
                null
            );
        }};

        const speak = () => {{
            if (speechStarted) return;
            if (!("speechSynthesis" in window) || localStorage.getItem(storageKey) === responseId) {{
                sendRestart();
                return;
            }}
            speechStarted = true;

            targetWindow.__shopeaseVoiceShouldListen = false;
            if (targetWindow.__shopeaseRecognition) {{
                try {{ targetWindow.__shopeaseRecognition.abort(); }} catch (error) {{}}
                targetWindow.__shopeaseRecognition = null;
            }}

            window.speechSynthesis.cancel();
            const utterance = new SpeechSynthesisUtterance(text);
            utterance.lang = language;
            utterance.rate = 0.95;
            const voices = window.speechSynthesis.getVoices();
            const matchedVoice = chooseVoice(voices, language);
            if (matchedVoice) {{
                utterance.voice = matchedVoice;
            }}
            utterance.onend = () => {{
                localStorage.setItem(storageKey, responseId);
                targetWindow.__shopeaseVoiceShouldListen = autoListeningEnabled;
                sendRestart();
            }};
            utterance.onerror = () => {{
                localStorage.setItem(storageKey, responseId);
                targetWindow.__shopeaseVoiceShouldListen = autoListeningEnabled;
                sendRestart();
            }};
            window.speechSynthesis.speak(utterance);
        }};

        if (window.speechSynthesis.getVoices().length) {{
            speak();
        }} else {{
            window.speechSynthesis.onvoiceschanged = speak;
            setTimeout(speak, 600);
        }}
        </script>
        """,
        unsafe_allow_javascript=True,
    )


def add_to_cart(product: Dict[str, Any]) -> None:
    if not product:
        return

    cart = st.session_state.cart
    product_id = str(product.get("id") or _get_product_cache_key(product))
    # find existing entry
    for entry in cart:
        pid = str(entry.get("product", {}).get("id") or _get_product_cache_key(entry.get("product", {})))
        if pid == product_id:
            entry["quantity"] = entry.get("quantity", 1) + 1
            st.session_state.cart = cart
            return

    # add new entry
    cart.append({"product": product, "quantity": 1})
    st.session_state.cart = cart


def remove_from_cart(product_id: str) -> None:
    if not product_id:
        return

    cart = st.session_state.cart
    key = str(product_id)
    new_cart = [entry for entry in cart if str(entry.get("product", {}).get("id") or _get_product_cache_key(entry.get("product", {}))) != key]
    st.session_state.cart = new_cart


def add_to_cart_by_id(product_id: str) -> None:
    """Find product by id from the local catalog and add to cart, then notify."""
    if not product_id:
        return
    products = load_products()
    prod = next((p for p in products if str(p.get("id")) == str(product_id)), None)
    if not prod:
        return
    add_to_cart(prod)
    st.session_state.chat_history.append({"role": "assistant", "text": f"{prod.get('name')} has been added to your cart."})
    st.toast(f"{prod.get('name')} added to cart!")
    st.rerun()


def normalize_text(text: str) -> str:
    return (text or "").strip().lower()


def contains_any(text: str, keywords: Set[str]) -> bool:
    normalized = normalize_text(text)
    return any(keyword in normalized for keyword in keywords)


def parse_recommendation_request(text: str) -> tuple[Optional[str], Optional[float]]:
    normalized = normalize_text(text)
    if not normalized:
        return None, None

    budget = None
    match = re.search(r"[\$\₹]\s*([0-9,]+(?:\.[0-9]+)?)", normalized)
    if match:
        try:
            budget = float(match.group(1).replace(",", ""))
        except ValueError:
            budget = None
    else:
        match = re.search(r"(?:under|below|less than|underneath|ఇంకా తక్కువ|కంటే తక్కువ|कम से कम|से कम)\s+[\$\₹]?\s*([0-9,]+)", normalized)
        if match:
            try:
                budget = float(match.group(1).replace(",", ""))
            except ValueError:
                budget = None

    category = None
    for token, mapped in CATEGORY_TOKENS.items():
        if token in normalized:
            category = mapped
            break

    return category, budget


def find_product_by_name(query: str, products: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    normalized = normalize_text(query)
    if not normalized:
        return None
    for product in products:
        name = normalize_text(product.get("name", ""))
        brand = normalize_text(product.get("brand", ""))
        if normalized == name or normalized in name or normalized in brand:
            return product
    return None


def find_recommendation_by_index(query: str) -> Optional[Dict[str, Any]]:
    normalized = normalize_text(query)
    for token, idx in ORDINAL_TOKENS.items():
        if re.search(rf"(?<!\w){re.escape(token)}(?!\w)", normalized):
            recs = st.session_state.current_recommendations
            if 0 <= idx < len(recs):
                return recs[idx]
    return None


def infer_products_from_text(text: str, products: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    normalized = normalize_text(text)
    found: List[Dict[str, Any]] = []
    for product in products:
        name = normalize_text(product.get("name", ""))
        if name and name in normalized:
            found.append(product)
    return found


def filter_products(products: List[Dict[str, Any]], query: str) -> List[Dict[str, Any]]:
    normalized = normalize_text(query)
    if not normalized:
        return products

    filtered = []
    for product in products:
        name = normalize_text(product.get("name", ""))
        brand = normalize_text(product.get("brand", ""))
        category = normalize_text(product.get("category", ""))
        if normalized in name or normalized in brand or normalized in category:
            filtered.append(product)
    return filtered


def build_cart_summary() -> str:
    cart = st.session_state.cart
    if not cart:
        return "Your cart is empty."

    total = 0.0
    lines = ["Here is your cart:"]
    for item in cart:
        product = item.get("product", {})
        quantity = item.get("quantity", 1)
        price = float(product.get("price_value") or 0.0)
        subtotal = price * quantity
        total += subtotal
        lines.append(f"- {product.get('name', 'Unknown')} x{quantity} @ ₹{price:,.2f} = ₹{subtotal:,.2f}")
    lines.append(f"Total: ₹{total:,.2f}")
    return "\n".join(lines)


def build_checkout_message() -> str:
    if not st.session_state.cart:
        return "Your cart is empty. Add a product before checkout."

    total = 0.0
    for item in st.session_state.cart:
        product = item.get("product", {})
        quantity = item.get("quantity", 1)
        price = float(product.get("price_value") or 0.0)
        total += price * quantity
    st.session_state.cart = []
    return f"Your order is confirmed. Total payment is ₹{total:,.2f}. Thank you for shopping with ShopEase Copilot!"


def build_recommendation_message(recs: List[Dict[str, Any]], category: Optional[str], budget: Optional[float]) -> str:
    if not recs:
        if category:
            return f"I couldn't find any {category.lower()} matching that budget. Try a different request."
        return "I couldn't find any matching products. Can you try another request?"

    header = f"Here are the top {len(recs)} products"
    if category:
        header += f" for {category.lower()}"
    if budget:
        header += f" under ₹{budget:.2f}"
    header += ":"

    lines = [header]
    for index, product in enumerate(recs, start=1):
        price_display = product.get("price")
        rating = product.get("rating")
        review_count = product.get("reviewCount", 0)
        lines.append(
            f"{index}. {product.get('name', 'Unknown')} by {product.get('brand', 'Unknown')} — {price_display}, rating {rating or 'N/A'}, {review_count} reviews"
        )
    lines.append("You can ask me to add one of these to your cart, compare products, or request more details.")
    return "\n".join(lines)


def get_product_detail_message(product: Dict[str, Any]) -> str:
    price_display = product.get("price")
    rating = product.get("rating")
    reviews = product.get("reviewCount", 0)
    return (
        f"Here are the details for {product.get('name', 'Unknown')}:\n"
        f"- Brand: {product.get('brand', 'Unknown')}\n"
        f"- Category: {product.get('category', 'Unknown')}\n"
        f"- Price: {price_display}\n"
        f"- Rating: {rating or 'N/A'}\n"
        f"- Reviews: {reviews}\n"
        f"- Description: {product.get('description', 'No description available.')}."
    )


def get_compare_message(product_a: Optional[Dict[str, Any]], product_b: Optional[Dict[str, Any]]) -> str:
    if not product_a or not product_b:
        return "I couldn't compare those products. Please try a more specific comparison request."

    price_a = float(product_a.get("price_value") or 0.0)
    price_b = float(product_b.get("price_value") or 0.0)
    rating_a = float(product_a.get("rating") or 0.0)
    rating_b = float(product_b.get("rating") or 0.0)

    lines = [
        f"Comparing {product_a.get('name', 'Product A')} and {product_b.get('name', 'Product B')}:",
        f"- {product_a.get('name', 'Product A')}: {product_a.get('price')}, rating {rating_a}, {product_a.get('reviewCount', 0)} reviews",
        f"- {product_b.get('name', 'Product B')}: {product_b.get('price')}, rating {rating_b}, {product_b.get('reviewCount', 0)} reviews",
    ]
    if rating_a > rating_b:
        lines.append(f"I recommend {product_a.get('name')} for a stronger overall rating.")
    elif rating_b > rating_a:
        lines.append(f"I recommend {product_b.get('name')} for a stronger overall rating.")
    else:
        lines.append("Both products have similar ratings, so choose based on price or style preferences.")
    return "\n".join(lines)


def process_user_query(user_message: str, products: List[Dict[str, Any]]) -> str:
    text = normalize_text(user_message)
    if not text:
        return "Please type a message so I can help you shop."

    if contains_any(text, CHECKOUT_KEYWORDS):
        return build_checkout_message()

    if contains_any(text, REMOVE_KEYWORDS):
        product_query = text
        for keyword in REMOVE_KEYWORDS:
            product_query = product_query.replace(keyword, "")
        product_query = product_query.replace("from cart", "").strip()
        if not product_query:
            return "Please tell me which product to remove from your cart."
        cart_products = [item["product"] for item in st.session_state.cart]
        product = find_product_by_name(product_query, cart_products)
        if not product:
            return "I couldn't find that product in your cart. Please try using the full product name."
        remove_from_cart(product.get("id", ""))
        return f"{product.get('name')} has been removed from your cart."

    if contains_any(text, ADD_KEYWORDS):
        recommendation = find_recommendation_by_index(text)
        if recommendation:
            add_to_cart(recommendation)
            st.session_state.selected_product = recommendation
            return f"{recommendation.get('name')} has been added to your cart."

        cleaned = text
        for keyword in ADD_KEYWORDS:
            cleaned = cleaned.replace(keyword, "")
        cleaned = cleaned.replace("to cart", "").strip()
        product = find_product_by_name(cleaned, products)
        if product:
            add_to_cart(product)
            st.session_state.selected_product = product
            return f"{product.get('name')} has been added to your cart."

        if "this" in text and st.session_state.selected_product:
            selected = st.session_state.selected_product
            add_to_cart(selected)
            return f"{selected.get('name')} has been added to your cart."

    if ("cart" in text or "card" in text or "కార్ట్" in text or "कार्ट" in text):
        recommendation = find_recommendation_by_index(text)
        if recommendation:
            add_to_cart(recommendation)
            st.session_state.selected_product = recommendation
            return f"{recommendation.get('name')} has been added to your cart."

    if contains_any(text, SHOW_CART_KEYWORDS):
        return build_cart_summary()

    category, budget = parse_recommendation_request(text)
    if contains_any(text, COMPARE_KEYWORDS) and category:
        recs = recommend_products(products, category, budget, limit=3)
        if len(recs) >= 2:
            return get_compare_message(recs[0], recs[1])
        if recs:
            return build_recommendation_message(recs, category, budget)
        return f"I couldn't find enough products in {category} to compare."

    if category or budget:
        recs = recommend_products(products, category, budget, limit=3)
        if recs:
            st.session_state.current_recommendations = recs
            st.session_state.selected_product = recs[0]
            return build_recommendation_message(recs, category, budget)
        return "I couldn't find matching products. Try a different category or price range."

    if contains_any(text, {"show", "display", "list", "show me", "చూపించు", "दिखाओ"}) and category:
        recs = [p for p in products if normalize_text(p.get("category", "")) == normalize_text(category)]
        if recs:
            st.session_state.current_recommendations = recs[:5]
            return build_recommendation_message(recs[:5], category, None)

    if contains_any(text, {"best", "top", "top 3", "top 5", "naku", "kavali", "चाहिए", "चाहिए"}):
        recs = recommend_products(products, category, budget, limit=3)
        if recs:
            st.session_state.current_recommendations = recs
            st.session_state.selected_product = recs[0]
            return build_recommendation_message(recs, category, budget)

    if contains_any(text, DETAIL_KEYWORDS):
        recommendation = find_recommendation_by_index(text)
        if recommendation:
            st.session_state.selected_product = recommendation
            return get_product_detail_message(recommendation)
        product = find_product_by_name(text, products)
        if product:
            return get_product_detail_message(product)
        return "Please tell me which product you want details for, like a product name or the first recommendation."

    if contains_any(text, COMPARE_KEYWORDS):
        found = infer_products_from_text(text, products)
        if len(found) >= 2:
            return get_compare_message(found[0], found[1])
        return "Please tell me which two products to compare, for example compare first and second from the same category."

    product = find_product_by_name(text, products)
    if product:
        return get_product_detail_message(product)

    return "I can help you find products, compare them, add or remove items from your cart, show your cart, or checkout. Try asking for a category like 'best earbuds' or 'compare smartwatches'."


def render_header() -> None:
    st.markdown("<div class='hero-card'>", unsafe_allow_html=True)
    st.markdown("<div class='hero-pill'>ShopEase AI</div>", unsafe_allow_html=True)
    st.markdown("<h1 class='page-title'>ShopEase Copilot</h1>", unsafe_allow_html=True)
    st.markdown(
        "<p class='page-subtitle'>A modern shopping experience with an embedded AI assistant for easy recommendations, comparisons, and cart support.</p>",
        unsafe_allow_html=True,
    )
    st.markdown("</div>", unsafe_allow_html=True)

    with st.container():
        st.markdown("<div class='search-header'>", unsafe_allow_html=True)
        st.markdown("<div><h2>Search the catalog</h2></div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        st.text_input(
            "Search products, brands, or categories",
            key="search_query",
            placeholder="Search for earbuds, smartwatches, PulseTrack Pro...",
            label_visibility="collapsed",
        )


def render_cart(products: List[Dict[str, Any]]) -> None:
    st.sidebar.markdown("<div class='sidebar-card'>", unsafe_allow_html=True)
    st.sidebar.markdown("<div class='sidebar-title'>Cart Sidebar</div>", unsafe_allow_html=True)
    cart = st.session_state.cart
    if not cart:
        st.sidebar.info("Your cart is empty.")
    else:
        total = 0.0
        for item in cart:
            product = item.get("product", {})
            quantity = item.get("quantity", 1)
            price = float(product.get("price_value") or 0.0)
            subtotal = quantity * price
            total += subtotal
            st.sidebar.markdown(
                f"<div class='cart-item'><strong>{product.get('name')}</strong><br/>Qty: {quantity} · ₹{price:,.2f} each<br/>Subtotal: ₹{subtotal:,.2f}</div>",
                unsafe_allow_html=True,
            )
            if st.sidebar.button("Remove", key=f"sidebar_remove_{product.get('id')}"):
                remove_from_cart(product.get('id', ""))
                st.session_state.chat_history.append({"role": "assistant", "text": f"{product.get('name')} has been removed from your cart."})
        st.sidebar.markdown(f"<div class='cart-total'>Total: ₹{total:,.2f}</div>", unsafe_allow_html=True)

    if st.sidebar.button("Checkout", key="sidebar_checkout"):
        response = build_checkout_message()
        st.session_state.chat_history.append({"role": "user", "text": "Checkout"})
        st.session_state.chat_history.append({"role": "assistant", "text": response})
        # st.rerun() removed as per the patch requirement

    st.sidebar.markdown("</div>", unsafe_allow_html=True)


def render_product_catalog(products: List[Dict[str, Any]]) -> None:
    filtered_products = filter_products(products, st.session_state.search_query)
    st.markdown("## Product Catalog")
    if filtered_products:
        st.markdown(f"### Showing {len(filtered_products)} products")
    else:
        st.warning("No products found. Try a different search term.")

    columns = st.columns(3, gap="large")
    for index, product in enumerate(filtered_products):
        column = columns[index % 3]
        with column:
            image_url = get_product_image(product)
            st.markdown("<div class='shop-card'>", unsafe_allow_html=True)
            st.image(image_url, width="stretch")
            st.markdown(
                f"<div class='product-title'>{product.get('name')}</div>",
                unsafe_allow_html=True,
            )
            st.markdown(
                f"<div class='product-meta'>{product.get('brand')} · {product.get('category')}</div>",
                unsafe_allow_html=True,
            )
            st.markdown(
                f"<div class='product-price'>{product.get('price')}</div>",
                unsafe_allow_html=True,
            )
            st.markdown(
                f"<div class='product-meta'>Rating: {product.get('rating')} · {product.get('reviewCount')} reviews</div>",
                unsafe_allow_html=True,
            )
            st.write(product.get("description", "No description available."))
            if st.button("Add To Cart", key=f"catalog_add_{product.get('id')}"):
                add_to_cart_by_id(product.get("id"))
            st.markdown("</div>", unsafe_allow_html=True)


def render_ai_popup(products: List[Dict[str, Any]]) -> None:
    handle_voice_query(products)

    st.sidebar.markdown("<div class='sidebar-card'>", unsafe_allow_html=True)
    st.sidebar.markdown("<div class='sidebar-title'>ShopEase AI Assistant</div>", unsafe_allow_html=True)

    if st.session_state.get("chat_history"):
        for message in st.session_state.chat_history:
            role = message.get("role", "assistant")
            text = message.get("text", "")
            if role == "user":
                st.sidebar.markdown(f"<div class='chat-bubble user'>{text}</div>", unsafe_allow_html=True)
            else:
                st.sidebar.markdown(f"<div class='chat-bubble assistant'>{text}</div>", unsafe_allow_html=True)
    else:
        st.sidebar.markdown(
            "<div class='chat-bubble assistant'>Hi — ask me for product recommendations (e.g. 'best earbuds under 100').</div>",
            unsafe_allow_html=True,
        )

    if st.session_state.get("voice_listening"):
        st.session_state.voice_status = "listening"
    elif st.session_state.get("last_spoken_response") and st.session_state.get("auto_listening_enabled"):
        st.session_state.voice_status = "speaking"

    status_key = st.session_state.get("voice_status", "ready")
    status_label = VOICE_STATUS_LABELS.get(status_key, VOICE_STATUS_LABELS["ready"])
    language_name = VOICE_LANGUAGE_NAMES.get(st.session_state.get("current_language", "en-IN"), "English")
    st.sidebar.markdown(
        f"<div id='voice-status' class='voice-status'>{status_label} · {language_name}</div>",
        unsafe_allow_html=True,
    )

    if st.session_state.get("voice_error_message"):
        voice_error = html.escape(st.session_state.voice_error_message)
        st.sidebar.markdown(
            f"<div class='voice-error'>{voice_error}</div>",
            unsafe_allow_html=True,
        )

    if st.session_state.get("last_voice_transcript"):
        voice_transcript = html.escape(st.session_state.last_voice_transcript)
        st.sidebar.markdown(
            f"<div class='voice-transcript'>✅ You said:<br/>\"{voice_transcript}\"</div>",
            unsafe_allow_html=True,
        )

    with st.sidebar.container(key="assistant_input_row"):
        col1, col2 = st.columns([9, 1])
        with col1:
            st.text_input(
                "Your message",
                key="ai_input",
                placeholder="Type your message here...",
                label_visibility="collapsed",
                on_change=submit_typed_assistant_query,
                args=(products,),
            )
        with col2:
            mic_clicked = st.button("🎤", key="assistant_mic_button", help="Speak your request")

    if mic_clicked:
        st.session_state.voice_listening = True
        st.session_state.conversation_mode = True
        st.session_state.auto_listening_enabled = True
        st.session_state.current_language = "en-IN"
        st.session_state.voice_language_probe_index = 0
        st.session_state.voice_status = "listening"
        st.session_state.voice_request_id += 1
        st.session_state.voice_error_message = ""
        st.session_state.last_voice_transcript = ""
        st.rerun()

    render_voice_recognition_bridge()
    render_speech_synthesis_bridge()

    st.sidebar.markdown("</div>", unsafe_allow_html=True)


def main() -> None:
    st.set_page_config(page_title=APP_TITLE, layout="wide")
    render_page_style()
    initialize_session_state()

    render_header()
    products = load_products()
    render_ai_popup(products)
    render_cart(products)
    render_product_catalog(products)


if __name__ == "__main__":
    main()

