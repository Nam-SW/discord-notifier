from typing import Any

import requests

from config import Config


def build_discord_payload(config: Config, live: dict[str, Any]) -> dict[str, Any]:
    """라이브 상세 정보를 Discord 웹훅 payload 형태로 변환합니다."""

    mention = config.discord_mention.strip()
    title = live["title"]
    url = live["url"]

    content_lines = []
    if mention:
        content_lines.append(mention)
    content_lines.append("🔴 **Live ON!**")
    content_lines.append(url)

    embed = {
        "title": title,
        "url": url,
        "description": "지금 방송 중이에요.",
        "fields": [],
    }

    if live.get("actual_start_time"):
        embed["fields"].append(
            {
                "name": "시작 시간",
                "value": live["actual_start_time"],
                "inline": True,
            }
        )

    if live.get("concurrent_viewers"):
        embed["fields"].append(
            {
                "name": "현재 시청자",
                "value": str(live["concurrent_viewers"]),
                "inline": True,
            }
        )

    if live.get("thumbnail_url"):
        embed["thumbnail"] = {"url": live["thumbnail_url"]}

    payload = {
        "content": "\n".join(content_lines),
        "embeds": [embed],
        "allowed_mentions": {
            "parse": ["everyone", "roles", "users"],
        },
    }

    if config.discord_webhook_name:
        payload["username"] = config.discord_webhook_name

    if config.discord_webhook_avatar_url:
        payload["avatar_url"] = config.discord_webhook_avatar_url

    return payload


def build_community_post_payload(config: Config, post: dict[str, Any]) -> dict[str, Any]:
    """커뮤니티 게시글 정보를 Discord 웹훅 payload 형태로 변환합니다."""

    mention = config.discord_mention.strip()
    url = post["url"]

    content_lines = []
    if mention:
        content_lines.append(mention)
    content_lines.append("📢 **새 커뮤니티 게시글**")
    content_lines.append(url)

    embed = {
        "title": "새 커뮤니티 게시글",
        "url": url,
        "description": post.get("content") or "내용 없음",
    }

    if post.get("image_url"):
        embed["image"] = {"url": post["image_url"]}

    payload = {
        "content": "\n".join(content_lines),
        "embeds": [embed],
        "allowed_mentions": {
            "parse": ["everyone", "roles", "users"],
        },
    }

    if config.discord_webhook_name:
        payload["username"] = config.discord_webhook_name

    if config.discord_webhook_avatar_url:
        payload["avatar_url"] = config.discord_webhook_avatar_url

    return payload


def send_discord_webhook(webhook_url: str, payload: dict[str, Any]) -> None:
    """Discord 웹훅 URL로 payload를 전송하고 실패 응답을 에러로 처리합니다."""

    response = requests.post(webhook_url, json=payload, timeout=15)

    if response.status_code not in (200, 204):
        body = response.text[:1000]
        raise RuntimeError(f"Discord webhook error: {response.status_code} {body}")
