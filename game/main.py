# 게임 시작점

from src.game_app import run_game


def main(difficulty=None):
    # 게임 실행
    raise SystemExit(run_game(difficulty))


if __name__ == "__main__":
    # 직접 실행
    main()
