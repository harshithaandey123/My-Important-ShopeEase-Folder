from __future__ import annotations

import base64
import html

import streamlit as st

from cart_manager import cart_total


def inject_styles() -> None:
    st.markdown(
        """
        <style>
        :root {
          --ink:#0f172a;
          --muted:#64748b;
          --line:#e2e8f0;
          --soft:#f8fafc;
          --brand:#0f766e;
        }
        .block-container { padding-top: 1.4rem; max-width: 1240px; }
        h1, h2, h3 { letter-spacing: 0; }
        .app-header {
          display:flex;
          align-items:flex-start;
          justify-content:space-between;
          gap:24px;
          border-bottom:1px solid var(--line);
          padding-bottom:18px;
          margin-bottom:18px;
        }
        .app-title { font-size:34px; line-height:1.1; font-weight:800; color:var(--ink); margin:0; }
        .app-subtitle { color:var(--muted); margin-top:8px; font-size:15px; max-width:720px; }
        .metric-strip { display:flex; gap:10px; flex-wrap:wrap; justify-content:flex-end; }
        .metric-pill {
          border:1px solid var(--line);
          background:#fff;
          border-radius:8px;
          padding:9px 12px;
          min-width:98px;
        }
        .metric-label { color:var(--muted); font-size:12px; }
        .metric-value { color:var(--ink); font-size:18px; font-weight:800; }
        .product-card {
          border:1px solid var(--line);
          border-radius:8px;
          background:white;
          overflow:hidden;
          height:100%;
          box-shadow:0 10px 28px rgba(15,23,42,.06);
        }
        .product-card img { width:100%; height:150px; object-fit:cover; background:#f1f5f9; }
        .product-body { padding:14px; }
        .product-rank { color:var(--brand); font-size:12px; font-weight:800; text-transform:uppercase; }
        .product-name { color:var(--ink); font-size:16px; line-height:1.25; font-weight:800; margin-top:4px; min-height:40px; }
        .product-meta { color:var(--muted); font-size:13px; margin-top:5px; }
        .product-desc { color:#334155; font-size:13px; line-height:1.35; margin-top:8px; min-height:54px; }
        .price-row { display:flex; align-items:center; justify-content:space-between; gap:10px; margin-top:12px; }
        .price { color:var(--ink); font-size:18px; font-weight:900; }
        .rating { color:#92400e; background:#fef3c7; border-radius:8px; padding:4px 7px; font-size:13px; font-weight:800; }
        .chat-hint {
          border:1px solid var(--line);
          background:var(--soft);
          border-radius:8px;
          padding:10px 12px;
          color:#475569;
          font-size:14px;
          margin-bottom:10px;
        }
        .cart-card {
          border:1px solid var(--line);
          border-radius:8px;
          background:#fff;
          padding:10px;
          margin-bottom:8px;
        }
        .cart-name { font-weight:800; color:var(--ink); font-size:14px; }
        .cart-line { color:var(--muted); font-size:13px; margin-top:3px; }
        @media (max-width: 760px) {
          .app-header { display:block; }
          .metric-strip { justify-content:flex-start; margin-top:14px; }
          .app-title { font-size:28px; }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def _image_src(image: str) -> str:
    if image.strip().startswith("<svg"):
        encoded = html.escape(image)
        return f"data:image/svg+xml;utf8,{encoded}"
    with open(image, "rb") as handle:
        encoded = base64.b64encode(handle.read()).decode("ascii")
    return f"data:image/svg+xml;base64,{encoded}"


def render_header(cart_items: int, total: int) -> None:
    st.markdown(
        f"""
        <div class="app-header">
          <div>
            <div class="app-title">ShopEase Copilot</div>
            <div class="app-subtitle">A voice-first shopping assistant that remembers recommendations, understands follow-ups, and manages your cart conversationally.</div>
          </div>
          <div class="metric-strip">
            <div class="metric-pill"><div class="metric-label">Cart Items</div><div class="metric-value">{cart_items}</div></div>
            <div class="metric-pill"><div class="metric-label">Cart Total</div><div class="metric-value">Rs. {total:,}</div></div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_product_card(product: dict, rank: int | None = None) -> None:
    rank_text = f"Recommendation #{rank}" if rank else product["category"].title()
    st.markdown(
        f"""
        <div class="product-card">
          <img src="{_image_src(product['image'])}" alt="{html.escape(product['name'])}" />
          <div class="product-body">
            <div class="product-rank">{rank_text}</div>
            <div class="product-name">{html.escape(product['name'])}</div>
            <div class="product-meta">{html.escape(product['brand'])} · {html.escape(product['category'].title())}</div>
            <div class="product-desc">{html.escape(product['description'])}</div>
            <div class="price-row">
              <div class="price">Rs. {product['price']:,}</div>
              <div class="rating">{product['rating']:.1f} star</div>
            </div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_product_grid(products: list[dict], ranked: bool = False) -> None:
    if not products:
        return
    columns = st.columns(min(3, len(products)))
    for index, product in enumerate(products):
        with columns[index % len(columns)]:
            render_product_card(product, index + 1 if ranked else None)


def render_cart_sidebar(session_state) -> None:
    st.sidebar.header("Cart")
    if not session_state.cart:
        st.sidebar.info("Your cart is empty.")
        return

    for index, item in enumerate(session_state.cart, start=1):
        product = item["product"]
        quantity = item["quantity"]
        st.sidebar.markdown(
            f"""
            <div class="cart-card">
              <div class="cart-name">{index}. {html.escape(product['name'])}</div>
              <div class="cart-line">Qty {quantity} · Rs. {product['price'] * quantity:,}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    st.sidebar.markdown(f"**Total: Rs. {cart_total(session_state):,}**")


def render_chat_history(messages: list[dict]) -> None:
    for message in messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
