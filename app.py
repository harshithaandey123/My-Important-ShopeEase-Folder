import streamlit as st

from cart_manager import cart_count, cart_total, clear_cart
from intent_engine import handle_message
from product_service import get_products
from ui_components import (
    inject_styles,
    render_cart_sidebar,
    render_chat_history,
    render_header,
    render_product_grid,
)
from voice import render_voice_controls, speak


st.set_page_config(page_title="ShopEase Copilot", page_icon="SC", layout="wide")


def init_state() -> None:
    defaults = {
        "cart": [],
        "messages": [
            {
                "role": "assistant",
                "content": "Hi, I am ShopEase Copilot. Ask for products naturally, like: show top 3 earbuds, show best earbuds under 2000, add the first one, or checkout.",
            }
        ],
        "last_recommendations": [],
        "last_selected_product": None,
        "last_result_products": [],
        "last_spoken_text": "",
        "chat_input_text": "",
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def submit_message(message: str, products: list[dict]) -> None:
    clean_message = message.strip()
    if not clean_message:
        return

    st.session_state.messages.append({"role": "user", "content": clean_message})
    result = handle_message(clean_message, products, st.session_state)
    st.session_state.last_result_products = result.products
    st.session_state.messages.append({"role": "assistant", "content": result.response})
    st.session_state.last_spoken_text = result.response


def render_quick_actions(products: list[dict]) -> None:
    cols = st.columns(4)
    actions = [
        "Show top 3 earbuds",
        "Show best earbuds under 2000",
        "Which product has highest rating?",
        "Show cart",
    ]
    for col, action in zip(cols, actions):
        with col:
            if st.button(action, use_container_width=True):
                submit_message(action, products)
                st.rerun()


def main() -> None:
    init_state()
    products = list(get_products())
    inject_styles()
    render_cart_sidebar(st.session_state)
    render_header(cart_count(st.session_state), cart_total(st.session_state))

    if st.sidebar.button("Clear cart", use_container_width=True):
        clear_cart(st.session_state)
        st.rerun()

    left, right = st.columns([1.3, 1], gap="large")

    with left:
        st.subheader("Conversation")
        st.markdown(
            '<div class="chat-hint">Use the microphone or type a message. Follow-ups like "add it", "add all", and "remove the first item" use conversation memory.</div>',
            unsafe_allow_html=True,
        )
        render_voice_controls("chat_input_text")
        render_chat_history(st.session_state.messages)

        with st.form("chat_form", clear_on_submit=True):
            user_text = st.text_input(
                "Message ShopEase Copilot",
                key="chat_input_text",
                placeholder="Ask for top earbuds, add the first one, show cart...",
            )
            submitted = st.form_submit_button("Send", use_container_width=True)

        if submitted:
            submit_message(user_text, products)
            st.rerun()

        render_quick_actions(products)

    with right:
        st.subheader("Recommendations")
        if st.session_state.last_result_products:
            render_product_grid(st.session_state.last_result_products, ranked=True)
        else:
            render_product_grid(products[:3], ranked=False)

    st.divider()
    st.subheader("Product Catalog")
    category = st.radio(
        "Browse category",
        ["All", "earbuds", "headphones", "smartwatch", "power bank"],
        horizontal=True,
    )
    visible_products = products if category == "All" else [product for product in products if product["category"] == category]
    render_product_grid(visible_products, ranked=False)

    if st.session_state.last_spoken_text:
        speak(st.session_state.last_spoken_text)
        st.session_state.last_spoken_text = ""


if __name__ == "__main__":
    main()
