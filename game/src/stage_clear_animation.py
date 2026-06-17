from functools import lru_cache

import pygame as pg

import load


FRAME_MS = 55
DANCE_FRAME_SIZE = (150, 112)
ENTRY_MS = 360
_FRAME_DIR = load.IMAGE_ROOT / "ending"
_FRAME_PATTERN = "kirby_frame_*.jpg"


@lru_cache(maxsize=1)
def _frame_names():
    return tuple(path.name for path in sorted(_FRAME_DIR.glob(_FRAME_PATTERN)))


def animation_duration_ms():
    return max(1, len(_frame_names())) * FRAME_MS


def draw_stage_clear_animation(surface, started_at, player_rect, goal_rect, camera_x):
    frames = _load_frames()
    if not frames:
        return

    elapsed = pg.time.get_ticks() - started_at
    index = min(len(frames) - 1, elapsed // FRAME_MS)
    duration = animation_duration_ms()
    entry_progress = _entry_progress(elapsed, duration)
    image = _entry_frame(frames[index], entry_progress)

    world_x = _lerp(player_rect.centerx, goal_rect.centerx, entry_progress)
    screen_x = round(world_x - camera_x)
    image_rect = image.get_rect(midbottom=(screen_x, player_rect.bottom))
    surface.blit(image, image_rect)


@lru_cache(maxsize=1)
def _load_frames():
    frames = []
    for filename in _frame_names():
        frame = load.load_image(f"ending/{filename}").convert()
        frames.append(pg.transform.scale(frame, DANCE_FRAME_SIZE).convert_alpha())
    return tuple(frames)


def _entry_progress(elapsed, duration):
    entry_start = max(0, duration - ENTRY_MS)
    if elapsed <= entry_start:
        return 0.0
    return min(1.0, (elapsed - entry_start) / ENTRY_MS)


def _entry_frame(frame, progress):
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
    return start + (end - start) * progress
