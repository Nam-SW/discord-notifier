import json
import re
from collections import deque
from typing import Any

import requests

from config import Config
from state import save_state


YOUTUBE_API_BASE = "https://www.googleapis.com/youtube/v3"
YOUTUBE_BASE = "https://www.youtube.com"


YOUTUBE_WEB_HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/125.0 Safari/537.36",
    "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
}


def youtube_get(path: str, params: dict[str, Any]) -> dict[str, Any]:
    """YouTube Data API GET 요청을 보내고 JSON 응답을 반환합니다."""

    url = f"{YOUTUBE_API_BASE}/{path}"
    response = requests.get(url, params=params, timeout=15)

    if not response.ok:
        body = response.text[:1000]
        raise RuntimeError(f"YouTube API error: {response.status_code} {body}")

    return response.json()


def resolve_channel_id(config: Config, state: dict[str, Any]) -> str:
    """설정 또는 캐시된 상태를 이용해 조회 대상 YouTube 채널 ID를 결정합니다."""

    if config.youtube_channel_id:
        return config.youtube_channel_id

    if state.get("channel_id"):
        return state["channel_id"]

    assert config.youtube_channel_handle is not None

    data = youtube_get(
        "channels",
        {
            "part": "id,snippet",
            "forHandle": config.youtube_channel_handle,
            "key": config.youtube_api_key,
        },
    )

    items = data.get("items", [])
    if not items:
        raise RuntimeError(f"Cannot resolve channel handle: {config.youtube_channel_handle}")

    channel_id = items[0]["id"]
    state["channel_id"] = channel_id
    save_state(config.state_path, state)

    print(f"[init] resolved {config.youtube_channel_handle} -> {channel_id}")
    return channel_id


def find_current_live_video(config: Config, channel_id: str) -> dict[str, Any] | None:
    """채널에서 현재 진행 중인 라이브 영상 후보를 하나 조회합니다."""

    # search.list에서 eventType=live를 쓰면 현재 진행 중인 라이브 방송으로 제한할 수 있습니다.
    # eventType을 쓸 때는 type=video도 함께 넣어야 합니다.
    data = youtube_get(
        "search",
        {
            "part": "snippet",
            "channelId": channel_id,
            "type": "video",
            "eventType": "live",
            "maxResults": 1,
            "key": config.youtube_api_key,
        },
    )

    items = data.get("items", [])
    if not items:
        return None

    item = items[0]
    video_id = item["id"]["videoId"]
    snippet = item.get("snippet", {})

    return {
        "video_id": video_id,
        "title": snippet.get("title", "Untitled live stream"),
        "channel_title": snippet.get("channelTitle", "YouTube"),
        "published_at": snippet.get("publishedAt"),
        "thumbnail_url": pick_thumbnail(snippet),
        "url": f"https://www.youtube.com/watch?v={video_id}",
    }


def get_live_details(config: Config, video_id: str) -> dict[str, Any] | None:
    """라이브 영상의 상세 정보와 실제 시작 여부를 조회합니다."""

    data = youtube_get(
        "videos",
        {
            "part": "snippet,liveStreamingDetails",
            "id": video_id,
            "key": config.youtube_api_key,
        },
    )

    items = data.get("items", [])
    if not items:
        return None

    item = items[0]
    snippet = item.get("snippet", {})
    live_details = item.get("liveStreamingDetails", {})

    return {
        "video_id": video_id,
        "title": snippet.get("title", "Untitled live stream"),
        "channel_title": snippet.get("channelTitle", "YouTube"),
        "thumbnail_url": pick_thumbnail(snippet),
        "actual_start_time": live_details.get("actualStartTime"),
        "scheduled_start_time": live_details.get("scheduledStartTime"),
        "concurrent_viewers": live_details.get("concurrentViewers"),
        "url": f"https://www.youtube.com/watch?v={video_id}",
    }


def fetch_initial_community_posts(config: Config) -> list[dict[str, Any]]:
    """채널 커뮤니티 탭의 최초 HTML에 포함된 게시글 목록을 조회합니다."""

    if not config.youtube_channel_handle:
        return []

    handle = config.youtube_channel_handle
    if not handle.startswith("@"):
        handle = f"@{handle}"

    response = requests.get(f"{YOUTUBE_BASE}/{handle}/posts", headers=YOUTUBE_WEB_HEADERS, timeout=15)
    if not response.ok:
        body = response.text[:1000]
        raise RuntimeError(f"YouTube community page error: {response.status_code} {body}")

    match = re.search(r"var ytInitialData = (\{.*?\});</script>", response.text)
    if not match:
        raise RuntimeError("Cannot find ytInitialData in YouTube community page")

    data = json.loads(match.group(1))
    posts = []
    queue = deque([data])

    while queue:
        item = queue.popleft()
        if isinstance(item, dict):
            if "backstagePostThreadRenderer" in item:
                renderer = item["backstagePostThreadRenderer"].get("post", {}).get("backstagePostRenderer", {})
                post = build_community_post(renderer)
                if post:
                    posts.append(post)

            for value in item.values():
                if isinstance(value, (dict, list)):
                    queue.append(value)
        elif isinstance(item, list):
            queue.extend(value for value in item if isinstance(value, (dict, list)))

    return posts


def build_community_post(renderer: dict[str, Any]) -> dict[str, Any] | None:
    """커뮤니티 게시글 renderer에서 알림에 필요한 값만 추출합니다."""

    post_id = renderer.get("postId")
    if not post_id:
        return None

    content = runs_text(renderer.get("contentText"))

    return {
        "post_id": post_id,
        "url": f"{YOUTUBE_BASE}/post/{post_id}",
        "content": content.splitlines()[0] if content else "",
        "image_url": first_community_image_url(renderer.get("backstageAttachment")),
    }


def first_community_image_url(attachment: dict[str, Any] | None) -> str | None:
    """첨부 이미지가 있으면 첫 이미지 묶음의 가장 큰 URL을 반환합니다."""

    if not attachment:
        return None

    queue = deque([attachment])
    while queue:
        item = queue.popleft()
        if isinstance(item, dict):
            image_renderer = item.get("backstageImageRenderer")
            if isinstance(image_renderer, dict):
                thumbnails = image_renderer.get("image", {}).get("thumbnails")
                largest = largest_thumbnail(thumbnails) if isinstance(thumbnails, list) else None
                if largest:
                    return largest["url"]

            for value in item.values():
                if isinstance(value, (dict, list)):
                    queue.append(value)
        elif isinstance(item, list):
            queue.extend(value for value in item if isinstance(value, (dict, list)))

    return None


def largest_thumbnail(thumbnails: list[dict[str, Any]]) -> dict[str, Any] | None:
    """같은 이미지의 크기별 썸네일 중 가장 큰 항목을 고릅니다."""

    valid = [thumbnail for thumbnail in thumbnails if isinstance(thumbnail, dict) and thumbnail.get("url")]
    if not valid:
        return None

    return max(
        valid,
        key=lambda thumbnail: (
            int(thumbnail.get("width") or 0) * int(thumbnail.get("height") or 0),
            int(thumbnail.get("width") or 0),
            int(thumbnail.get("height") or 0),
        ),
    )


def runs_text(value: dict[str, Any] | None) -> str:
    """YouTube renderer의 simpleText/runs 텍스트를 문자열로 합칩니다."""

    if not isinstance(value, dict):
        return ""

    if "simpleText" in value:
        return value["simpleText"]

    return "".join(run.get("text", "") for run in value.get("runs", []))


def pick_thumbnail(snippet: dict[str, Any]) -> str | None:
    """YouTube snippet에서 가장 품질이 좋은 썸네일 URL을 고릅니다."""

    thumbnails = snippet.get("thumbnails", {})
    for key in ("maxres", "standard", "high", "medium", "default"):
        item = thumbnails.get(key)
        if item and item.get("url"):
            return item["url"]
    return None
