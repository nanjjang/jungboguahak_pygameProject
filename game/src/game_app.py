"""게임 실행 흐름을 관리하는 파일."""

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
    pg.init()
    screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pg.display.set_caption("지연쌤팬클럽")
    clock = pg.time.Clock()
    font = load.get_korean_font(18)
    large_font = load.get_korean_font(38)

    if difficulty is None:
        difficulty = _choose_difficulty(screen, clock)
    else:
        difficulty = _resolve_difficulty(difficulty)

    if difficulty is None:
        pg.quit()
        return 0

    state = GameState(difficulty, SCREEN_HEIGHT - 50)
    running = True
    while running:
        clock.tick(FPS)
        actions = read_frame_input()
        if actions.quit_requested:
            running = False
            continue
        if actions.settings_pressed:
            _show_settings_menu()
            continue
        if actions.restart_requested and (
            state.player.game_over or state.stage.completed
        ):
            state.restart()
            continue

        update_gameplay(state, actions)
        render_game(screen, state, font, large_font)
        pg.display.flip()

    pg.quit()
    return 0


def _choose_difficulty(screen, clock):
    while True:
        title_action = show_title_screen(screen, clock)
        if title_action == TitleAction.QUIT:
            return None
        if title_action == TitleAction.SETTINGS:
            _show_settings_menu()
            continue

        difficulty = select_difficulty(screen, clock)
        if difficulty == "quit":
            return None
        if difficulty is not None:
            return difficulty


def _resolve_difficulty(difficulty):
    if difficulty not in DIFFICULTY_SETTINGS:
        return "normal"
    return difficulty


def _show_settings_menu():
    from src.settingScreen import show_settings_menu

    show_settings_menu()
