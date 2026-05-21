"""
rkitect.ai Content Pipeline — Image Generation Agent

Generates carousel images (chained img2img), LinkedIn hero images, and
Twitter card images via Flux models on OpenRouter. Implements the
image-style-lock and carousel-image-generator skills.

Skills referenced:
  - skills/carousel-image-generator/SKILL.md
  - skills/image-style-lock/SKILL.md
"""

import json
import time
import base64
from pathlib import Path

import httpx
from openai import OpenAI

from config import (
    OPENROUTER_API_KEY,
    IMAGE_GENERATION_ENABLED,
    IMAGE_T2I_MODEL,
    IMAGE_I2I_MODEL,
    IMAGE_CAROUSEL_SIZE,
    IMAGE_LINKEDIN_SIZE,
    IMAGE_TWITTER_SIZE,
    IMAGE_RATE_LIMIT_SLEEP,
    IMAGE_MAX_RETRIES,
)


# ── OpenRouter client (OpenAI-compatible) ────────────────────────────────────

_client = None


def _get_client() -> OpenAI:
    """Lazy-init OpenAI client pointed at OpenRouter."""
    global _client
    if _client is None:
        _client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=OPENROUTER_API_KEY,
        )
    return _client


def _size_to_aspect_ratio(size: str | None) -> str | None:
    """Map a pixel size hint to a natural language aspect ratio."""
    if not size:
        return None
    mapping = {
        "1080x1350": "4:5 portrait",
        "1200x627": "1.91:1 landscape",
        "1600x900": "16:9 landscape",
        "1024x1024": "1:1 square",
    }
    return mapping.get(size)


def _extract_image_result(response_json: dict) -> str | None:
    """Pull a generated image URL or data URL out of an OpenRouter response."""
    choices = response_json.get("choices", []) or []
    if not choices:
        return None

    message = choices[0].get("message", {}) or {}

    images = message.get("images") or []
    if images:
        first_image = images[0] or {}
        image_url = (first_image.get("image_url") or {}).get("url")
        if image_url:
            return image_url

    content = message.get("content")
    if isinstance(content, str):
        if content.startswith("data:") or content.startswith("http"):
            return content.strip()
        return None

    if isinstance(content, list):
        for part in content:
            if not isinstance(part, dict):
                continue
            image_url = (part.get("image_url") or {}).get("url")
            if image_url:
                return image_url
            text = part.get("text")
            if isinstance(text, str) and (text.startswith("data:") or text.startswith("http")):
                return text.strip()

    return None


def _generate_openrouter_image(prompt: str, size: str | None = None) -> str | None:
    """Generate an image through OpenRouter's image-capable chat endpoint."""
    if not OPENROUTER_API_KEY:
        return None

    aspect_ratio = _size_to_aspect_ratio(size)
    if aspect_ratio:
        prompt = f"{prompt}\n\nTarget framing: {aspect_ratio}."

    payload = {
        "model": IMAGE_T2I_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "modalities": ["image"],
    }

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "rkitect-pipeline",
        "X-Title": "rkitect.ai Content Pipeline",
    }

    try:
        response = httpx.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=120,
        )
        response.raise_for_status()
        return _extract_image_result(response.json())
    except Exception as e:
        print(f"      [image_gen] openrouter image API error: {e}")
        return None


# ── Style Fingerprint (from image-style-lock skill) ─────────────────────────

def extract_style_fingerprint(slide_1_brief: dict) -> dict:
    """Extract locked visual DNA from slide 1 brief."""
    palette = slide_1_brief.get(
        "color_palette",
        "warm neutrals, cream #F5F1ED, concrete gray #A89A8D",
    )
    mood = slide_1_brief.get("mood", "professional")

    mood_lighting_map = {
        "professional": "soft diffuse natural light, warm afternoon, no harsh shadows",
        "urgent": "high contrast, single directional light, sharp shadow edges",
        "inspirational": "golden hour warmth, broad soft window light",
        "educational": "even studio light, clean visibility, no directional preference",
        "bold": "high contrast, dramatic lighting, strong highlights",
    }
    lighting = mood_lighting_map.get(mood, "soft diffuse natural light, clean and even")

    dims = slide_1_brief.get("dimensions", "1080x1350")
    if "1350" in dims:
        camera = "35mm equivalent, slight wide angle, portrait framing, architectural photography"
    elif "627" in dims:
        camera = "35mm equivalent, landscape framing, generous negative space"
    else:
        camera = "35mm equivalent, neutral perspective, architectural photography"

    style = slide_1_brief.get("style", "architectural")
    style_render_map = {
        "architectural": "photorealistic architectural visualization, minimal post-processing",
        "data-viz": "clean vector-style graphic, flat design",
        "before-after": "split composition, photorealistic both sides",
        "sektura-segment": "photorealistic render with clean UI label overlays",
        "minimal": "minimal, high white space, clean composition",
        "modern": "modern photorealistic, professional, editorial quality",
    }
    rendering = style_render_map.get(style, "photorealistic, clean, minimal")

    # Extract material keywords from prompt
    prompt_text = slide_1_brief.get("prompt", "").lower()
    material_keywords = {
        "concrete": "polished concrete",
        "oak": "warm oak wood",
        "linen": "natural linen",
        "glass": "matte glass",
        "marble": "veined marble",
        "steel": "brushed steel",
    }
    materials = [label for key, label in material_keywords.items() if key in prompt_text]
    material_language = ", ".join(materials) if materials else "natural architectural materials"

    return {
        "color_palette": palette,
        "lighting": lighting,
        "camera_style": camera,
        "rendering_style": rendering,
        "mood": mood,
        "material_language": material_language,
        "composition_principle": "safe text area top 80% of frame, no text in bottom 20%",
    }


def build_style_lock_block(fingerprint: dict) -> str:
    """Build the locked style string to prepend to all slide 2-N prompts."""
    return (
        f"LOCKED VISUAL STYLE — maintain exactly across all slides:\n"
        f"Color palette: {fingerprint['color_palette']}\n"
        f"Lighting: {fingerprint['lighting']}\n"
        f"Camera: {fingerprint['camera_style']}\n"
        f"Rendering: {fingerprint['rendering_style']}\n"
        f"Materials: {fingerprint['material_language']}\n"
        f"Mood: {fingerprint['mood']}\n"
        f"Composition: {fingerprint['composition_principle']}\n"
        f"Text in image: NONE\n"
        f"---\n"
        f"SCENE FOR THIS SLIDE:\n"
    )


def build_slide_prompt(
    brief: dict, slide_index: int, style_lock: str | None = None
) -> str:
    """
    Build the final prompt for a single slide.

    Slide 0 = reference image (no style lock).
    Slides 1+ = style lock prepended to scene content.
    """
    scene = brief.get("prompt", "")

    if slide_index == 0:
        return (
            f"{scene}\n\n"
            f"Photography: photorealistic architectural, soft diffuse natural light.\n"
            f"Format: portrait 4:5 ratio. No text in image. No watermarks."
        )
    else:
        return (
            f"{style_lock}{scene}\n\n"
            f"Critical: maintain the exact color palette and lighting from the reference image.\n"
            f"Only the subject and spatial composition should differ.\n"
            f"No text in image. No watermarks."
        )


def save_fingerprint(fingerprint: dict, output_dir: Path) -> None:
    """Persist style fingerprint to disk for single-slide regeneration."""
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / "style_fingerprint.json"
    path.write_text(json.dumps(fingerprint, indent=2), encoding="utf-8")


# ── Brief Parsing ────────────────────────────────────────────────────────────

def parse_carousel_briefs(raw: str) -> list[dict]:
    """Parse carousel image brief JSON string into a list of slide dicts."""
    if not raw:
        return []
    try:
        parsed = json.loads(raw)
        if isinstance(parsed, list):
            return parsed
        if isinstance(parsed, dict):
            return [parsed]
        return []
    except (json.JSONDecodeError, TypeError) as e:
        print(f"      [image_gen] Failed to parse carousel briefs: {e}")
        return []


def parse_linkedin_brief(raw: str) -> dict | None:
    """Parse LinkedIn image brief JSON string into a single dict."""
    if not raw:
        return None
    try:
        parsed = json.loads(raw)
        if isinstance(parsed, list) and parsed:
            return parsed[0]
        if isinstance(parsed, dict):
            return parsed
        return None
    except (json.JSONDecodeError, TypeError) as e:
        print(f"      [image_gen] Failed to parse LinkedIn brief: {e}")
        return None


def parse_twitter_brief(raw: str) -> dict | None:
    """Parse Twitter image brief JSON string into a single dict."""
    if not raw:
        return None
    try:
        parsed = json.loads(raw)
        if isinstance(parsed, list) and parsed:
            return parsed[0]
        if isinstance(parsed, dict):
            return parsed
        return None
    except (json.JSONDecodeError, TypeError) as e:
        print(f"      [image_gen] Failed to parse Twitter brief: {e}")
        return None


# ── Image API Calls ──────────────────────────────────────────────────────────

def _download_image(url: str, save_path: Path) -> bool:
    """Download image from URL and save to disk. CDN URLs expire — act fast."""
    try:
        save_path.parent.mkdir(parents=True, exist_ok=True)
        with httpx.stream("GET", url, timeout=60, follow_redirects=True) as r:
            r.raise_for_status()
            with open(save_path, "wb") as f:
                for chunk in r.iter_bytes(chunk_size=8192):
                    f.write(chunk)
        return True
    except Exception as e:
        print(f"      [image_gen] Download failed ({save_path.name}): {e}")
        return False


def _generate_t2i(prompt: str, size: str = "1080x1350") -> str | None:
    """
    Text-to-image via OpenRouter image-capable chat completions.

    Returns the image URL on success, None on failure.
    """
    return _generate_openrouter_image(prompt, size)


def _generate_i2i(prompt: str, reference_image_url: str) -> str | None:
    """
    Image-to-image via Flux Kontext Pro (OpenRouter chat completions with
    image_url message block).

    Returns the generated image URL on success, None on failure.
    """
    client = _get_client()
    try:
        response = client.chat.completions.create(
            model=IMAGE_I2I_MODEL,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {"url": reference_image_url},
                        },
                        {
                            "type": "text",
                            "text": prompt,
                        },
                    ],
                }
            ],
        )
        # Kontext Pro returns the image URL in the response content
        if response.choices and response.choices[0].message:
            content = response.choices[0].message.content
            # The response may contain the URL directly or in a structured format
            if content and (content.startswith("http") or content.startswith("data:")):
                return content.strip()
            # Try to extract URL from response
            if content:
                # Sometimes the URL is embedded in markdown or text
                import re
                urls = re.findall(r'https?://[^\s\)\"\']+', content)
                if urls:
                    return urls[0]
        return None
    except Exception as e:
        print(f"      [image_gen] i2i API error: {e}")
        return None


def _generate_with_retry(
    generate_fn, *args, max_retries: int = IMAGE_MAX_RETRIES
) -> str | None:
    """
    Call generate_fn with exponential backoff on 429 rate limits.

    Returns image URL or None after exhausting retries.
    """
    for attempt in range(max_retries):
        result = generate_fn(*args)
        if result is not None:
            return result
        # Exponential backoff: 2s, 4s, 8s
        wait = 2 ** (attempt + 1)
        print(f"      [image_gen] Retry {attempt + 1}/{max_retries} in {wait}s...")
        time.sleep(wait)
    return None


# ── Carousel Generation (chained img2img) ────────────────────────────────────

def generate_carousel_images(
    prompts: list[str],
    briefs: list[dict],
    output_dir: Path,
) -> list[str]:
    """
    Generate carousel images with chained img2img.

    Slide 1: t2i via Flux 1.1 Pro
    Slides 2-N: i2i via Flux Kontext Pro using previous slide as reference

    Returns list of local file paths for successfully generated images.
    """
    images_dir = output_dir / "carousel_images"
    images_dir.mkdir(parents=True, exist_ok=True)

    paths = []
    errors = []
    previous_image_url = None

    for idx, prompt in enumerate(prompts):
        slide_num = idx + 1
        save_path = images_dir / f"slide_{slide_num:02d}.jpg"

        print(f"      [image_gen] Generating slide {slide_num}/{len(prompts)}...")

        if idx == 0:
            # Slide 1: text-to-image
            image_url = _generate_with_retry(_generate_t2i, prompt, IMAGE_CAROUSEL_SIZE)
            if image_url is None:
                print(f"      [image_gen] FATAL: Slide 1 failed. Aborting carousel generation.")
                return []  # Abort entire carousel if slide 1 fails
        else:
            # Slides 2-N: image-to-image using previous slide
            image_url = None
            if previous_image_url:
                image_url = _generate_with_retry(
                    _generate_i2i, prompt, previous_image_url
                )

            if image_url is None:
                # Fallback: t2i with full style block + scene content
                print(f"      [image_gen] slide_{slide_num:02d}: i2i failed, falling back to t2i")
                errors.append(f"slide_{slide_num:02d}: img2img failed, used t2i fallback")
                image_url = _generate_with_retry(_generate_t2i, prompt, IMAGE_CAROUSEL_SIZE)

            if image_url is None:
                print(f"      [image_gen] slide_{slide_num:02d}: All generation methods failed, skipping")
                errors.append(f"slide_{slide_num:02d}: all generation failed, skipped")
                time.sleep(IMAGE_RATE_LIMIT_SLEEP)
                continue

        # Handle data URI vs HTTP URL
        if image_url.startswith("data:"):
            # Decode base64 data URI
            try:
                b64_data = image_url.split(",", 1)[1]
                save_path.write_bytes(base64.b64decode(b64_data))
                downloaded = True
            except Exception as e:
                print(f"      [image_gen] Failed to decode b64 for slide_{slide_num:02d}: {e}")
                downloaded = False
        else:
            # Download from CDN URL (URLs expire, download immediately)
            downloaded = _download_image(image_url, save_path)

        if downloaded:
            paths.append(str(save_path))
            previous_image_url = image_url  # Use this as reference for next slide
        else:
            errors.append(f"slide_{slide_num:02d}: download failed")

        # Rate limit sleep between calls
        time.sleep(IMAGE_RATE_LIMIT_SLEEP)

    return paths


# ── Single Image Generation (LinkedIn, Twitter) ─────────────────────────────

# Platform-specific guards and image size mappings
_PLATFORM_IMAGE_CONFIG = {
    "linkedin": {
        "size": IMAGE_LINKEDIN_SIZE,
        "guards": (
            "\n\nNo text or watermarks in image. "
            "Wide 16:9 landscape composition. "
            "Professional architectural photography."
        ),
        "label": "LinkedIn hero",
    },
    "twitter": {
        "size": IMAGE_TWITTER_SIZE,
        "guards": (
            "\n\nNo text in image. "
            "High contrast for dark mode. "
            "Center-heavy composition. "
            "16:9 landscape. Professional architectural photography."
        ),
        "label": "Twitter card",
    },
}


def generate_single_image(
    brief: dict, save_path: Path, platform: str = "linkedin"
) -> str | None:
    """
    Generate a single image via t2i for a given platform.

    No chaining, no style lock — just a direct Flux 1.1 Pro call
    with platform-specific size and guards.

    Args:
        brief: Image brief dict with at least a "prompt" key.
        save_path: Where to save the downloaded image.
        platform: "linkedin" or "twitter" — determines size and guards.
    """
    prompt = brief.get("prompt", "")
    if not prompt:
        print(f"      [image_gen] {platform} brief has no prompt, skipping")
        return None

    config = _PLATFORM_IMAGE_CONFIG.get(platform, _PLATFORM_IMAGE_CONFIG["linkedin"])
    prompt += config["guards"]
    size = config["size"]
    label = config["label"]

    print(f"      [image_gen] Generating {label} image...")
    image_url = _generate_with_retry(_generate_t2i, prompt, size)

    if image_url is None:
        print(f"      [image_gen] {label} image generation failed")
        return None

    save_path.parent.mkdir(parents=True, exist_ok=True)

    # Handle data URI vs HTTP URL
    if image_url.startswith("data:"):
        try:
            b64_data = image_url.split(",", 1)[1]
            save_path.write_bytes(base64.b64decode(b64_data))
            return str(save_path)
        except Exception as e:
            print(f"      [image_gen] Failed to decode b64 for {label}: {e}")
            return None
    else:
        if _download_image(image_url, save_path):
            return str(save_path)
        return None


# ── Main Entry Point ─────────────────────────────────────────────────────────

def run_image_generation(generated: dict, output_dir: Path) -> dict:
    """
    Generate images for carousel, LinkedIn, and Twitter content.

    Called from main.py Stage 3.5, after generation and before QA.
    Implements chained img2img for carousel consistency per the
    carousel-image-generator and image-style-lock skills.

    Args:
        generated: Output from run_generation(), includes
                   carousel_image_brief, linkedin_image_brief, and
                   twitter_image_brief keys.
        output_dir: Today's output directory (e.g. output/2026-05-16/).

    Returns:
        {
            "carousel": ["output/.../slide_01.jpg", ...],
            "linkedin": ["output/.../linkedin_image.jpg"],
            "twitter":  ["output/.../twitter_image.jpg"],
            "errors": ["slide_03: img2img failed, used t2i fallback"]
        }
    """
    if not IMAGE_GENERATION_ENABLED:
        print("      [image_gen] Image generation disabled (IMAGE_GENERATION_ENABLED=false)")
        return {"carousel": [], "linkedin": [], "twitter": [], "errors": []}

    if not OPENROUTER_API_KEY:
        print("      [image_gen] OPENROUTER_API_KEY not set, skipping image generation")
        return {"carousel": [], "linkedin": [], "twitter": [], "errors": ["OPENROUTER_API_KEY not configured"]}

    result = {"carousel": [], "linkedin": [], "twitter": [], "errors": []}

    # ── Carousel Images ──────────────────────────────────────────────────
    carousel_briefs = parse_carousel_briefs(
        generated.get("carousel_image_brief", "")
    )

    if carousel_briefs:
        # Extract style fingerprint from slide 1 brief BEFORE any API call
        fingerprint = extract_style_fingerprint(carousel_briefs[0])
        save_fingerprint(fingerprint, output_dir)

        # Build locked style block for slides 2-N
        style_lock = build_style_lock_block(fingerprint)

        # Build per-slide prompts
        prompts = [
            build_slide_prompt(brief, idx, style_lock if idx > 0 else None)
            for idx, brief in enumerate(carousel_briefs)
        ]

        # Generate images with chaining
        paths = generate_carousel_images(prompts, carousel_briefs, output_dir)
        result["carousel"] = paths

        if len(paths) < len(carousel_briefs):
            result["errors"].append(
                f"Generated {len(paths)}/{len(carousel_briefs)} carousel slides"
            )
    else:
        print("      [image_gen] No carousel image briefs found, skipping carousel images")

    # ── LinkedIn Hero Image ──────────────────────────────────────────────
    linkedin_brief = parse_linkedin_brief(
        generated.get("linkedin_image_brief", "")
    )

    if linkedin_brief:
        linkedin_path = generate_single_image(
            linkedin_brief, output_dir / "linkedin_image.jpg", platform="linkedin"
        )
        if linkedin_path:
            result["linkedin"] = [linkedin_path]
        else:
            result["errors"].append("LinkedIn hero image generation failed")
    else:
        print("      [image_gen] No LinkedIn image brief found, skipping LinkedIn image")

    # ── Twitter Card Image ───────────────────────────────────────────────
    twitter_brief = parse_twitter_brief(
        generated.get("twitter_image_brief", "")
    )

    if twitter_brief:
        twitter_path = generate_single_image(
            twitter_brief, output_dir / "twitter_image.jpg", platform="twitter"
        )
        if twitter_path:
            result["twitter"] = [twitter_path]
        else:
            result["errors"].append("Twitter card image generation failed")
    else:
        print("      [image_gen] No Twitter image brief found, skipping Twitter image")

    return result
