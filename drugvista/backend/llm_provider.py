"""
Configurable LLM Provider Layer for DrugVista
Supports OpenAI-compatible endpoints with offline heuristic fallback.
"""
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
import logging
import config

logger = logging.getLogger(__name__)


class LLMProvider(ABC):
    @abstractmethod
    def generate(self, prompt: str, temperature: float = 0.3) -> Optional[str]:
        """Generate response text for the provided prompt"""
        pass

    @property
    @abstractmethod
    def is_online(self) -> bool:
        """True if backed by live LLM model inference"""
        pass


class OpenAIProvider(LLMProvider):
    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or config.OPENAI_API_KEY
        self.base_url = base_url or config.OPENAI_BASE_URL
        self.model = model or config.OPENAI_MODEL
        self._client = None
        self._init_client()

    def _init_client(self):
        if self._is_valid_api_key(self.api_key):
            try:
                import openai
                self._client = openai.OpenAI(
                    api_key=self.api_key,
                    base_url=self.base_url
                )
                logger.info(f"OpenAIProvider initialized with model '{self.model}' at {self.base_url}")
            except Exception as e:
                logger.warning(f"Failed to initialize OpenAI client: {e}")
                self._client = None
        else:
            logger.info("OpenAIProvider: No valid API key detected.")
            self._client = None

    @staticmethod
    def _is_valid_api_key(key: Optional[str]) -> bool:
        if not key:
            return False
        if key.startswith("dummy") or key == "your-api-key-here" or len(key) < 15:
            return False
        return True

    @property
    def is_online(self) -> bool:
        return self._client is not None

    def generate(self, prompt: str, temperature: float = 0.3) -> Optional[str]:
        if not self._client:
            return None
        try:
            response = self._client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.warning(f"OpenAI API call failed: {e}")
            return None


class OfflineRuleProvider(LLMProvider):
    """
    Offline heuristic provider used when no API key is supplied or when offline.
    """
    @property
    def is_online(self) -> bool:
        return False

    def generate(self, prompt: str, temperature: float = 0.3) -> Optional[str]:
        # Returns None to trigger domain-specific heuristic extraction
        return None


def get_llm_provider() -> LLMProvider:
    """Factory to retrieve appropriate LLM provider based on configuration"""
    provider = OpenAIProvider()
    if provider.is_online:
        return provider
    return OfflineRuleProvider()
