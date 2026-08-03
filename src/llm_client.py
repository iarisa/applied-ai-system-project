"""
Gemini client wrapper used by the Agent.

Mirrors ai110-module4tinker-docubot-solution/llm_client.py: a thin wrapper
that reads GEMINI_API_KEY from the environment and exposes a single
generate() method, keeping the Agent decoupled from the Gemini SDK.
"""

import os
from google import genai

# Central place to update the model name if needed.
GEMINI_MODEL_NAME = "gemini-flash-lite-latest"


class GeminiClient:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise RuntimeError(
                "Missing GEMINI_API_KEY environment variable. "
                "Set it in your shell or .env file to enable the Agent."
            )
        self.client = genai.Client(api_key=api_key)

    def generate(self, prompt: str) -> str:
        try:
            response = self.client.models.generate_content(
                model=GEMINI_MODEL_NAME,
                contents=prompt,
            )
            return (response.text or "").strip()
        except Exception as e:
            return f"API error — could not generate answer. ({type(e).__name__}: {e})"
