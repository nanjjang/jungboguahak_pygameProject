from pathlib import Path

import pygame as pg

import load
from src.constants import SCREEN_HEIGHT, SCREEN_WIDTH


SCENERY_ROOT = Path(__file__).resolve().parent / "assets" / "scenery"
DIFFICULTY_ORDER = ("easy", "normal", "hard")
DIFFICULTY_IMAGES = {
    "easy": "09_17_56",
    "normal": "09_26_19",
    "hard": "09_22_20",
}
DIFFICULTY_LABELS = {
    "easy": "EASY",
    "normal": "NORMAL",
    "hard": "HARD",
}


class DifficultyMenu:
    def __init__(self):
        self.selected_index = 1
        self.confirmed = False
        self.cancelled = False
        self.font = load.get_korean_font(18)
        self.images = {
            difficulty: _load_difficulty_screen(timestamp)
            for difficulty, timestamp in DIFFICULTY_IMAGES.items()
        }

    @property
    def difficulty(self):
        return DIFFICULTY_ORDER[self.selected_index]

    def handle_event(self, event):
        if event.type == pg.QUIT:
            self.cancelled = True
            return
        if event.type != pg.KEYDOWN:
            return
        if event.key in (pg.K_UP, pg.K_w, pg.K_RIGHT, pg.K_d):
            self.selected_index = min(
                len(DIFFICULTY_ORDER) - 1,
                self.selected_index + 1,
            )
        elif event.key in (pg.K_DOWN, pg.K_s, pg.K_LEFT, pg.K_a):
            self.selected_index = max(0, self.selected_index - 1)
        elif event.key in (pg.K_RETURN, pg.K_KP_ENTER, pg.K_SPACE):
            self.confirmed = True
        elif event.key == pg.K_ESCAPE:
            self.cancelled = True

    def draw(self, surface):
        difficulty = self.difficulty
        surface.fill(_backdrop_color(difficulty))
        image = self.images[difficulty]
        image_rect = image.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        surface.blit(image, image_rect)
        self._draw_controls(surface, difficulty)

    def _draw_controls(self, surface, difficulty):
        label = DIFFICULTY_LABELS[difficulty]
        guide_text = f"{label}   ↑↓/←→ 선택     ENTER/SPACE 결정     ESC 종료"
        shadow = self.font.render(guide_text, True, (80, 25, 15))
        guide = self.font.render(guide_text, True, (255, 255, 255))
        rect = guide.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 30))
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


def _load_difficulty_screen(timestamp):
    path = _find_difficulty_image(timestamp)
    image = pg.image.load(path).convert()
    scale = min(SCREEN_WIDTH / image.get_width(), SCREEN_HEIGHT / image.get_height())
    size = (
        round(image.get_width() * scale),
        round(image.get_height() * scale),
    )
    return pg.transform.smoothscale(image, size)


def _find_difficulty_image(timestamp):
    matches = sorted(SCENERY_ROOT.glob(f"ChatGPT Image*{timestamp}.png"))
    if not matches:
        raise FileNotFoundError(f"Difficulty image not found: {timestamp}")
    return matches[0]


def _backdrop_color(difficulty):
    if difficulty == "hard":
        return (120, 12, 8)
    if difficulty == "normal":
        return (224, 82, 14)
    return (248, 169, 24)
