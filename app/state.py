import json
from pathlib import Path
from typing import Any


def default_state() -> dict[str, Any]:
    """상태 파일이 없거나 깨졌을 때 사용할 기본 상태를 반환합니다."""

    return {
        "channel_id": None,
        "notified_video_ids": [],
        "notified_community_post_ids": [],
        "community_posts_initialized": False,
    }


def load_state(path: Path) -> dict[str, Any]:
    """지정한 JSON 상태 파일을 읽고 누락된 기본 필드를 채웁니다."""

    if not path.exists():
        return default_state()

    try:
        with path.open("r", encoding="utf-8") as f:
            state = json.load(f)
    except json.JSONDecodeError:
        return default_state()

    state.setdefault("channel_id", None)
    state.setdefault("notified_video_ids", [])
    state.setdefault("notified_community_post_ids", [])
    state.setdefault("community_posts_initialized", False)
    return state


def save_state(path: Path, state: dict[str, Any]) -> None:
    """현재 상태를 임시 파일에 쓴 뒤 원자적으로 상태 파일을 교체합니다."""

    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = path.with_suffix(path.suffix + ".tmp")

    with tmp_path.open("w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)

    tmp_path.replace(path)
