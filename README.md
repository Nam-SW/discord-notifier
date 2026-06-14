# discord-notifier

YouTube 채널의 현재 라이브 방송과 커뮤니티 게시글을 주기적으로 확인하고, 새 항목이 발견되면 Discord 웹훅으로 알림을 보내는 간단한 봇입니다.

## 설정

프로젝트 루트의 `.env` 파일에 필요한 값을 설정합니다.

`YOUTUBE_CHANNEL_ID`와 `YOUTUBE_CHANNEL_HANDLE` 중 하나는 반드시 필요합니다.

커뮤니티 게시글 알림은 `https://www.youtube.com/{YOUTUBE_CHANNEL_HANDLE}/posts` 페이지를 읽기 때문에 `YOUTUBE_CHANNEL_HANDLE`이 설정된 경우에만 동작합니다. 최초 실행 시에도 현재 보이는 커뮤니티 게시글도 알림을 보내고 상태 파일에 저장하기 때문에, 최초 실행 시 알람이 우르르 뜰 수 있습니다.

## 실행

```bash
docker compose up -d
```

로그 확인:

```bash
docker compose logs -f
```

중지:

```bash
docker compose down
```

## 초기화

알림을 보낸 영상 ID, 커뮤니티 게시글 ID, 핸들로 찾은 채널 ID는 `data/state.json`에 저장됩니다.

처음 상태로 다시 시작하려면 컨테이너를 내린 뒤 `data` 디렉터리 또는 `data/state.json` 파일을 삭제하고 다시 실행하면 됩니다.
