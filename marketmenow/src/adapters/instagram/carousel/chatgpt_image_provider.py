"""
ChatGPT image provider adapter for playground API.

Wraps the browser-controlled ChatGPT API to return images in Imagen-compatible format.
"""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

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


class ChatGPTImageProvider:
    """Adapter that calls playground API (browser-controlled ChatGPT) for image generation.
    
    Provides the same async interface as Google's Imagen client:
        response = await provider.aio.models.generate_images(
            model="...",
            prompt="...",
            config=...
        )
        image_bytes = response.generated_images[0].image.image_bytes
    """

    def __init__(self, api_url: str, timeout_ms: int = 480000):
        """Initialize with playground API URL and timeout.
        
        Args:
            api_url: Base URL of playground API (e.g., "http://localhost:3001")
            timeout_ms: Total timeout for image generation in milliseconds
        """
        self.api_url = api_url.rstrip("/")
        self.timeout_ms = timeout_ms
        self.aio = _AsyncImageModels(self)

    async def generate_images_async(
        self, prompt: str, config: genai_types.GenerateImagesConfig | None = None
    ) -> GenerateImagesResponse:
        """Generate images using playground ChatGPT API.
        
        Args:
            prompt: Image generation prompt
            config: GenerateImagesConfig (unused, accepted for interface compatibility)
        
        Returns:
            GenerateImagesResponse with generated_images list
        """
        timeout_sec = self.timeout_ms / 1000
        client = httpx.AsyncClient(timeout=30.0)

        try:
            # Submit job
            resp = await client.post(
                f"{self.api_url}/v1/images/generate",
                json={"prompt": prompt, "provider": "chatgpt"},
            )
            if resp.status_code != 202:
                raise RuntimeError(
                    f"Failed to submit image generation job: {resp.status_code} {resp.text}"
                )
            job_data = resp.json()
            job_id = job_data["jobId"]

            logger.info(f"Image generation job submitted: {job_id} (prompt: {prompt[:60]}...)")

            # Poll for completion
            start_time = asyncio.get_event_loop().time()
            poll_interval = 2  # seconds

            while asyncio.get_event_loop().time() - start_time < timeout_sec:
                resp = await client.get(f"{self.api_url}/v1/jobs/{job_id}")
                if resp.status_code != 200:
                    raise RuntimeError(f"Failed to get job status: {resp.status_code}")

                job_status = resp.json()
                state = job_status.get("state")

                if state == "completed":
                    logger.info(f"Image generation job completed: {job_id}")
                    # Extract images from returnvalue (ImageJobResult format)
                    return_value = job_status.get("returnvalue")
                    if not return_value:
                        raise RuntimeError("Job completed but no images returned")

                    # Handle ImageJobResult format: { requestId, provider, images: StoredImage[] }
                    images_list = return_value.get("images", [])
                    if not isinstance(images_list, list):
                        raise RuntimeError("Invalid images format in job result")

                    # Download image bytes from secureUrl
                    image_bytes_list = []
                    for image_info in images_list:
                        if isinstance(image_info, dict) and "secureUrl" in image_info:
                            secure_url = image_info["secureUrl"]
                            image_bytes = await self._download_from_url(client, secure_url)
                            image_bytes_list.append(GeneratedImage(image_bytes=image_bytes))

                    if image_bytes_list:
                        logger.info(
                            f"Downloaded {len(image_bytes_list)} images from job {job_id}"
                        )
                        return GenerateImagesResponse(generated_images=image_bytes_list)
                    else:
                        raise RuntimeError("No valid images found in job output")

                elif state == "failed":
                    reason = job_status.get("failedReason", "Unknown error")
                    raise RuntimeError(f"Image generation job failed: {reason}")

                # Job still processing, wait before next poll
                await asyncio.sleep(poll_interval)

            raise RuntimeError(
                f"Image generation timed out after {timeout_sec:.0f} seconds"
            )
        finally:
            await client.aclose()

    async def _download_from_url(self, client: httpx.AsyncClient, url: str) -> bytes:
        """Download image bytes from URL (local file:// or remote HTTP).
        
        Args:
            client: httpx async client
            url: URL to download from (can be file:// or http(s)://)
        
        Returns:
            Image file bytes
        """
        # Handle file:// URLs (local files)
        if url.startswith("file://"):
            try:
                local_path = url.replace("file:///", "").replace("/", "\\")
                return Path(local_path).read_bytes()
            except Exception as e:
                logger.warning(f"Failed to read local file {url}: {e}")

        # Handle HTTP(S) URLs (Cloudinary, etc.)
        try:
            resp = await client.get(url)
            if resp.status_code == 200:
                return resp.content
        except Exception as e:
            logger.warning(f"Failed to download image from {url}: {e}")

        raise RuntimeError(f"Could not download image from {url}")


class _AsyncImageModels:
    """Mock async models interface to match genai client structure."""

    def __init__(self, provider: ChatGPTImageProvider):
        self.provider = provider
        self.models = _AsyncModels(provider)


class _AsyncModels:
    """Mock models interface."""

    def __init__(self, provider: ChatGPTImageProvider):
        self.provider = provider

    async def generate_images(
        self,
        model: str,
        prompt: str,
        config: genai_types.GenerateImagesConfig | None = None,
    ) -> GenerateImagesResponse:
        """Match Imagen API signature."""
        return await self.provider.generate_images_async(prompt, config)
