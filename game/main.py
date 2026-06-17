"""게임 실행을 시작하는 가장 작은 진입점 파일."""

from src.game_app import run_game


def main(difficulty=None):
    """선택 난이도를 받아 전체 게임 루프를 실행한다."""
    raise SystemExit(run_game(difficulty))


if __name__ == "__main__":
    # 이 파일을 직접 실행했을 때만 게임을 시작한다.
    main()
