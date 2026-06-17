from enum import Enum

import pygame as pg

import load
from src.constants import FPS, SCREEN_HEIGHT, SCREEN_WIDTH


class TitleAction(Enum):
    START = "start"
    INSTRUCTIONS = "instructions"
    QUIT = "quit"


class TitleButton(pg.sprite.Sprite):
    def __init__(self, rect, action):
        super().__init__()
        self.image = pg.Surface(rect.size, pg.SRCALPHA)
        self.rect = rect
        self.action = action
        self.mouse_over = False

    def update(self, mouse_pos, mouse_up):
        self.mouse_over = self.rect.collidepoint(mouse_pos)
        if self.mouse_over and mouse_up:
            return self.action
        return None


class TitleMenu:
    def __init__(self):
        self.selected_index = 0
        self.backgrounds = [
            _load_cover("menu1.png"),
            _load_cover("menu2.png"),
            _load_cover("menu3.png"),
        ]
        self.buttons = pg.sprite.RenderUpdates(
            TitleButton(_menu_rect(0, 134, 244, 51), TitleAction.START),
            TitleButton(_menu_rect(0, 185, 244, 51), TitleAction.INSTRUCTIONS),
            TitleButton(_menu_rect(0, 236, 244, 51), TitleAction.QUIT),
        )
        self.help_font = load.get_korean_font(18)

    def handle_key(self, event):
        if event.type != pg.KEYDOWN:
            return None
        if event.key in (pg.K_UP, pg.K_w):
            self.selected_index = (self.selected_index - 1) % len(self.buttons)
        elif event.key in (pg.K_DOWN, pg.K_s):
            self.selected_index = (self.selected_index + 1) % len(self.buttons)
        elif event.key in (pg.K_RETURN, pg.K_KP_ENTER, pg.K_SPACE):
            return self._selected_button().action
        elif event.key == pg.K_ESCAPE:
            return TitleAction.QUIT
        return None

    def update(self, mouse_pos, mouse_up):
        for index, button in enumerate(self.buttons):
            action = button.update(mouse_pos, mouse_up)
            if button.mouse_over:
                self.selected_index = index
            if action is not None:
                return action
        return None

    def draw(self, surface):
        surface.blit(self.backgrounds[self.selected_index], (0, 0))
        guide_text = "↑ ↓ / 마우스 선택    ENTER / 클릭 결정    ESC 종료"
        guide_shadow = self.help_font.render(guide_text, True, (20, 20, 28))
        guide = self.help_font.render(guide_text, True, (255, 255, 255))
        guide_rect = guide.get_rect(center=(SCREEN_WIDTH // 2, 565))
        surface.blit(guide_shadow, guide_rect.move(2, 2))
        surface.blit(guide, guide_rect)

    def _selected_button(self):
        return self.buttons.sprites()[self.selected_index]


def show_title_screen(screen, clock):
    menu = TitleMenu()
    while True:
        clock.tick(FPS)
        mouse_up = False
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return TitleAction.QUIT
            if event.type == pg.MOUSEBUTTONUP and event.button == 1:
                mouse_up = True
            action = menu.handle_key(event)
            if action is not None:
                if action == TitleAction.INSTRUCTIONS:
                    instruction_action = show_instructions(screen, clock)
                    if instruction_action == TitleAction.QUIT:
                        return TitleAction.QUIT
                    continue
                return action

        action = menu.update(pg.mouse.get_pos(), mouse_up)
        if action is not None:
            if action == TitleAction.INSTRUCTIONS:
                instruction_action = show_instructions(screen, clock)
                if instruction_action == TitleAction.QUIT:
                    return TitleAction.QUIT
                continue
            return action

        menu.draw(screen)
        pg.display.flip()


def show_instructions(screen, clock):
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
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return TitleAction.QUIT
            if event.type == pg.MOUSEBUTTONUP and event.button == 1:
                return None
            if event.type == pg.KEYDOWN and event.key in (
                pg.K_ESCAPE,
                pg.K_RETURN,
                pg.K_KP_ENTER,
                pg.K_SPACE,
            ):
                return None

        screen.blit(background, (0, 0))
        shade = pg.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pg.SRCALPHA)
        shade.fill((0, 0, 0, 92))
        screen.blit(shade, (0, 0))

        panel = pg.Rect(130, 62, 540, 468)
        pg.draw.rect(screen, (255, 255, 250), panel, border_radius=18)
        pg.draw.rect(screen, (190, 24, 42), panel, width=6, border_radius=18)

        title = title_font.render("조작 방법", True, (35, 35, 45))
        screen.blit(title, title.get_rect(center=(panel.centerx, 112)))

        for index, line in enumerate(lines):
            text = line_font.render(line, True, (35, 35, 45))
            screen.blit(text, text.get_rect(topleft=(188, 158 + index * 32)))

        footer = small_font.render(
            "클릭 / ENTER / ESC 로 메뉴로 돌아가기",
            True,
            (110, 30, 45),
        )
        screen.blit(footer, footer.get_rect(center=(panel.centerx, 500)))
        pg.display.flip()


def _load_cover(filename):
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


def _menu_rect(x, y, width, height):
    scale = max(SCREEN_WIDTH / 600, SCREEN_HEIGHT / 400)
    left = round(x * scale + (SCREEN_WIDTH - 600 * scale) / 2)
    top = round(y * scale + (SCREEN_HEIGHT - 400 * scale) / 2)
    return pg.Rect(left, top, round(width * scale), round(height * scale))
