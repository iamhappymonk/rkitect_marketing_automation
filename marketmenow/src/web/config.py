from __future__ import annotations

from pathlib import Path

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = ""
    output_dir: Path = Path("output")
    queue_poll_seconds: int = 30
    host: str = "0.0.0.0"
    port: int = 8000

    # Buffer publishing bridge (approved content -> Buffer queue)
    buffer_enabled: bool = True
    buffer_api_url: str = "https://api.buffer.com"
    buffer_api_token: str = ""
    buffer_scheduling_type: str = "automatic"
    buffer_share_mode: str = "addToQueue"
    buffer_linkedin_channel_id: str = "6a020577090476fb990aecc6"
    buffer_instagram_channel_id: str = "6a020514090476fb990aeaf3"
    buffer_twitter_channel_id: str = "6a02054e090476fb990aec04"

    batch_email_template: Path = Path("templates/email_template.html")
    batch_email_csv: Path = Path("vault/contacts.csv")
    batch_email_size: int = 100

    model_config = {"env_prefix": "MMN_WEB_", "env_file": ".env", "extra": "ignore"}


settings = Settings()
