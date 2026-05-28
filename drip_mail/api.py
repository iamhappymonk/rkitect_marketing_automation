"""FastAPI server: webhook receiver + APScheduler drip runner + dashboard."""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from pathlib import Path

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import FastAPI, Header, HTTPException
from fastapi.staticfiles import StaticFiles

from drip_mail import config
from drip_mail.engine.runner import FlowRunner

logger = logging.getLogger(__name__)

_scheduler = AsyncIOScheduler()


def _run_drip_poll() -> None:
    try:
        stats = FlowRunner().run_once()
        logger.info("Scheduled poll: %s", stats)
    except Exception as exc:  # noqa: BLE001
        logger.error("Scheduled poll failed: %s", exc)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    interval = config.DRIP_POLL_INTERVAL_SECONDS
    if interval > 0:
        _scheduler.add_job(_run_drip_poll, "interval", seconds=interval, id="drip_poll")
        _scheduler.start()
        logger.info("APScheduler started — drip poll every %ss", interval)
    yield
    if _scheduler.running:
        _scheduler.shutdown(wait=False)


app = FastAPI(title="drip_mail", lifespan=lifespan)

_static_dir = Path(__file__).parent / "dashboard" / "static"
if _static_dir.is_dir():
    app.mount("/static", StaticFiles(directory=str(_static_dir)), name="static")

# Import dashboard router after app is created to avoid circular issues
from drip_mail.dashboard.routes import router as dashboard_router  # noqa: E402
app.include_router(dashboard_router)


@app.get("/health")
async def health() -> dict:
    return {"ok": True}


@app.post("/webhook/signup")
async def webhook_signup(x_webhook_secret: str | None = Header(default=None)) -> dict:
    if not config.WEBHOOK_SECRET or x_webhook_secret != config.WEBHOOK_SECRET:
        raise HTTPException(status_code=401, detail="Invalid or missing webhook secret")
    try:
        stats = FlowRunner().run_once(flow_filter="welcome_on_signup")
        logger.info("Webhook signup triggered: %s", stats)
        return stats
    except Exception as exc:  # noqa: BLE001
        logger.error("Webhook signup error: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc)) from exc
