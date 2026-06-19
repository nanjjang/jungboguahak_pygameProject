import pygame as pg


DOOR_ANIMATION_MS = 220


class DoorAnimation:
    """문 열림/닫힘 상태와 애니메이션 진행률을 관리한다."""

    def __init__(self, duration_ms=DOOR_ANIMATION_MS):
        self.duration_ms = duration_ms
        self.is_open = False
        self.changed_at = pg.time.get_ticks() - duration_ms

    def reset(self, is_open=False):
        """현재 상태를 애니메이션 없이 즉시 적용한다."""
        self.is_open = is_open
        self.changed_at = pg.time.get_ticks() - self.duration_ms

    def set_open(self, is_open):
        """열림 상태가 바뀌면 애니메이션 시작 시간을 갱신한다."""
        if is_open != self.is_open:
            self.is_open = is_open
            self.changed_at = pg.time.get_ticks()

    def progress(self):
        """0.0은 닫힘, 1.0은 열림 상태를 뜻한다."""
        if self.duration_ms <= 0:
            return 1.0 if self.is_open else 0.0

        elapsed = pg.time.get_ticks() - self.changed_at
        progress = min(1.0, elapsed / self.duration_ms)
        if self.is_open:
            return progress
        return 1.0 - progress


def door_frame_index(open_progress):
    """0.0~1.0 열림 진행률을 0, 1, 2번 문 프레임으로 변환한다."""
    if open_progress < 1 / 3:
        return 0
    if open_progress < 2 / 3:
        return 1
    return 2
