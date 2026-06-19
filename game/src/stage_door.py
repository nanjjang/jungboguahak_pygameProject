"""스테이지 출구 문과 문 위 표지판 이미지를 그리는 파일."""

from functools import lru_cache
from pathlib import Path

import pygame as pg

import load


DOOR_ANIMATION_MS = 220
DOOR_SCALE = 3
SIGN_SCALE = 2
STAGE_PARTS_ROOT = Path(__file__).resolve().parent / "assets" / "scenery" / "stage_parts"
CAVE_DOOR_SIZE = (54, 82)
CAVE_DOOR_OPENING_MIDBOTTOM = (28, 64)

# 일반 문과 보스 문은 서로 다른 스프라이트 행을 사용한다.
_DOOR_ROWS = {
    "normal": "row3",
    "boss": "row2",
}


def draw_stage_door(surface, goal_rect, camera_x, kind, open_progress):
    """문 열림 진행률에 맞는 프레임과 표지판을 화면에 그린다."""
    frames = _load_door_frames(kind)
    frame = frames[_frame_index(open_progress)]
    # goal_rect는 월드 좌표이므로 카메라 위치를 빼 화면 좌표로 바꾼다.
    screen_rect = goal_rect.move(-round(camera_x), 0)

    door_rect = frame.get_rect(midbottom=screen_rect.midbottom)
    surface.blit(frame, door_rect)


def draw_cave_door(surface, door_rect, camera_x, open_progress=0.0):
    """로컬 이동에 쓰는 동굴문을 검은 입구 핫스팟에 맞춰 그린다."""
    frame = _load_cave_door()
    screen_rect = door_rect.move(-round(camera_x), 0)
    sprite_x = screen_rect.centerx - CAVE_DOOR_OPENING_MIDBOTTOM[0]
    sprite_y = screen_rect.bottom - CAVE_DOOR_OPENING_MIDBOTTOM[1]
    surface.blit(frame, (sprite_x, sprite_y))

    if open_progress <= 0:
        return

    glow = pg.Surface((screen_rect.width + 18, screen_rect.height + 18), pg.SRCALPHA)
    alpha = round(52 + 48 * open_progress)
    pg.draw.ellipse(glow, (190, 235, 255, alpha), glow.get_rect())
    surface.blit(glow, glow.get_rect(center=screen_rect.center), special_flags=pg.BLEND_ADD)


def _frame_index(open_progress):
    """0.0~1.0 열림 진행률을 0, 1, 2번 문 프레임으로 변환한다."""
    if open_progress < 1 / 3:
        return 0
    if open_progress < 2 / 3:
        return 1
    return 2


@lru_cache(maxsize=None)
def _load_door_frames(kind):
    """문 프레임 이미지를 한 번만 불러와 캐시에 저장한다."""
    row = _DOOR_ROWS[kind]
    frames = []
    for index in range(1, 4):
        frames.append(_load_scaled(f"{row}_{index:02d}.png", DOOR_SCALE))
    return frames


@lru_cache(maxsize=None)
def _load_scaled(filename, scale):
    """이미지를 읽고 지정 배율만큼 키워서 반환한다."""
    image = load.load_image(filename).convert_alpha()
    size = (
        round(image.get_width() * scale),
        round(image.get_height() * scale),
    )
    return pg.transform.scale(image, size)


@lru_cache(maxsize=None)
def _load_cave_door():
    """잘라낸 동굴문 이미지를 게임 안 크기로 키워서 반환한다."""
    image = pg.image.load(STAGE_PARTS_ROOT / "cave_door.png").convert_alpha()
    return pg.transform.scale(image, CAVE_DOOR_SIZE)
