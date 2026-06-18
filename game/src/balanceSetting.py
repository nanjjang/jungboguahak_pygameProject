"""난이도 선택 화면."""

from pathlib import Path
import pygame as pg

import load
from src.constants import SCREEN_HEIGHT, SCREEN_WIDTH


SCENERY_ROOT = Path(__file__).resolve().parent / "assets" / "scenery"

DIFFICULTIES = ["easy", "normal", "hard"]

DIFFICULTY_IMAGES = [
    "difficulty_easy.png",
    "difficulty_normal.png",
    "difficulty_hard.png",
]

BACKGROUND_COLORS = [
    (248, 169, 24),
    (224, 82, 14),
    (120, 12, 8),
]


def select_difficulty(screen, clock, initial="normal"):
    selected_index = 1
    if initial in DIFFICULTIES:
        selected_index = DIFFICULTIES.index(initial)

    font = load.get_korean_font(18)
    images = []
    for filename in DIFFICULTY_IMAGES:
        images.append(load_difficulty_image(filename))

    while True:
        clock.tick(60)

        for event in pg.event.get():
            if event.type == pg.QUIT:
                return "quit"

            if event.type != pg.KEYDOWN:
                continue

            if event.key in (pg.K_UP, pg.K_RIGHT):
                selected_index += 1
                if selected_index >= len(DIFFICULTIES):
                    selected_index = len(DIFFICULTIES) - 1
            elif event.key in (pg.K_DOWN, pg.K_LEFT):
                selected_index -= 1
                if selected_index < 0:
                    selected_index = 0
            elif event.key in (pg.K_RETURN, pg.K_KP_ENTER, pg.K_SPACE):
                return DIFFICULTIES[selected_index]
            elif event.key == pg.K_ESCAPE:
                return None

        screen.fill(BACKGROUND_COLORS[selected_index])

        image = images[selected_index]
        image_rect = image.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        screen.blit(image, image_rect)

        guide_text = (
            f"{DIFFICULTIES[selected_index].upper()}   "
            "UP/DOWN 선택     ENTER/SPACE 결정     ESC 이전"
        )
        shadow = font.render(guide_text, True, (80, 25, 15))
        text = font.render(guide_text, True, (255, 255, 255))
        text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 30))
        screen.blit(shadow, text_rect.move(2, 2))
        screen.blit(text, text_rect)

        pg.display.flip()


def load_difficulty_image(filename):
    image_path = SCENERY_ROOT / filename
    image = pg.image.load(image_path).convert()
    scale = min(SCREEN_WIDTH / image.get_width(), SCREEN_HEIGHT / image.get_height())
    new_width = round(image.get_width() * scale)
    new_height = round(image.get_height() * scale)
    return pg.transform.smoothscale(image, (new_width, new_height))
