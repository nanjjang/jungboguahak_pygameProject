import pygame as pg


DOOR_ANIMATION_MS = 220


class DoorAnimation:
    # 문 애니메이션

    def __init__(self, duration_ms=DOOR_ANIMATION_MS):
        self.duration_ms = duration_ms
        self.is_open = False
        self.changed_at = pg.time.get_ticks() - duration_ms

    def reset(self, is_open=False):
        # 바로 적용
        self.is_open = is_open
        self.changed_at = pg.time.get_ticks() - self.duration_ms

    def set_open(self, is_open):
        # 열고 닫기
        if is_open != self.is_open:
            self.is_open = is_open
            self.changed_at = pg.time.get_ticks()

    def progress(self):
        # 진행률
        if self.duration_ms <= 0:
            return 1.0 if self.is_open else 0.0

        elapsed = pg.time.get_ticks() - self.changed_at
        progress = min(1.0, elapsed / self.duration_ms)
        if self.is_open:
            return progress
        return 1.0 - progress


def door_frame_index(open_progress):
    # 문 프레임
    if open_progress < 1 / 3:
        return 0
    if open_progress < 2 / 3:
        return 1
    return 2
