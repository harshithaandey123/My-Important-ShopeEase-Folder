"""
Voice functions for ShopEase Copilot (STABLE VERSION - MAC FIXED)
"""

import re
from typing import Optional, Tuple, Dict, Any, List
import pyttsx3
import speech_recognition as sr


class VoiceProcessor:
    def __init__(self):
        self.recognizer = sr.Recognizer()

        # 🔥 FIX: reduce sensitivity issues
        self.recognizer.energy_threshold = 2500
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.pause_threshold = 0.8

        self.tts_engine = pyttsx3.init()
        self.tts_engine.setProperty("rate", 155)
        self.tts_engine.setProperty("volume", 0.9)

    def listen_for_command(
        self,
        language: str = "en-IN",
        timeout: int = 5,
        phrase_time_limit: int = 8,
        retries: int = 2
    ) -> Optional[str]:

        for _ in range(retries):
            try:
                with sr.Microphone() as source:
                    # 🔥 IMPORTANT FIX: faster calibration
                    self.recognizer.adjust_for_ambient_noise(source, duration=0.3)

                    print("🎤 Listening...")
                    audio = self.recognizer.listen(
                        source,
                        timeout=timeout,
                        phrase_time_limit=phrase_time_limit
                    )

                text = self.recognizer.recognize_google(audio, language=language)
                return text

            except sr.WaitTimeoutError:
                print("⚠️ No speech detected, retrying...")
                continue

            except sr.UnknownValueError:
                print("⚠️ Could not understand audio")
                return None

            except Exception as e:
                print("Microphone error:", str(e))
                return None

        return None

    def speak_text(self, text: str) -> None:
        try:
            text = re.sub(r"🔊", "", text)
            self.tts_engine.say(text)
            self.tts_engine.runAndWait()
        except Exception:
            pass

    @staticmethod
    def process_voice_command(text: str) -> Tuple[str, Dict[str, Any]]:
        text_lower = text.lower().strip()

        if any(k in text_lower for k in ["top", "best", "show top"]):
            return ("show_top", {"limit": 3})

        if any(k in text_lower for k in ["add", "cart", "pettu"]):
            if "first" in text_lower or "1" in text_lower:
                return ("add_to_cart_by_index", {"index": 0})
            if "second" in text_lower or "2" in text_lower:
                return ("add_to_cart_by_index", {"index": 1})
            if "third" in text_lower or "3" in text_lower:
                return ("add_to_cart_by_index", {"index": 2})

            product_name = re.sub(r"(add|cart|to)", "", text_lower).strip()
            return ("add_to_cart", {"product_name": product_name})

        if "cart" in text_lower:
            return ("show_cart", {})

        if any(k in text_lower for k in ["checkout", "buy"]):
            return ("checkout", {})

        return ("search_product", {"product_name": text_lower})


def get_language_code(language: str) -> str:
    return {
        "English": "en-IN",
        "Telugu": "te-IN",
        "Hindi": "hi-IN"
    }.get(language, "en-IN")


def initialize_voice_processor():
    return VoiceProcessor()