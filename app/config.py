import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


@dataclass(frozen=True)
class Config:
    """애플리케이션 실행에 필요한 환경 설정값 묶음입니다."""

    youtube_api_key: str
    youtube_channel_id: str | None
    youtube_channel_handle: str | None
    discord_webhook_url: str
    discord_mention: str
    discord_webhook_name: str | None
    discord_webhook_avatar_url: str | None
    poll_interval_seconds: int
    state_path: Path


def load_config() -> Config:
    """환경 변수와 `.env` 파일에서 설정을 읽고 필수값을 검증합니다."""

    load_dotenv()

    youtube_api_key = os.getenv("YOUTUBE_API_KEY", "").strip()
    youtube_channel_id = os.getenv("YOUTUBE_CHANNEL_ID", "").strip() or None
    youtube_channel_handle = os.getenv("YOUTUBE_CHANNEL_HANDLE", "").strip() or None
    discord_webhook_url = os.getenv("DISCORD_WEBHOOK_URL", "").strip()
    discord_mention = os.getenv("DISCORD_MENTION", "").strip()
    poll_interval_seconds = int(os.getenv("POLL_INTERVAL_SECONDS", "60"))
    state_path = Path(os.getenv("STATE_PATH", "./state.json"))
    discord_webhook_name = os.getenv("DISCORD_WEBHOOK_NAME", "").strip() or None
    discord_webhook_avatar_url = os.getenv("DISCORD_WEBHOOK_AVATAR_URL", "").strip() or None

    missing = []
    if not youtube_api_key:
        missing.append("YOUTUBE_API_KEY")
    if not youtube_channel_id and not youtube_channel_handle:
        missing.append("YOUTUBE_CHANNEL_ID or YOUTUBE_CHANNEL_HANDLE")
    if not discord_webhook_url:
        missing.append("DISCORD_WEBHOOK_URL")

    if missing:
        raise RuntimeError(f"Missing required env values: {', '.join(missing)}")

    return Config(
        youtube_api_key=youtube_api_key,
        youtube_channel_id=youtube_channel_id,
        youtube_channel_handle=youtube_channel_handle,
        discord_webhook_url=discord_webhook_url,
        discord_mention=discord_mention,
        poll_interval_seconds=poll_interval_seconds,
        state_path=state_path,
        discord_webhook_name=discord_webhook_name,
        discord_webhook_avatar_url=discord_webhook_avatar_url,
    )
