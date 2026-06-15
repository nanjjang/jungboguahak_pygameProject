import math
import random

import pygame as pg

import load
from src.constants import SCREEN_HEIGHT, SCREEN_WIDTH


DIFFICULTY_ORDER = ("easy", "normal", "hard")
DIFFICULTY_PRESENTATION = {
    "easy": {
        "name": "easy",
        "subtitle": "처음 모험하는 사용자에게 추천",
        "color": (75, 195, 95),
        "dark": (24, 125, 66),
        "enemy": "몬스터 느림",
        "damage": "피해 적음",
        "spice": 1,
    },
    "normal": {
        "name": "normal",
        "subtitle": "기본 난이도",
        "color": (255, 154, 34),
        "dark": (205, 75, 25),
        "enemy": "비교적 둔함",
        "damage": "기본 피해량",
        "spice": 2,
    },
    "hard": {
        "name": "hard",
        "subtitle": "빠른 반응과 강한 공격을 조심하세요",
        "color": (235, 48, 54),
        "dark": (145, 18, 50),
        "enemy": "몬스터 움직임 빠름!!",
        "damage": "몬스터 증가 및 피해량 증가",
        "spice": 3,
    },
}


class DifficultyMenu:
    def __init__(self):
        self.selected_index = 1
        self.confirmed = False
        self.cancelled = False
        self.title_font = load.get_korean_font(46)
        self.large_font = load.get_korean_font(32)
        self.medium_font = load.get_korean_font(22)
        self.small_font = load.get_korean_font(17)
        self.kirby = load.load_image("KSSU_Kirby_Hover_sprite.png").convert_alpha()
        self.kirby = pg.transform.scale(self.kirby, (176, 187))
        self.potion = load.load_image("potion.png").convert_alpha()
        self.potion = pg.transform.scale(self.potion, (72, 72))
        rng = random.Random(17)
        self.confetti = [
            (
                rng.randrange(0, SCREEN_WIDTH),
                rng.randrange(40, SCREEN_HEIGHT - 40),
                rng.randrange(7, 19),
                rng.choice(((255, 218, 45), (255, 240, 120), (255, 128, 35))),
            )
            for _ in range(34)
        ]

    @property
    def difficulty(self):
        return DIFFICULTY_ORDER[self.selected_index]

    def handle_event(self, event):
        if event.type == pg.QUIT:
            self.cancelled = True
            return
        if event.type != pg.KEYDOWN:
            return
        if event.key in (pg.K_UP, pg.K_w):
            self.selected_index = min(
                len(DIFFICULTY_ORDER) - 1,
                self.selected_index + 1,
            )
        elif event.key in (pg.K_DOWN, pg.K_s):
            self.selected_index = max(0, self.selected_index - 1)
        elif event.key in (pg.K_RETURN, pg.K_KP_ENTER, pg.K_SPACE):
            self.confirmed = True
        elif event.key == pg.K_ESCAPE:
            self.cancelled = True

    def draw(self, surface):
        data = DIFFICULTY_PRESENTATION[self.difficulty]
        self._draw_background(surface, data)
        self._draw_gauge(surface)
        self._draw_info_card(surface, data)
        self._draw_plate(surface, data)
        self._draw_kirby(surface, data)
        self._draw_controls(surface)

    def _draw_background(self, surface, data):
        top = data["color"]
        bottom = (255, 205, 35) if self.difficulty != "hard" else (245, 90, 35)
        for y in range(SCREEN_HEIGHT):
            ratio = y / SCREEN_HEIGHT
            color = tuple(
                round(top[i] * (1 - ratio) + bottom[i] * ratio) for i in range(3)
            )
            pg.draw.line(surface, color, (0, y), (SCREEN_WIDTH, y))

        for x, y, size, color in self.confetti:
            shade = (*color, 80)
            tile = pg.Surface((size, size), pg.SRCALPHA)
            tile.fill(shade)
            surface.blit(tile, (x, y))

        pg.draw.polygon(
            surface,
            (205, 20, 38),
            ((0, 0), (SCREEN_WIDTH, 0), (SCREEN_WIDTH, 58), (0, 86)),
        )
        pg.draw.polygon(
            surface,
            (255, 115, 24),
            (
                (0, 535),
                (SCREEN_WIDTH, 510),
                (SCREEN_WIDTH, SCREEN_HEIGHT),
                (0, SCREEN_HEIGHT),
            ),
        )
        title = self.title_font.render("난이도 선택", True, (255, 255, 255))
        shadow = self.title_font.render("난이도 선택", True, (55, 37, 120))
        title_rect = title.get_rect(topright=(SCREEN_WIDTH - 35, 24))
        surface.blit(shadow, title_rect.move(4, 4))
        surface.blit(title, title_rect)

    def _draw_gauge(self, surface):
        outer = pg.Rect(48, 105, 142, 356)
        pg.draw.rect(surface, (28, 35, 110), outer, border_radius=24)
        pg.draw.rect(surface, (255, 117, 35), outer.inflate(-18, -18), border_radius=17)
        tube = pg.Rect(82, 135, 54, 285)
        pg.draw.rect(surface, (255, 245, 210), tube, border_radius=12)

        segment_height = tube.height / 3
        colors = ((70, 205, 95), (255, 174, 32), (235, 48, 54))
        for index, color in enumerate(colors):
            y = round(tube.bottom - segment_height * (index + 1))
            rect = pg.Rect(
                tube.x + 7, y + 4, tube.width - 14, round(segment_height - 8)
            )
            pg.draw.rect(surface, color, rect, border_radius=5)

        marker_y = round(tube.bottom - segment_height * (self.selected_index + 0.5))
        pg.draw.polygon(
            surface,
            (255, 245, 75),
            ((139, marker_y), (177, marker_y - 22), (177, marker_y + 22)),
        )
        pg.draw.polygon(
            surface,
            (31, 39, 115),
            ((146, marker_y), (169, marker_y - 13), (169, marker_y + 13)),
        )

        label = self.medium_font.render(
            f"LEVEL {self.selected_index + 1}",
            True,
            (255, 255, 255),
        )
        surface.blit(label, label.get_rect(center=(outer.centerx, 443)))

    def _draw_info_card(self, surface, data):
        outer = pg.Rect(214, 112, 385, 225)
        pg.draw.ellipse(surface, (28, 38, 120), outer)
        inner = outer.inflate(-25, -25)
        pg.draw.ellipse(surface, data["dark"], inner)

        level = self.large_font.render(
            str(self.selected_index + 1),
            True,
            (255, 255, 255),
        )
        level_badge = pg.Rect(232, 91, 72, 72)
        pg.draw.ellipse(surface, (255, 218, 45), level_badge)
        pg.draw.ellipse(surface, (28, 38, 120), level_badge, 6)
        surface.blit(level, level.get_rect(center=level_badge.center))

        name = self.large_font.render(data["name"], True, (255, 255, 255))
        surface.blit(name, name.get_rect(center=(outer.centerx, 174)))
        subtitle = self.small_font.render(data["subtitle"], True, (255, 239, 188))
        surface.blit(subtitle, subtitle.get_rect(center=(outer.centerx, 214)))

        rows = (
            ("몬스터", data["enemy"]),
            ("전투", data["damage"]),
        )
        for row, (label, value) in enumerate(rows):
            y = 250 + row * 35
            pg.draw.rect(surface, (110, 30, 45), (280, y, 250, 27), border_radius=13)
            text = self.small_font.render(f"{label}   {value}", True, (255, 255, 255))
            surface.blit(text, text.get_rect(center=(405, y + 13)))

    def _draw_plate(self, surface, data):
        pg.draw.ellipse(surface, (215, 220, 230), (245, 414, 375, 128))
        pg.draw.ellipse(surface, (255, 255, 250), (260, 400, 345, 124))
        pg.draw.ellipse(surface, data["dark"], (300, 427, 265, 76))

        for index in range(data["spice"] + 2):
            x = 335 + index * 46
            y = 461 + round(math.sin(index * 1.7) * 12)
            pg.draw.circle(surface, data["color"], (x, y), 12)
            pg.draw.circle(surface, (255, 220, 60), (x, y), 5)

        bottle = self.potion
        surface.blit(bottle, bottle.get_rect(midbottom=(564, 442)))

    def _draw_kirby(self, surface, data):
        bob = round(math.sin(pg.time.get_ticks() / 230) * 5)
        kirby_rect = self.kirby.get_rect(midbottom=(690, 482 + bob))
        surface.blit(self.kirby, kirby_rect)

    def _draw_controls(self, surface):
        guide = self.medium_font.render(
            "↑ ↓  선택       ENTER / SPACE  결정       ESC  종료",
            True,
            (255, 255, 255),
        )
        shadow = self.medium_font.render(
            "↑ ↓  선택       ENTER / SPACE  결정       ESC  종료",
            True,
            (50, 34, 105),
        )
        rect = guide.get_rect(center=(SCREEN_WIDTH // 2, 566))
        surface.blit(shadow, rect.move(2, 2))
        surface.blit(guide, rect)


def select_difficulty(screen, clock):
    menu = DifficultyMenu()
    while not menu.confirmed and not menu.cancelled:
        clock.tick(60)
        for event in pg.event.get():
            menu.handle_event(event)
        menu.draw(screen)
        pg.display.flip()
    return None if menu.cancelled else menu.difficulty
