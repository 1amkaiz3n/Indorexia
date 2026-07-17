import json
import httpx
from app.config import get_settings
from .base import AIProvider, AIProviderError

TIMEOUT = 60.0
MODEL = "gemini-2.0-flash"


class GeminiProvider(AIProvider):
    name = "Gemini"

    async def generate(self, system_prompt: str, user_prompt: str) -> str:
        settings = get_settings()
        if not settings.gemini_api_key:
            raise AIProviderError("GEMINI_API_KEY tidak dikonfigurasi")

        url = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent?key={settings.gemini_api_key}"

        payload = {
            "contents": [{
                "role": "user",
                "parts": [{"text": f"{system_prompt}\n\n{user_prompt}"}]
            }],
            "generationConfig": {
                "temperature": 0.15,
                "maxOutputTokens": 4096,
            },
        }

        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            try:
                resp = await client.post(url, json=payload)
            except httpx.TimeoutException:
                raise AIProviderError("Timeout")
            except httpx.NetworkError as e:
                raise AIProviderError(f"Network error: {e}")

        if resp.status_code == 429:
            raise AIProviderError("Rate limited (429)", status_code=429)
        if resp.status_code in (500, 502, 503, 504):
            raise AIProviderError(f"Server error ({resp.status_code})", status_code=resp.status_code)
        if resp.status_code != 200:
            raise AIProviderError(f"HTTP {resp.status_code}: {resp.text[:200]}", status_code=resp.status_code)

        try:
            data = resp.json()
        except json.JSONDecodeError as e:
            raise AIProviderError(f"Invalid JSON response: {e}")

        candidates = data.get("candidates", [])
        if not candidates:
            block_reason = data.get("promptFeedback", {}).get("blockReason", "unknown")
            raise AIProviderError(f"No candidates returned (blockReason={block_reason})")

        parts = candidates[0].get("content", {}).get("parts", [])
        text = "".join(p.get("text", "") for p in parts).strip()
        if not text:
            finish = candidates[0].get("finishReason", "?")
            raise AIProviderError(f"Empty response (finishReason={finish})")

        return text
