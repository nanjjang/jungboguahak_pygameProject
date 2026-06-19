"""게임 시작 전 타이틀 메뉴와 조작 방법 화면을 담당한다."""

from enum import Enum

import pygame as pg

import load
from src.constants import FPS, SCREEN_HEIGHT, SCREEN_WIDTH
from src.game_input import read_frame_input
from src import sfx


class TitleAction(Enum):
    """타이틀 화면에서 game_app.py로 돌려줄 사용자의 선택."""

    START = "start"
    INSTRUCTIONS = "instructions"
    QUIT = "quit"
    SETTINGS = "settings"


class TitleMenu:
    """선택 인덱스와 타이틀 배경 이미지를 보관하는 메뉴 객체."""

    def __init__(self):
        # selected_index는 START/INSTRUCTIONS/QUIT 중 현재 선택된 항목 위치이다.
        self.selected_index = 0
        self.actions = (
            TitleAction.START,
            TitleAction.INSTRUCTIONS,
            TitleAction.QUIT,
        )
        self.backgrounds = [
            _load_cover("menu1.png"),
            _load_cover("menu2.png"),
            _load_cover("menu3.png"),
        ]
        self.help_font = load.get_korean_font(18)

    def update(self, actions):
        """입력 상태를 받아 메뉴 선택을 바꾸거나 선택 결과를 반환한다."""
        if actions.title_quit_pressed:
            sfx.play_sfx("menu_confirm")
            return TitleAction.QUIT
        if actions.settings_pressed:
            sfx.play_sfx("menu_confirm")
            return TitleAction.SETTINGS
        moved = False
        if actions.up_pressed:
            self.selected_index = (self.selected_index - 1) % len(self.actions)
            moved = True
        if actions.down_pressed:
            self.selected_index = (self.selected_index + 1) % len(self.actions)
            moved = True
        if moved:
            sfx.play_sfx("menu_move", cooldown_ms=80)
        if actions.confirm_pressed:
            sfx.play_sfx("menu_confirm")
            return self.actions[self.selected_index]
        return None

    def draw(self, surface):
        """현재 선택된 메뉴에 맞는 배경과 하단 조작 안내를 그린다."""
        surface.blit(self.backgrounds[self.selected_index], (0, 0))
        guide_text = "↑ ↓ 선택    ENTER 결정    ESC 설정    Q 종료"
        guide_shadow = self.help_font.render(guide_text, True, (20, 20, 28))
        guide = self.help_font.render(guide_text, True, (255, 255, 255))
        guide_rect = guide.get_rect(center=(SCREEN_WIDTH // 2, 565))
        surface.blit(guide_shadow, guide_rect.move(2, 2))
        surface.blit(guide, guide_rect)


def show_title_screen(screen, clock):
    """사용자가 시작/조작 방법/종료 중 하나를 고를 때까지 타이틀 화면을 반복한다."""
    menu = TitleMenu()
    while True:
        clock.tick(FPS)
        actions = read_frame_input()
        if actions.quit_requested:
            return TitleAction.QUIT
        action = menu.update(actions)
        if action is not None:
            if action == TitleAction.INSTRUCTIONS:
                # 조작 방법 화면에서 돌아오면 타이틀 화면을 계속 보여준다.
                instruction_action = show_instructions(screen, clock)
                if instruction_action == TitleAction.QUIT:
                    return TitleAction.QUIT
                if instruction_action == TitleAction.SETTINGS:
                    return TitleAction.SETTINGS
                continue
            return action

        menu.draw(screen)
        pg.display.flip()


def show_instructions(screen, clock):
    """조작 방법 안내 화면을 그리고, ENTER를 누르면 타이틀로 돌아간다."""
    background = _load_cover("menu2.png")
    title_font = load.get_korean_font(34)
    line_font = load.get_korean_font(21)
    small_font = load.get_korean_font(17)
    lines = (
        "← / →        이동",
        "SPACE        점프",
        "SHIFT + SPACE 공중 유지",
        "Z            흡입",
        "X            발사",
        "↓            삼키기",
        "D / F        펀치 / 킥",
        "V            능력 공격",
        "문 앞에서 ↑   다음 스테이지",
        "R            게임오버/클리어 후 다시 시작",
    )

    while True:
        clock.tick(FPS)
        actions = read_frame_input()
        if actions.quit_requested or actions.title_quit_pressed:
            sfx.play_sfx("menu_confirm")
            return TitleAction.QUIT
        if actions.settings_pressed:
            sfx.play_sfx("menu_confirm")
            return TitleAction.SETTINGS
        if actions.confirm_pressed:
            sfx.play_sfx("menu_confirm")
            return None

        # 배경 위에 어두운 반투명 막을 깔아 안내 글자가 잘 보이게 한다.
        screen.blit(background, (0, 0))
        shade = pg.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pg.SRCALPHA)
        shade.fill((0, 0, 0, 92))
        screen.blit(shade, (0, 0))

        panel = pg.Rect(130, 62, 540, 468)
        # 조작 목록이 들어갈 흰색 안내 패널을 그린다.
        pg.draw.rect(screen, (255, 255, 250), panel, border_radius=18)
        pg.draw.rect(screen, (190, 24, 42), panel, width=6, border_radius=18)

        title = title_font.render("조작 방법", True, (35, 35, 45))
        screen.blit(title, title.get_rect(center=(panel.centerx, 112)))

        for index, line in enumerate(lines):
            text = line_font.render(line, True, (35, 35, 45))
            screen.blit(text, text.get_rect(topleft=(188, 158 + index * 32)))

        footer = small_font.render(
            "ENTER 로 메뉴로 돌아가기    ESC 설정    Q 종료",
            True,
            (110, 30, 45),
        )
        screen.blit(footer, footer.get_rect(center=(panel.centerx, 500)))
        pg.display.flip()


def _load_cover(filename):
    """메뉴 이미지를 화면을 꽉 채우는 배경으로 변환한다."""
    image = load.load_image(filename).convert()
    width, height = image.get_size()
    scale = max(SCREEN_WIDTH / width, SCREEN_HEIGHT / height)
    size = (round(width * scale), round(height * scale))
    image = pg.transform.smoothscale(image, size)
    x = (SCREEN_WIDTH - size[0]) // 2
    y = (SCREEN_HEIGHT - size[1]) // 2
    surface = pg.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    surface.blit(image, (x, y))
    return surface
