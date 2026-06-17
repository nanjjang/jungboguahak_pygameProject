"""타이틀 화면 다음에 보여주는 난이도 선택 화면."""

from pathlib import Path
import pygame as pg

import load
from src.constants import SCREEN_HEIGHT, SCREEN_WIDTH


SCENERY_ROOT = Path(__file__).resolve().parent / "assets" / "scenery"

# 게임 내부에서 실제로 쓰는 난이도 이름이다.
# constants.py의 DIFFICULTY_SETTINGS 키와 같은 문자열이어야 한다.
DIFFICULTIES = ["easy", "normal", "hard"]

# 난이도마다 보여줄 배경 이미지 파일명이다.
# 파일은 game/src/assets/scenery 폴더 안에 있어야 한다.
DIFFICULTY_IMAGES = [
    "difficulty_easy.png",
    "difficulty_normal.png",
    "difficulty_hard.png",
]

# 이미지가 화면을 꽉 채우지 못할 때 뒤에 깔리는 배경색이다.
BACKGROUND_COLORS = [
    (248, 169, 24),
    (224, 82, 14),
    (120, 12, 8),
]


def select_difficulty(screen, clock, initial="normal"):
    """사용자가 난이도를 고를 때까지 선택 화면을 반복해서 보여준다."""
    selected_index = 1
    if initial in DIFFICULTIES:
        selected_index = DIFFICULTIES.index(initial)

    font = load.get_korean_font(18)
    images = []
    for filename in DIFFICULTY_IMAGES:
        images.append(load_difficulty_image(filename))

    while True:
        # clock.tick(60)은 선택 화면이 초당 60번보다 빨리 돌지 않게 제한한다.
        clock.tick(60)

        for event in pg.event.get():
            if event.type == pg.QUIT:
                # 창 닫기 버튼은 "이전"이 아니라 게임 종료 요청으로 처리한다.
                return pg.QUIT

            if event.type != pg.KEYDOWN:
                continue

            if event.key in (pg.K_UP, pg.K_RIGHT):
                # 위/오른쪽 키는 더 어려운 난이도 쪽으로 이동한다.
                selected_index += 1
                if selected_index >= len(DIFFICULTIES):
                    selected_index = len(DIFFICULTIES) - 1
            elif event.key in (pg.K_DOWN, pg.K_LEFT):
                # 아래/왼쪽 키는 더 쉬운 난이도 쪽으로 이동한다.
                selected_index -= 1
                if selected_index < 0:
                    selected_index = 0
            elif event.key in (pg.K_RETURN, pg.K_KP_ENTER, pg.K_SPACE):
                # 결정 키를 누르면 선택한 난이도 문자열을 game_app.py로 돌려준다.
                return DIFFICULTIES[selected_index]
            elif event.key == pg.K_ESCAPE:
                # ESC는 게임 종료가 아니라 타이틀 화면으로 돌아가기 위해 None을 돌려준다.
                return None

        # 현재 선택된 난이도에 맞는 배경색과 이미지를 그린다.
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
    """난이도 선택용 이미지를 화면 안에 들어오도록 비율 유지해서 불러온다."""
    image_path = SCENERY_ROOT / filename
    image = pg.image.load(image_path).convert()
    scale = min(SCREEN_WIDTH / image.get_width(), SCREEN_HEIGHT / image.get_height())
    new_width = round(image.get_width() * scale)
    new_height = round(image.get_height() * scale)
    return pg.transform.smoothscale(image, (new_width, new_height))
