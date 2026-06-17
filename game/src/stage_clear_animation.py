"""스테이지 클리어 때 Kirby가 문 쪽으로 들어가는 연출을 그리는 파일."""

from functools import lru_cache

import pygame as pg

import load


FRAME_MS = 55
DANCE_FRAME_SIZE = (150, 112)
ENTRY_MS = 360
# 엔딩 프레임 이미지는 assets/images/ending 폴더에서 순서대로 읽는다.
_FRAME_DIR = load.IMAGE_ROOT / "ending"
_FRAME_PATTERN = "kirby_frame_*.jpg"


@lru_cache(maxsize=1)
def _frame_names():
    """프레임 파일 이름 목록을 한 번만 찾아 캐시에 저장한다."""
    return tuple(path.name for path in sorted(_FRAME_DIR.glob(_FRAME_PATTERN)))


def animation_duration_ms():
    """전체 클리어 연출이 몇 ms 동안 재생되는지 계산한다."""
    return max(1, len(_frame_names())) * FRAME_MS


def draw_stage_clear_animation(surface, started_at, player_rect, goal_rect, camera_x):
    """클리어 연출 프레임을 현재 시간에 맞춰 화면에 그린다."""
    frames = _load_frames()
    if not frames:
        return

    elapsed = pg.time.get_ticks() - started_at
    # elapsed를 프레임 번호로 바꿔 현재 보여줄 이미지를 고른다.
    index = min(len(frames) - 1, elapsed // FRAME_MS)
    duration = animation_duration_ms()
    entry_progress = _entry_progress(elapsed, duration)
    image = _entry_frame(frames[index], entry_progress)

    world_x = _lerp(player_rect.centerx, goal_rect.centerx, entry_progress)
    # 월드 좌표에서 카메라 위치를 빼 화면 좌표로 변환한다.
    screen_x = round(world_x - camera_x)
    image_rect = image.get_rect(midbottom=(screen_x, player_rect.bottom))
    surface.blit(image, image_rect)


@lru_cache(maxsize=1)
def _load_frames():
    """이미지 파일을 pygame Surface로 불러와 같은 크기로 맞춘 뒤 캐시한다."""
    frames = []
    for filename in _frame_names():
        frame = load.load_image(f"ending/{filename}").convert()
        frames.append(pg.transform.scale(frame, DANCE_FRAME_SIZE).convert_alpha())
    return tuple(frames)


def _entry_progress(elapsed, duration):
    """연출 마지막 ENTRY_MS 동안 문 안으로 들어가는 진행률을 계산한다."""
    entry_start = max(0, duration - ENTRY_MS)
    if elapsed <= entry_start:
        return 0.0
    return min(1.0, (elapsed - entry_start) / ENTRY_MS)


def _entry_frame(frame, progress):
    """문으로 들어가는 동안 이미지가 작아지고 흐려지는 효과를 만든다."""
    if progress <= 0:
        return frame

    scale = 1.0 - 0.35 * progress
    size = (
        max(1, round(frame.get_width() * scale)),
        max(1, round(frame.get_height() * scale)),
    )
    image = pg.transform.scale(frame, size).convert_alpha()
    image.set_alpha(round(255 * (1.0 - 0.75 * progress)))
    return image


def _lerp(start, end, progress):
    """start에서 end까지 progress 비율만큼 보간한 값을 반환한다."""
    return start + (end - start) * progress
