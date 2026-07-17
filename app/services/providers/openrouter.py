import json
import httpx
from app.config import get_settings
from .base import AIProvider, AIProviderError

TIMEOUT = 60.0
MODEL = "openai/gpt-4o-mini"


class OpenRouterProvider(AIProvider):
    name = "OpenRouter"

    async def generate(self, system_prompt: str, user_prompt: str) -> str:
        settings = get_settings()
        if not settings.openrouter_api_key:
            raise AIProviderError("OPENROUTER_API_KEY tidak dikonfigurasi")

        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            try:
                resp = await client.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {settings.openrouter_api_key}",
                        "Content-Type": "application/json",
                        "HTTP-Referer": "https://indorexia.app",
                        "X-Title": "Indorexia",
                    },
                    json={
                        "model": MODEL,
                        "messages": [
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_prompt},
                        ],
                        "temperature": 0.15,
                        "max_tokens": 4096,
                    },
                )
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

        content = data.get("choices", [{}])[0].get("message", {}).get("content", "").strip()
        if not content:
            finish = data.get("choices", [{}])[0].get("finish_reason", "?")
            raise AIProviderError(f"Empty response (finish_reason={finish})")

        return content
