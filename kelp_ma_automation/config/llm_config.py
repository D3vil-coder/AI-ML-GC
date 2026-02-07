"""
LLM Configuration Module
Supports both Ollama (local) and Gemini (API) providers.
"""

import os
import logging
from typing import Optional, Dict, Any
from dataclasses import dataclass
from enum import Enum

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LLMProvider(Enum):
    OLLAMA = "ollama"
    GEMINI = "gemini"


@dataclass
class LLMConfig:
    """LLM configuration."""
    provider: LLMProvider
    model: str
    api_key: Optional[str] = None
    temperature: float = 0.3
    max_tokens: int = 500


# Default models for each provider
OLLAMA_MODELS = [
    "phi4-mini:latest",
    "llama3.2:latest",
    "qwen2.5:latest",
    "mistral:latest",
]

GEMINI_MODELS = [
    "gemini-2.0-flash",
    "gemini-1.5-pro",
    "gemma-27b-it",
]


class LLMClient:
    """
    Unified LLM client supporting Ollama and Gemini.
    """
    
    def __init__(self, config: LLMConfig):
        self.config = config
        self._client = None
        self._init_client()
    
    def _init_client(self):
        """Initialize the appropriate client."""
        if self.config.provider == LLMProvider.OLLAMA:
            self._init_ollama()
        elif self.config.provider == LLMProvider.GEMINI:
            self._init_gemini()
    
    def _init_ollama(self):
        """Initialize Ollama client."""
        try:
            import ollama
            self._client = ollama.Client()
            logger.info(f"Ollama client initialized with model: {self.config.model}")
        except ImportError:
            logger.error("Ollama package not installed. Run: pip install ollama")
            raise
    
    def _init_gemini(self):
        """Initialize Gemini client."""
        if not self.config.api_key:
            raise ValueError("Gemini API key is required")
        
        try:
            import google.generativeai as genai
            genai.configure(api_key=self.config.api_key)
            self._client = genai.GenerativeModel(self.config.model)
            logger.info(f"Gemini client initialized with model: {self.config.model}")
        except ImportError:
            logger.error("Google Generative AI package not installed. Run: pip install google-generativeai")
            raise
    
    def generate(self, prompt: str, max_tokens: Optional[int] = None) -> str:
        """Generate text using configured LLM."""
        max_tokens = max_tokens or self.config.max_tokens
        
        if self.config.provider == LLMProvider.OLLAMA:
            return self._generate_ollama(prompt, max_tokens)
        elif self.config.provider == LLMProvider.GEMINI:
            return self._generate_gemini(prompt, max_tokens)
    
    def _generate_ollama(self, prompt: str, max_tokens: int) -> str:
        """Generate with Ollama."""
        try:
            response = self._client.generate(
                model=self.config.model,
                prompt=prompt,
                options={
                    "temperature": self.config.temperature,
                    "num_predict": max_tokens
                }
            )
            return response.get('response', '')
        except Exception as e:
            logger.error(f"Ollama generation error: {e}")
            return ""
    
    def _generate_gemini(self, prompt: str, max_tokens: int) -> str:
        """Generate with Gemini."""
        try:
            response = self._client.generate_content(
                prompt,
                generation_config={
                    "temperature": self.config.temperature,
                    "max_output_tokens": max_tokens,
                }
            )
            return response.text
        except Exception as e:
            logger.error(f"Gemini generation error: {e}")
            return ""
    
    def is_available(self) -> bool:
        """Check if the LLM is available."""
        try:
            test = self.generate("Say 'ok'", max_tokens=10)
            return len(test) > 0
        except:
            return False


def create_llm_client(
    provider: str = "ollama",
    model: str = None,
    api_key: str = None,
    temperature: float = 0.3
) -> LLMClient:
    """Factory function to create LLM client."""
    
    provider_enum = LLMProvider(provider.lower())
    
    # Default model based on provider
    if model is None:
        model = OLLAMA_MODELS[0] if provider_enum == LLMProvider.OLLAMA else GEMINI_MODELS[0]
    
    config = LLMConfig(
        provider=provider_enum,
        model=model,
        api_key=api_key,
        temperature=temperature
    )
    
    return LLMClient(config)


if __name__ == "__main__":
    # Test Ollama
    print("Testing Ollama...")
    try:
        client = create_llm_client(provider="ollama", model="phi4-mini:latest")
        if client.is_available():
            print("✓ Ollama is available")
        else:
            print("✗ Ollama not responding")
    except Exception as e:
        print(f"✗ Ollama error: {e}")
    
    # Test Gemini (requires API key)
    api_key = os.getenv("GEMINI_API_KEY")
    if api_key:
        print("Testing Gemini...")
        try:
            client = create_llm_client(provider="gemini", api_key=api_key)
            if client.is_available():
                print("✓ Gemini is available")
            else:
                print("✗ Gemini not responding")
        except Exception as e:
            print(f"✗ Gemini error: {e}")
    else:
        print("⚠ GEMINI_API_KEY not set, skipping Gemini test")
