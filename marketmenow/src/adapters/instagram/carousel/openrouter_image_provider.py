"""
OpenRouter image provider adapter.

Calls OpenRouter's /v1/chat/completions API to generate images using the specified model.
"""

from __future__ import annotations

import base64
import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING
import re

import httpx

if TYPE_CHECKING:
    from google.genai import types as genai_types


logger = logging.getLogger(__name__)


@dataclass
class GeneratedImage:
    """Mock of genai GeneratedImage for interface compatibility."""

    image_bytes: bytes


@dataclass
class GenerateImagesResponse:
    """Mock response matching Imagen API response structure."""

    generated_images: list[GeneratedImage]


class OpenRouterImageProvider:
    """Adapter that calls OpenRouter API for image generation.
    
    Provides the same async interface as Google's Imagen client.
    """

    def __init__(self, api_key: str, model: str = "gpt-image-1", timeout_ms: int = 120000):
        """Initialize with OpenRouter API key.
        
        Args:
            api_key: OpenRouter API key
            model: OpenRouter model to use for image generation
            timeout_ms: Total timeout for image generation in milliseconds
        """
        self.api_key = api_key
        self.model = model
        self.timeout_ms = timeout_ms
        self.aio = _AsyncImageModels(self)
        self.api_url = "https://openrouter.ai/api/v1/chat/completions"

    async def generate_images_async(
        self, prompt: str, config: genai_types.GenerateImagesConfig | None = None
    ) -> GenerateImagesResponse:
        """Generate images using OpenRouter.
        
        Args:
            prompt: Image generation prompt
            config: GenerateImagesConfig (unused)
        
        Returns:
            GenerateImagesResponse with generated_images list
        """
        if not self.api_key:
            raise RuntimeError("OpenRouter API key is missing.")

        timeout_sec = self.timeout_ms / 1000
        client = httpx.AsyncClient(timeout=timeout_sec)

        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "modalities": ["image"],
        }
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "HTTP-Referer": "https://marketmenow.com", # Required by OpenRouter
            "X-Title": "MarketMeNow", # Required by OpenRouter
            "Content-Type": "application/json",
        }

        try:
            logger.info(f"Submitting image generation request to OpenRouter ({self.model})")
            resp = await client.post(self.api_url, json=payload, headers=headers)
            
            if resp.status_code != 200:
                raise RuntimeError(
                    f"OpenRouter API failed: {resp.status_code} {resp.text}"
                )
                
            data = resp.json()
            
            if "choices" not in data or not data["choices"]:
                raise RuntimeError(f"OpenRouter returned no choices: {data}")
                
            message = data["choices"][0].get("message", {})
            content = message.get("content", "")
            
            # OpenRouter might return images in a few different ways:
            # 1. message.images array (URLs or base64 data URIs)
            # 2. Markdown image links in content: ![alt](url)
            # 3. Just a URL in content
            
            image_urls_or_data = []
            
            if "images" in message and isinstance(message["images"], list):
                image_urls_or_data.extend(message["images"])
            
            if not image_urls_or_data and content:
                # Try to extract markdown image links
                markdown_images = re.findall(r'!\[.*?\]\((.*?)\)', content)
                if markdown_images:
                    image_urls_or_data.extend(markdown_images)
                # Try to see if content is just a URL
                elif content.strip().startswith("http"):
                    image_urls_or_data.append(content.strip())
            
            if not image_urls_or_data:
                raise RuntimeError(f"Could not extract any images from OpenRouter response: {data}")

            image_bytes_list = []
            for img_data in image_urls_or_data:
                if img_data.startswith("data:image"):
                    # Extract base64 part
                    b64_str = img_data.split(",", 1)[1]
                    img_bytes = base64.b64decode(b64_str)
                    image_bytes_list.append(GeneratedImage(image_bytes=img_bytes))
                elif img_data.startswith("http"):
                    img_bytes = await self._download_from_url(client, img_data)
                    image_bytes_list.append(GeneratedImage(image_bytes=img_bytes))
                else:
                    logger.warning(f"Unrecognized image data format from OpenRouter: {img_data[:50]}...")
            
            if not image_bytes_list:
                raise RuntimeError("Failed to parse or download any images from OpenRouter")
                
            return GenerateImagesResponse(generated_images=image_bytes_list)
            
        finally:
            await client.aclose()

    async def _download_from_url(self, client: httpx.AsyncClient, url: str) -> bytes:
        """Download image bytes from HTTP URL."""
        try:
            resp = await client.get(url, follow_redirects=True)
            if resp.status_code == 200:
                return resp.content
        except Exception as e:
            logger.warning(f"Failed to download image from {url}: {e}")

        raise RuntimeError(f"Could not download image from {url}")


class _AsyncImageModels:
    """Mock async models interface to match genai client structure."""

    def __init__(self, provider: OpenRouterImageProvider):
        self.provider = provider
        self.models = _AsyncModels(provider)


class _AsyncModels:
    """Mock models interface."""

    def __init__(self, provider: OpenRouterImageProvider):
        self.provider = provider

    async def generate_images(
        self,
        model: str,
        prompt: str,
        config: genai_types.GenerateImagesConfig | None = None,
    ) -> GenerateImagesResponse:
        """Match Imagen API signature."""
        # Note: We ignore the passed-in model and use the one initialized in OpenRouterImageProvider
        return await self.provider.generate_images_async(prompt, config)
