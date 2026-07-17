"""AI Provider Manager — automatic fallback across multiple providers."""

import logging
from .providers.base import AIProvider, AIProviderError
from .providers.groq import GroqProvider
from .providers.gemini import GeminiProvider
from .providers.openrouter import OpenRouterProvider

logger = logging.getLogger(__name__)

_default_providers = [
    GeminiProvider(),
    GroqProvider(),
    OpenRouterProvider(),
]


class AIProviderManager:
    def __init__(self, providers: list[AIProvider] | None = None):
        self.providers = providers or _default_providers

    async def generate(self, system_prompt: str, user_prompt: str) -> str:
        last_error = None

        for provider in self.providers:
            logger.info("Mencoba %s...", provider.name)
            try:
                result = await provider.generate(system_prompt, user_prompt)
                logger.info("Sukses menggunakan: %s", provider.name)
                return result
            except AIProviderError as e:
                logger.warning("%s gagal (%s)", provider.name, e)
                last_error = e
            except Exception as e:
                logger.warning("%s gagal (unexpected error: %s)", provider.name, e)
                last_error = AIProviderError(str(e))

        msg = "Semua AI provider tidak tersedia.\n"
        if last_error:
            msg += f"Error terakhir: {last_error}"
        logger.error(msg)
        raise AIProviderError(msg)


manager = AIProviderManager()
