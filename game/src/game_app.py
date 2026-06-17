"""게임 전체 실행 흐름을 관리하는 파일.

타이틀 화면, 난이도 선택, 실제 플레이 루프, 설정 화면 진입을 여기서 연결한다.
"""

import pygame as pg

import load
from src.constants import (
    DIFFICULTY_SETTINGS,
    FPS,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
)
from src.game_input import read_frame_input
from src.game_renderer import render_game
from src.game_state import GameState
from src.gameplay import update_gameplay
from src.balanceSetting import select_difficulty
from src.title_screen import TitleAction, show_title_screen


def run_game(difficulty=None):
    """pygame을 초기화하고 사용자가 종료할 때까지 게임을 실행한다."""
    pg.init()
    screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pg.display.set_caption("지연쌤팬클럽")
    clock = pg.time.Clock()
    font = load.get_korean_font(18)
    large_font = load.get_korean_font(38)

    if difficulty is None:
        # main.py에서 난이도를 넘겨주지 않으면 사용자가 직접 선택하게 한다.
        difficulty = _choose_difficulty(screen, clock)
    else:
        # 테스트용으로 difficulty가 직접 들어온 경우 올바른 값인지 확인한다.
        difficulty = _resolve_difficulty(difficulty)

    if difficulty is None:
        # 타이틀/난이도 화면에서 종료를 고르면 게임 창을 닫는다.
        pg.quit()
        return 0

    # GameState는 플레이어, 스테이지, 적, 발사체 등 한 판의 상태를 모두 가진다.
    state = GameState(difficulty, SCREEN_HEIGHT - 50)
    running = True
    while running:
        # FPS에 맞춰 한 프레임씩 게임을 진행한다.
        clock.tick(FPS)
        actions = read_frame_input()
        if actions.quit_requested:
            running = False
            continue
        if actions.settings_pressed:
            # 게임 중 ESC를 누르면 설정 화면으로 들어간다.
            _show_settings_menu()
            continue
        if actions.restart_requested and (
            state.player.game_over or state.stage.completed
        ):
            # R키 재시작은 게임오버 또는 전체 클리어 상태에서만 허용한다.
            state.restart()
            continue

        # 상태 업데이트와 화면 그리기를 분리해서 처리한다.
        update_gameplay(state, actions)
        render_game(screen, state, font, large_font)
        pg.display.flip()

    pg.quit()
    return 0


def _choose_difficulty(screen, clock):
    """타이틀 화면과 난이도 선택 화면을 오가며 최종 난이도를 정한다."""
    while True:
        title_action = show_title_screen(screen, clock)
        if title_action == TitleAction.QUIT:
            return None
        if title_action == TitleAction.SETTINGS:
            _show_settings_menu()
            continue

        difficulty = select_difficulty(screen, clock)
        if difficulty == pg.QUIT:
            return None
        if difficulty is not None:
            return difficulty
        # difficulty가 None이면 난이도 화면에서 ESC를 누른 것이므로 타이틀로 돌아간다.


def _resolve_difficulty(difficulty):
    """외부에서 받은 난이도 값이 잘못되면 normal로 보정한다."""
    if difficulty not in DIFFICULTY_SETTINGS:
        return "normal"
    return difficulty


def _show_settings_menu():
    """설정 화면 모듈을 필요할 때만 불러와 초기 실행 부작용을 줄인다."""
    from src.settingScreen import show_settings_menu

    show_settings_menu()
