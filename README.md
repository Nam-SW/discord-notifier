# discord-notifier

크리에이터의 라이브 스트림 및 커뮤니티 업데이트를 위한 비공개 자체 호스팅 Discord 알림 도구입니다.

YouTube 데이터 API를 사용하여 공개 채널 및 라이브 스트림 메타데이터를 읽으며, 설정된 Discord 웹훅을 통해 Discord 채널로 알림을 전송합니다.

## 개인정보 보호정책
- YouTube 콘텐츠를 업로드, 수정, 삭제 또는 관리하지 않습니다.
- YouTube 사용자 계정, OAuth 토큰 또는 개인 데이터를 수집하지 않습니다.
- 라이브 스트림 알림에 필요한 공개 YouTube 메타데이터만 읽습니다.
- Discord 알림은 설정된 Discord 웹훅 URL로만 전송됩니다.
- 중복 알림 방지를 위한 최소한의 로컬 상태 정보만 저장할 수 있습니다.

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
