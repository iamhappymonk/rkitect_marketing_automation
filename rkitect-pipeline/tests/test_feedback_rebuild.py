"""
TDD: Feedback → pipeline rebuild.

Both text and image feedback must trigger an immediate rebuild of the exact
post and replace (not append alongside) the stale queue item.

Tests are written BEFORE implementation. Failing tests confirm features absent.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))


# ── helpers ─────────────────────────────────────────────────────────────────

def _make_queue_item(item_id: str, fmt: str = "linkedin", source_file: str = "") -> dict:
    return {
        "id": item_id,
        "format": fmt,
        "platform": fmt,
        "topic": "Test topic",
        "pillar": "education_insight",
        "angle": "",
        "content": "Original content",
        "score": 85,
        "status": "pending_review",
        "source_file": source_file,
        "image_paths": [],
    }


# ── helpers for Flask API tests ──────────────────────────────────────────────

def _app_client(queue_file):
    """Return a Flask test client with auth bypassed and queue patched."""
    import importlib
    import dashboard.app as app_module
    importlib.reload(app_module)
    # Patch credentials so test header passes
    app_module.DASHBOARD_USERNAME = "admin"
    app_module.DASHBOARD_PASSWORD = "changeme"
    app = app_module.app
    app.config["TESTING"] = True
    return app.test_client(), app_module


_AUTH = {"Authorization": "Basic YWRtaW46Y2hhbmdlbWU="}  # admin:changeme


# ── Text feedback: old item removed from queue ───────────────────────────────

def test_text_feedback_removes_old_item_from_queue(tmp_path):
    """After text feedback, the original queue item is no longer in the queue."""
    queue_file = tmp_path / "publish_queue.json"
    orig_item = _make_queue_item("item-old-001", "linkedin", str(tmp_path / "linkedin.md"))
    queue_file.write_text(json.dumps([orig_item]))

    with patch("utils.context_loader.PUBLISH_QUEUE", queue_file), \
         patch("config.PUBLISH_QUEUE", queue_file):

        client, app_module = _app_client(queue_file)

        with patch.object(app_module, "apply_feedback", return_value={
            "status": "requeued",
            "queue_id": "item-new-002",
            "format": "linkedin",
            "content": "Revised content",
        }), patch.object(app_module, "load_review_queue",
                         return_value=[orig_item]), \
             patch.object(app_module, "save_review_queue") as mock_save, \
             patch.object(app_module, "enrich_skill_performance"), \
             patch.object(app_module, "enrich_post_history"):

            resp = client.post(
                "/api/review-queue/item-old-001/feedback",
                json={"feedback": "Too formal, use builder voice"},
                headers=_AUTH,
            )

    assert resp.status_code == 200, resp.data
    # save_review_queue called with old item removed
    assert mock_save.called
    saved_queue = mock_save.call_args[0][0]
    ids = [e["id"] for e in saved_queue]
    assert "item-old-001" not in ids, f"Old item should be removed, got ids={ids}"


def test_text_feedback_new_item_present_in_queue(tmp_path):
    """After text feedback, the regenerated item IS in the queue (added by apply_feedback)."""
    queue_file = tmp_path / "publish_queue.json"
    orig_item = _make_queue_item("item-old-001", "linkedin", str(tmp_path / "linkedin.md"))
    new_item = _make_queue_item("item-new-002", "linkedin")
    queue_file.write_text(json.dumps([orig_item]))

    with patch("utils.context_loader.PUBLISH_QUEUE", queue_file), \
         patch("config.PUBLISH_QUEUE", queue_file):

        client, app_module = _app_client(queue_file)

        # apply_feedback appends new item → load_review_queue returns both
        with patch.object(app_module, "apply_feedback", return_value={
            "status": "requeued",
            "queue_id": "item-new-002",
            "format": "linkedin",
            "content": "Revised content",
        }), patch.object(app_module, "load_review_queue",
                         return_value=[orig_item, new_item]), \
             patch.object(app_module, "save_review_queue") as mock_save, \
             patch.object(app_module, "enrich_skill_performance"), \
             patch.object(app_module, "enrich_post_history"):

            resp = client.post(
                "/api/review-queue/item-old-001/feedback",
                json={"feedback": "Too formal"},
                headers=_AUTH,
            )

    assert resp.status_code == 200, resp.data
    # After filtering: only new item should remain
    saved_queue = mock_save.call_args[0][0]
    ids = [e["id"] for e in saved_queue]
    assert "item-new-002" in ids, f"New item missing. Got ids={ids}"


# ── Image feedback: regenerate_images_for_item ───────────────────────────────

def test_regenerate_images_loads_briefs_from_run_folder(tmp_path):
    """regenerate_images_for_item reads image_briefs.json from the run folder."""
    run_folder = tmp_path / "run_123"
    run_folder.mkdir()

    # Write fake briefs
    briefs = {
        "carousel_image_brief": json.dumps([
            {"prompt": "modern studio exterior", "mood": "professional"}
        ])
    }
    (run_folder / "image_briefs.json").write_text(json.dumps(briefs))
    (run_folder / "carousel.md").write_text("some content")

    item = _make_queue_item("img-001", "carousel", str(run_folder / "carousel.md"))

    with patch("agents.image_generator.run_image_generation") as mock_gen:
        mock_gen.return_value = {
            "carousel": [str(run_folder / "carousel_images" / "slide_01.jpg")],
            "linkedin": [],
            "twitter": [],
            "errors": [],
        }

        from agents.feedback import regenerate_images_for_item
        result = regenerate_images_for_item(item, feedback="needs golden hour lighting")

    assert mock_gen.called, "run_image_generation should be called"
    assert result["image_paths"], "should return new image paths"
    assert not result["errors"]


def test_regenerate_images_injects_feedback_into_prompts(tmp_path):
    """Feedback text is injected into each carousel slide prompt."""
    run_folder = tmp_path / "run_456"
    run_folder.mkdir()

    original_prompt = "modern studio exterior, concrete facade"
    briefs = {
        "carousel_image_brief": json.dumps([
            {"prompt": original_prompt, "mood": "professional"},
            {"prompt": "interior courtyard view", "mood": "professional"},
        ])
    }
    (run_folder / "image_briefs.json").write_text(json.dumps(briefs))
    (run_folder / "carousel.md").write_text("content")

    item = _make_queue_item("img-002", "carousel", str(run_folder / "carousel.md"))
    captured_briefs = {}

    def capture_gen(generated, out_dir):
        captured_briefs.update(generated)
        return {"carousel": ["slide_01.jpg"], "linkedin": [], "twitter": [], "errors": []}

    with patch("agents.image_generator.run_image_generation", side_effect=capture_gen):
        from agents.feedback import regenerate_images_for_item
        regenerate_images_for_item(item, feedback="needs golden hour lighting")

    passed_slides = json.loads(captured_briefs.get("carousel_image_brief", "[]"))
    for slide in passed_slides:
        assert "golden hour lighting" in slide["prompt"], (
            f"Feedback not injected. Got: {slide['prompt']!r}"
        )


def test_regenerate_images_returns_error_when_no_briefs_file(tmp_path):
    """Returns error dict (no crash) when image_briefs.json is missing."""
    run_folder = tmp_path / "run_789"
    run_folder.mkdir()
    # No image_briefs.json written

    item = _make_queue_item("img-003", "carousel", str(run_folder / "carousel.md"))

    from agents.feedback import regenerate_images_for_item
    result = regenerate_images_for_item(item, feedback="test feedback")

    assert result["image_paths"] == []
    assert result["errors"]


def test_regenerate_images_returns_error_when_no_source_file(tmp_path):
    """Returns error dict (no crash) when item has no source_file."""
    item = _make_queue_item("img-004", "carousel", source_file="")

    from agents.feedback import regenerate_images_for_item
    result = regenerate_images_for_item(item, feedback="test feedback")

    assert result["image_paths"] == []
    assert result["errors"]


# ── Image feedback API: updates queue item image_paths ───────────────────────

def test_image_feedback_api_updates_queue_item_image_paths(tmp_path):
    """POST image-feedback updates image_paths on the queue item after regen."""
    run_folder = tmp_path / "run_abc"
    run_folder.mkdir()
    queue_file = tmp_path / "publish_queue.json"
    item = _make_queue_item("img-queue-001", "carousel", str(run_folder / "carousel.md"))
    item["image_paths"] = [str(run_folder / "old_slide.jpg")]
    queue_file.write_text(json.dumps([item]))

    new_img_paths = [str(run_folder / "carousel_images" / "slide_01.jpg")]

    with patch("utils.context_loader.PUBLISH_QUEUE", queue_file), \
         patch("config.PUBLISH_QUEUE", queue_file):

        client, app_module = _app_client(queue_file)

        with patch.object(app_module, "enrich_image_feedback", return_value={
            "template_id": "studio-v1",
            "template_updated": True,
            "renderer_updated": True,
            "perf_updated": True,
            "feedback": "needs golden hour",
        }), patch.object(app_module, "regenerate_images_for_item", return_value={
            "image_paths": new_img_paths,
            "errors": [],
        }), patch.object(app_module, "load_review_queue",
                         return_value=[item]), \
             patch.object(app_module, "save_review_queue") as mock_save:

            resp = client.post(
                "/api/review-queue/img-queue-001/image-feedback",
                json={"feedback": "needs golden hour lighting"},
                headers=_AUTH,
            )

    assert resp.status_code == 200, resp.data
    data = resp.get_json()
    assert data.get("image_paths") == new_img_paths, f"Expected paths in response, got: {data}"

    # Queue item must be updated via save_review_queue
    assert mock_save.called
    saved = mock_save.call_args[0][0]
    assert saved[0]["image_paths"] == new_img_paths, (
        f"Queue item image_paths not updated. Got: {saved[0]['image_paths']}"
    )


def test_image_feedback_api_status_includes_regen_flag(tmp_path):
    """POST image-feedback response includes images_regenerated: true."""
    queue_file = tmp_path / "pub_queue.json"
    item = _make_queue_item("img-q-002", "carousel", str(tmp_path / "carousel.md"))
    queue_file.write_text(json.dumps([item]))

    with patch("utils.context_loader.PUBLISH_QUEUE", queue_file), \
         patch("config.PUBLISH_QUEUE", queue_file):

        client, app_module = _app_client(queue_file)

        with patch.object(app_module, "enrich_image_feedback", return_value={
            "template_id": None, "template_updated": False,
            "renderer_updated": False, "perf_updated": False, "feedback": "x",
        }), patch.object(app_module, "regenerate_images_for_item", return_value={
            "image_paths": ["new.jpg"], "errors": [],
        }), patch.object(app_module, "load_review_queue",
                         return_value=[item]), \
             patch.object(app_module, "save_review_queue"):

            resp = client.post(
                "/api/review-queue/img-q-002/image-feedback",
                json={"feedback": "fix lighting"},
                headers=_AUTH,
            )

    data = resp.get_json()
    assert data is not None, f"Response was not JSON. Status: {resp.status_code}, body: {resp.data}"
    assert data.get("images_regenerated") is True, f"Expected images_regenerated=True, got: {data}"
