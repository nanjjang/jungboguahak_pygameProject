"""스테이지 출구 문과 문 위 표지판 이미지를 그리는 파일."""

from functools import lru_cache

import pygame as pg

import load


DOOR_ANIMATION_MS = 220
DOOR_SCALE = 3
SIGN_SCALE = 2

# 일반 문과 보스 문은 서로 다른 스프라이트 행을 사용한다.
_DOOR_ROWS = {
    "normal": "row3",
    "boss": "row2",
}
_DOOR_SIGNS = {
    "normal": "top_04.png",
    "boss": "top_03.png",
}


def draw_stage_door(surface, goal_rect, camera_x, kind, open_progress):
    """문 열림 진행률에 맞는 프레임과 표지판을 화면에 그린다."""
    frames = _load_door_frames(kind)
    sign = _load_door_sign(kind)
    frame = frames[_frame_index(open_progress)]
    # goal_rect는 월드 좌표이므로 카메라 위치를 빼 화면 좌표로 바꾼다.
    screen_rect = goal_rect.move(-round(camera_x), 0)

    door_rect = frame.get_rect(midbottom=screen_rect.midbottom)
    surface.blit(frame, door_rect)

    sign_rect = sign.get_rect(midbottom=(screen_rect.centerx, door_rect.top + 8))
    surface.blit(sign, sign_rect)


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
def _load_door_sign(kind):
    """문 종류에 맞는 표지판 이미지를 불러온다."""
    return _load_scaled(_DOOR_SIGNS[kind], SIGN_SCALE)


def _load_scaled(filename, scale):
    """이미지를 읽고 지정 배율만큼 키워서 반환한다."""
    image = load.load_image(filename).convert_alpha()
    size = (
        round(image.get_width() * scale),
        round(image.get_height() * scale),
    )
    return pg.transform.scale(image, size)
