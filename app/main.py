import argparse
import sys
import time

from config import load_config
from notifier import check_once


def main() -> int:
    """명령행 옵션을 읽고 1회 실행 또는 주기 실행 모드를 시작합니다."""

    parser = argparse.ArgumentParser()
    parser.add_argument("--once", action="store_true", help="check once and exit")
    parser.add_argument("--dry-run", action="store_true", help="do not send Discord message")
    args = parser.parse_args()

    config = load_config()

    if args.once:
        check_once(config, dry_run=args.dry_run)
        return 0

    print(f"[start] polling every {config.poll_interval_seconds}s")

    while True:
        try:
            check_once(config, dry_run=args.dry_run)
        except Exception as e:
            print(f"[error] {e}", file=sys.stderr)

        time.sleep(config.poll_interval_seconds)


if __name__ == "__main__":
    raise SystemExit(main())
