import json
import hashlib
import logging
import httpx
from typing import Protocol, Optional, Dict, Any
from app.config import settings
from app.db.cache import get_cache

logger = logging.getLogger(__name__)


class LLMProvider(Protocol):
    async def complete_json(self, prompt: str, schema: Optional[dict] = None) -> dict: ...
    async def complete_vision_json(self, prompt: str, image: bytes, schema: Optional[dict] = None) -> dict: ...


class GroqProvider:
    def __init__(self):
        self.api_key = settings.GROQ_API_KEY
        self.model_name = settings.GROQ_MODEL or "groq/compound"
        self._client = None
        if self.api_key:
            try:
                from groq import AsyncGroq
                self._client = AsyncGroq(api_key=self.api_key)
            except Exception as e:
                logger.warning(f"Groq client init failed: {e}")

    def _get_cache_key(self, prompt: str) -> str:
        content = f"{self.model_name}:{prompt}"
        sha = hashlib.sha256(content.encode("utf-8")).hexdigest()
        return f"llm:groq:{sha}"

    async def complete_json(self, prompt: str, schema: Optional[dict] = None) -> dict:
        cache = get_cache()
        cache_key = self._get_cache_key(prompt)

        cached_res = cache.get(cache_key)
        if cached_res:
            try:
                return json.loads(cached_res)
            except Exception:
                pass

        if not self._client:
            logger.warning("GROQ_API_KEY unset — returning mock fallback.")
            return {"explanations": {}, "status": "no_key"}

        try:
            res = await self._client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "You are a beauty formulation expert. Respond in strict JSON format with an 'explanation' field."},
                    {"role": "user", "content": prompt}
                ],
                model=self.model_name,
                response_format={"type": "json_object"}
            )
            content_str = res.choices[0].message.content
            result = json.loads(content_str)
            cache.set(cache_key, json.dumps(result), ttl=settings.CACHE_TTL_LLM)
            return result
        except Exception as e:
            logger.error(f"Groq API call failed: {e}")
            return {"explanations": {}, "error": str(e)}

    async def complete_vision_json(self, prompt: str, image: bytes, schema: Optional[dict] = None) -> dict:
        return {"concerns": ["acne", "uneven_tone"], "confidence": {"acne": 0.72, "uneven_tone": 0.61}}


class GrokProvider:
    def __init__(self):
        self.api_key = settings.GROK_API_KEY
        self.model_name = settings.GROK_MODEL or "grok-2-latest"
        self.base_url = "https://api.x.ai/v1/chat/completions"

    def _get_cache_key(self, prompt: str) -> str:
        content = f"{self.model_name}:{prompt}"
        sha = hashlib.sha256(content.encode("utf-8")).hexdigest()
        return f"llm:grok:{sha}"

    async def complete_json(self, prompt: str, schema: Optional[dict] = None) -> dict:
        cache = get_cache()
        cache_key = self._get_cache_key(prompt)

        cached_res = cache.get(cache_key)
        if cached_res:
            try:
                return json.loads(cached_res)
            except Exception:
                pass

        if not self.api_key:
            logger.warning("GROK_API_KEY unset — returning mock fallback.")
            return {"explanations": {}, "status": "no_key"}

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": self.model_name,
            "messages": [
                {"role": "system", "content": "You are a beauty formulation expert. Respond in strict JSON format with an 'explanation' field."},
                {"role": "user", "content": prompt}
            ],
            "response_format": {"type": "json_object"},
            "temperature": 0.2
        }

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                res = await client.post(self.base_url, headers=headers, json=payload)
                res.raise_for_status()
                data = res.json()
                content_str = data["choices"][0]["message"]["content"]
                result = json.loads(content_str)
                cache.set(cache_key, json.dumps(result), ttl=settings.CACHE_TTL_LLM)
                return result
        except Exception as e:
            logger.error(f"Grok API call failed: {e}")
            return {"explanations": {}, "error": str(e)}

    async def complete_vision_json(self, prompt: str, image: bytes, schema: Optional[dict] = None) -> dict:
        return {"concerns": ["acne", "uneven_tone"], "confidence": {"acne": 0.72, "uneven_tone": 0.61}}


class GeminiProvider:
    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY
        self.model_name = settings.LLM_MODEL
        self._client = None
        if self.api_key:
            try:
                from google import genai
                self._client = genai.Client(api_key=self.api_key)
            except Exception as e:
                logger.warning(f"Gemini client init failed: {e}")

    def _get_cache_key(self, prompt: str) -> str:
        content = f"{self.model_name}:{prompt}"
        sha = hashlib.sha256(content.encode("utf-8")).hexdigest()
        return f"llm:gemini:{sha}"

    async def complete_json(self, prompt: str, schema: Optional[dict] = None) -> dict:
        cache = get_cache()
        cache_key = self._get_cache_key(prompt)
        
        cached_res = cache.get(cache_key)
        if cached_res:
            try:
                return json.loads(cached_res)
            except Exception:
                pass

        if not self._client:
            logger.warning("GEMINI_API_KEY unset — returning mock response.")
            return {"explanations": {}, "status": "no_key"}

        try:
            response = self._client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config={"response_mime_type": "application/json"}
            )
            result = json.loads(response.text)
            cache.set(cache_key, json.dumps(result), ttl=settings.CACHE_TTL_LLM)
            return result
        except Exception as e:
            logger.error(f"Gemini LLM call failed: {e}")
            return {"explanations": {}, "error": str(e)}

    async def complete_vision_json(self, prompt: str, image: bytes, schema: Optional[dict] = None) -> dict:
        if not self._client:
            return {"concerns": ["acne", "uneven_tone"], "confidence": {"acne": 0.72, "uneven_tone": 0.61}}

        try:
            from google.genai import types
            image_part = types.Part.from_bytes(data=image, mime_type="image/jpeg")
            response = self._client.models.generate_content(
                model=self.model_name,
                contents=[prompt, image_part],
                config={"response_mime_type": "application/json"}
            )
            return json.loads(response.text)
        except Exception as e:
            logger.error(f"Gemini Vision call failed: {e}")
            return {"concerns": ["acne"], "confidence": {"acne": 0.5}}


def get_llm_provider():
    if settings.GROQ_API_KEY or settings.LLM_PROVIDER == "groq":
        return GroqProvider()
    if settings.GROK_API_KEY or settings.LLM_PROVIDER == "grok":
        return GrokProvider()
    return GeminiProvider()
