from __future__ import annotations

import re
from dataclasses import dataclass, field

from cart_manager import add_product, add_products, cart_count, order_summary, remove_by_index
from product_service import category_from_text, find_product, product_line, recommend_products


ORDINALS = {
    "first": 0,
    "1st": 0,
    "one": 0,
    "second": 1,
    "2nd": 1,
    "two": 1,
    "third": 2,
    "3rd": 2,
    "three": 2,
    "fourth": 3,
    "4th": 3,
    "four": 3,
    "fifth": 4,
    "5th": 4,
    "five": 4,
}


@dataclass
class IntentResult:
    intent: str
    response: str
    products: list[dict] = field(default_factory=list)
    show_cart: bool = False
    checkout: bool = False
    matched_product: dict | None = None


def _extract_limit(text: str, default: int = 3) -> int:
    match = re.search(r"\btop\s+(\d+)|\b(\d+)\s+(?:best|top|products|items)", text)
    if match:
        return max(1, min(int(match.group(1) or match.group(2)), 8))
    for word, index in ORDINALS.items():
        if f"top {word}" in text:
            return index + 1
    return default


def _extract_price(text: str) -> int | None:
    match = re.search(r"(?:under|below|less than|within|upto|up to)\s*(?:rs\.?|inr|rupees|₹)?\s*([0-9,]+)", text)
    if not match:
        return None
    return int(match.group(1).replace(",", ""))


def _extract_index(text: str) -> int | None:
    for word, index in ORDINALS.items():
        if re.search(rf"\b{re.escape(word)}\b", text):
            return index
    match = re.search(r"#\s*(\d+)|product\s+(\d+)|item\s+(\d+)", text)
    if match:
        value = next(group for group in match.groups() if group)
        return int(value) - 1
    return None


def _score_intents(text: str) -> dict[str, int]:
    scores = {
        "SHOW_TOP_PRODUCTS": 0,
        "ADD_ALL_RECOMMENDED_PRODUCTS": 0,
        "ADD_PRODUCT_BY_INDEX": 0,
        "ADD_PRODUCT_BY_NAME": 0,
        "SHOW_CART": 0,
        "REMOVE_CART_ITEM": 0,
        "CHECKOUT": 0,
        "ASK_BEST_FROM_CONTEXT": 0,
        "HELP": 0,
    }

    words = set(re.findall(r"[a-z0-9]+", text))
    if words & {"show", "find", "recommend", "suggest", "list", "best", "top"}:
        scores["SHOW_TOP_PRODUCTS"] += 2
    if words & {"earbuds", "buds", "headphones", "headset", "watch", "smartwatch", "powerbank", "power"}:
        scores["SHOW_TOP_PRODUCTS"] += 2
    if words & {"under", "below", "within"}:
        scores["SHOW_TOP_PRODUCTS"] += 1
    if words & {"add", "put", "move"}:
        scores["ADD_PRODUCT_BY_NAME"] += 2
        scores["ADD_PRODUCT_BY_INDEX"] += 1
    if "all" in words and words & {"add", "put"}:
        scores["ADD_ALL_RECOMMENDED_PRODUCTS"] += 5
    if _extract_index(text) is not None and words & {"add", "put"}:
        scores["ADD_PRODUCT_BY_INDEX"] += 4
    if words & {"it", "this"} and words & {"add", "put"}:
        scores["ADD_PRODUCT_BY_INDEX"] += 3
    if "cart" in words and words & {"show", "view", "display", "open"}:
        scores["SHOW_CART"] += 5
    if words & {"remove", "delete", "drop"}:
        scores["REMOVE_CART_ITEM"] += 4
    if words & {"checkout", "buy", "purchase", "order"}:
        scores["CHECKOUT"] += 5
    if ("highest" in words or "best" in words) and ("rating" in words or "rated" in words):
        scores["ASK_BEST_FROM_CONTEXT"] += 5
    if words & {"help", "examples"}:
        scores["HELP"] += 4
    return scores


def classify_intent(text: str) -> str:
    scores = _score_intents(text)
    return max(scores, key=scores.get) if max(scores.values()) > 0 else "UNKNOWN"


def handle_message(text: str, products: list[dict], session_state) -> IntentResult:
    cleaned = text.strip().lower()
    intent = classify_intent(cleaned)

    if intent == "SHOW_TOP_PRODUCTS":
        category = category_from_text(cleaned)
        limit = _extract_limit(cleaned)
        max_price = _extract_price(cleaned)
        recommendations = recommend_products(products, category=category, limit=limit, max_price=max_price)
        session_state.last_recommendations = recommendations
        session_state.last_selected_product = recommendations[0] if recommendations else None
        if not recommendations:
            return IntentResult(intent, "I could not find matching products for that filter.")
        label = category or "products"
        price_text = f" under Rs. {max_price:,}" if max_price else ""
        return IntentResult(intent, f"Here are the top {len(recommendations)} {label}{price_text}.", recommendations)

    if intent == "ADD_ALL_RECOMMENDED_PRODUCTS":
        recommendations = session_state.get("last_recommendations", [])
        if not recommendations:
            return IntentResult(intent, "I do not have a recent recommendation list yet. Ask me to show products first.")
        add_products(session_state, recommendations)
        return IntentResult(intent, f"Added all {len(recommendations)} recommended products to your cart. Your cart now contains {cart_count(session_state)} items.")

    if intent in {"ADD_PRODUCT_BY_INDEX", "ADD_PRODUCT_BY_NAME"}:
        target = None
        index = _extract_index(cleaned)
        recommendations = session_state.get("last_recommendations", [])
        if "it" in cleaned or "this" in cleaned:
            target = session_state.get("last_selected_product")
        if target is None and index is not None and recommendations and 0 <= index < len(recommendations):
            target = recommendations[index]
        if target is None:
            target = find_product(cleaned, products)
        if target is None:
            return IntentResult(intent, "I could not confidently match that product. Try saying the product name or its recommendation number.")
        add_product(session_state, target)
        session_state.last_selected_product = target
        return IntentResult(intent, f"Added {target['name']} to your cart. Your cart now contains {cart_count(session_state)} items.", matched_product=target)

    if intent == "SHOW_CART":
        count = cart_count(session_state)
        message = "Your cart is empty." if count == 0 else f"Your cart contains {count} item{'s' if count != 1 else ''}."
        return IntentResult(intent, message, show_cart=True)

    if intent == "REMOVE_CART_ITEM":
        index = _extract_index(cleaned)
        if index is None:
            index = 0
        removed = remove_by_index(session_state, index)
        if not removed:
            return IntentResult(intent, "I could not remove that item because it is not in your cart.")
        return IntentResult(intent, f"Removed {removed['product']['name']} from your cart. Your cart now contains {cart_count(session_state)} items.", show_cart=True)

    if intent == "CHECKOUT":
        return IntentResult(intent, order_summary(session_state), checkout=True, show_cart=True)

    if intent == "ASK_BEST_FROM_CONTEXT":
        recommendations = session_state.get("last_recommendations", [])
        if not recommendations:
            best = recommend_products(products, limit=1)[0]
            session_state.last_selected_product = best
            return IntentResult(intent, f"The highest rated product overall is {product_line(best)}.", [best])
        best = max(recommendations, key=lambda product: product["rating"])
        session_state.last_selected_product = best
        return IntentResult(intent, f"From the latest recommendations, the best rated product is {product_line(best)}.", [best])

    if intent == "HELP":
        return IntentResult(intent, "Try: show top 3 earbuds, show best earbuds under 2000, add the first one, add all, remove the first item, show cart, or checkout.")

    matched = find_product(cleaned, products)
    if matched:
        session_state.last_recommendations = [matched]
        session_state.last_selected_product = matched
        return IntentResult("PRODUCT_DETAIL", f"I found {product_line(matched)}. Say add it to cart if you want it.", [matched])

    return IntentResult("UNKNOWN", "I can help you compare products, add recommendations to cart, remove items, and checkout. Try asking for the best earbuds under 2000.")
