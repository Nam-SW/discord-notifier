import json

from config import Config
from discord_webhook import build_community_post_payload, build_discord_payload, send_discord_webhook
from state import load_state, save_state
from youtube import fetch_initial_community_posts, find_current_live_video, get_live_details, resolve_channel_id


def check_once(config: Config, dry_run: bool = False) -> None:
    """현재 라이브와 커뮤니티 게시글을 한 번 확인하고 필요한 경우 Discord 알림을 보냅니다."""

    state = load_state(config.state_path)

    try:
        channel_id = resolve_channel_id(config, state)
        check_live_once(config, state, channel_id, dry_run=dry_run)
    except Exception as e:
        if is_youtube_quota_error(e):
            print(f"[error] live check skipped: YouTube API quota exceeded: {e}")
        else:
            print(f"[error] live check failed: {e}")
    save_state(config.state_path, state)

    try:
        check_community_once(config, state, dry_run=dry_run)
    except Exception as e:
        print(f"[error] community check failed: {e}")
    save_state(config.state_path, state)


def check_live_once(config: Config, state: dict, channel_id: str, dry_run: bool = False) -> None:
    """현재 라이브를 확인하고 새 라이브면 Discord 알림을 보냅니다."""

    live_candidate = find_current_live_video(config, channel_id)
    if not live_candidate:
        print("[check] live not found")
        return

    video_id = live_candidate["video_id"]
    notified_video_ids = set(state.get("notified_video_ids", []))

    if video_id in notified_video_ids:
        print(f"[check] already notified: {video_id}")
        return

    live_details = get_live_details(config, video_id)
    if not live_details:
        print(f"[check] video details not found: {video_id}")
        return

    # actualStartTime은 실제 방송 시작 후에 제공됩니다.
    # 이 값이 없으면 예정/전환 중 상태일 수 있으니 알림을 보류합니다.
    if not live_details.get("actual_start_time"):
        print(f"[check] live candidate found, but actualStartTime is missing: {video_id}")
        return

    payload = build_discord_payload(config, live_details)

    if dry_run:
        print("[dry-run] Discord payload:")
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        send_discord_webhook(config.discord_webhook_url, payload)
        print(f"[notify] sent: {video_id}")

    notified_video_ids.add(video_id)
    state["notified_video_ids"] = sorted(notified_video_ids)
    state["last_live_video_id"] = video_id


def check_community_once(config: Config, state: dict, dry_run: bool = False) -> None:
    """커뮤니티 게시글을 확인하고 새 게시글이면 Discord 알림을 보냅니다."""

    if not config.youtube_channel_handle:
        print("[check] community skipped: YOUTUBE_CHANNEL_HANDLE is missing")
        return

    posts = fetch_initial_community_posts(config)

    if not state.get("community_posts_initialized"):
        state["notified_community_post_ids"] = []
        state["last_community_post_id"] = posts[0]["post_id"] if posts else None
        state["community_posts_initialized"] = True
        if not posts:
            print("[init] community posts stored: 0")
            return

    if not posts:
        print("[check] community posts not found")
        return

    notified_post_ids = set(state.get("notified_community_post_ids", []))
    new_posts = [post for post in posts if post["post_id"] not in notified_post_ids]
    if not new_posts:
        print("[check] new community post not found")
        return

    for post in reversed(new_posts):
        payload = build_community_post_payload(config, post)

        if dry_run:
            print("[dry-run] Discord community payload:")
            print(json.dumps(payload, ensure_ascii=False, indent=2))
        else:
            send_discord_webhook(config.discord_webhook_url, payload)
            print(f"[notify] community sent: {post['post_id']}")

        notified_post_ids.add(post["post_id"])
        state["notified_community_post_ids"] = sorted(notified_post_ids)
        state["last_community_post_id"] = posts[0]["post_id"]
        state["community_posts_initialized"] = True
        save_state(config.state_path, state)

    state["notified_community_post_ids"] = sorted(notified_post_ids)
    state["last_community_post_id"] = posts[0]["post_id"]
    state["community_posts_initialized"] = True


def is_youtube_quota_error(error: Exception) -> bool:
    """YouTube Data API quota 초과 오류인지 메시지 기반으로 판별합니다."""

    message = str(error).lower()
    return "quota exceeded" in message or "quotaexceeded" in message
