from __future__ import annotations


def ensure_cart(session_state) -> None:
    if "cart" not in session_state:
        session_state.cart = []


def add_product(session_state, product: dict, quantity: int = 1) -> None:
    ensure_cart(session_state)
    for item in session_state.cart:
        if item["product"]["id"] == product["id"]:
            item["quantity"] += quantity
            return
    session_state.cart.append({"product": product, "quantity": quantity})


def add_products(session_state, products: list[dict]) -> None:
    for product in products:
        add_product(session_state, product)


def remove_by_index(session_state, index: int) -> dict | None:
    ensure_cart(session_state)
    if 0 <= index < len(session_state.cart):
        return session_state.cart.pop(index)
    return None


def clear_cart(session_state) -> None:
    session_state.cart = []


def cart_total(session_state) -> int:
    ensure_cart(session_state)
    return sum(item["product"]["price"] * item["quantity"] for item in session_state.cart)


def cart_count(session_state) -> int:
    ensure_cart(session_state)
    return sum(item["quantity"] for item in session_state.cart)


def order_summary(session_state) -> str:
    ensure_cart(session_state)
    if not session_state.cart:
        return "Your cart is empty, so there is nothing to checkout yet."

    lines = ["Order summary:"]
    for item in session_state.cart:
        product = item["product"]
        qty = item["quantity"]
        lines.append(f"- {product['name']} x {qty}: Rs. {product['price'] * qty:,}")
    lines.append(f"Total: Rs. {cart_total(session_state):,}")
    return "\n".join(lines)
