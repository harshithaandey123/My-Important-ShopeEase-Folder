from __future__ import annotations

import html

import streamlit as st
import streamlit.components.v1 as components


def render_voice_controls(input_key: str = "chat_input_text") -> None:
    escaped_key = html.escape(input_key)
    components.html(
        f"""
        <div class="voice-shell">
          <button id="micButton" title="Start voice input">🎙️</button>
          <span id="voiceStatus">Click and speak</span>
        </div>
        <script>
        const button = document.getElementById("micButton");
        const status = document.getElementById("voiceStatus");
        const Recognition = window.SpeechRecognition || window.webkitSpeechRecognition;

        function findInput() {{
          const doc = window.parent.document;
          const direct = doc.querySelector('input[aria-label="Message ShopEase Copilot"]');
          if (direct) return direct;
          const inputs = Array.from(doc.querySelectorAll('input[type="text"]'));
          return inputs.find((input) => input.value === "" || input.placeholder.includes("Ask"));
        }}

        function setNativeValue(element, value) {{
          const prototype = Object.getPrototypeOf(element);
          const descriptor = Object.getOwnPropertyDescriptor(prototype, "value");
          descriptor.set.call(element, value);
          element.dispatchEvent(new Event("input", {{ bubbles: true }}));
          element.dispatchEvent(new Event("change", {{ bubbles: true }}));
          element.focus();
        }}

        if (!Recognition) {{
          button.disabled = true;
          status.textContent = "Speech recognition is not supported in this browser";
        }} else {{
          const recognition = new Recognition();
          recognition.lang = "en-US";
          recognition.interimResults = false;
          recognition.continuous = false;

          button.onclick = () => {{
            status.textContent = "Listening...";
            recognition.start();
          }};

          recognition.onresult = (event) => {{
            const transcript = event.results[0][0].transcript;
            const input = findInput();
            if (input) {{
              setNativeValue(input, transcript);
              status.textContent = "Captured: " + transcript;
            }} else {{
              status.textContent = "Could not find the chat input";
            }}
          }};

          recognition.onerror = (event) => {{
            status.textContent = "Voice error: " + event.error;
          }};

          recognition.onend = () => {{
            if (status.textContent === "Listening...") status.textContent = "Click and speak";
          }};
        }}
        </script>
        <style>
          .voice-shell {{
            display:flex;
            align-items:center;
            gap:10px;
            font-family:Inter, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
          }}
          #micButton {{
            width:44px;
            height:44px;
            border:0;
            border-radius:8px;
            cursor:pointer;
            color:white;
            background:#0f766e;
            font-size:22px;
            box-shadow:0 8px 20px rgba(15, 118, 110, .22);
          }}
          #micButton:disabled {{
            opacity:.45;
            cursor:not-allowed;
          }}
          #voiceStatus {{
            color:#334155;
            font-size:14px;
          }}
        </style>
        """,
        height=64,
    )


def speak(text: str) -> None:
    safe_text = html.escape(text).replace("\n", " ")
    components.html(
        f"""
        <script>
          const text = `{safe_text}`;
          if ("speechSynthesis" in window && text.trim()) {{
            window.speechSynthesis.cancel();
            const utterance = new SpeechSynthesisUtterance(text);
            utterance.lang = "en-US";
            utterance.rate = 1;
            utterance.pitch = 1;
            window.speechSynthesis.speak(utterance);
          }}
        </script>
        """,
        height=0,
    )
