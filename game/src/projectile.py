"""Kirby가 뱉거나 능력으로 만든 발사체 Sprite를 정의한다."""

import pygame as pg

from src.constants import ELEMENTS, SCREEN_HEIGHT, SCREEN_WIDTH


class Projectile(pg.sprite.Sprite):
    """화면을 날아가 적에게 피해를 주는 플레이어 발사체."""

    def __init__(
        self,
        x,
        y,
        facing_right,
        element="star",
        world_width=SCREEN_WIDTH,
    ):
        super().__init__()
        self.element = element
        # ELEMENTS 설정에서 속성별 속도, 중력, 데미지, 색을 가져온다.
        cfg = ELEMENTS[element]
        self.dx = cfg["proj_speed"] if facing_right else -cfg["proj_speed"]
        self.dy = float(cfg["proj_dy"])
        self.gravity = cfg["proj_gravity"]
        self.damage = cfg["damage"]
        self.world_width = world_width
        self.image = self._make_image(cfg["proj_size"], cfg["color"])
        self.rect = self.image.get_rect(center=(x, y))
        self._y_float = float(y)

    def update(self):
        """속도와 중력을 적용하고, 화면 밖으로 나가면 제거한다."""
        self.dy += self.gravity
        self.rect.x += int(self.dx)
        self._y_float += self.dy
        self.rect.y = int(self._y_float)
        if (
            self.rect.right < 0
            or self.rect.left > self.world_width
            or self.rect.top > SCREEN_HEIGHT
        ):
            self.kill()

    # -------------------------------------------------------------- private
    def _make_image(self, size, color):
        """속성 이름에 맞는 그리기 함수를 골라 발사체 이미지를 만든다."""
        surf = pg.Surface((size, size), pg.SRCALPHA)
        draw = _DRAWERS.get(self.element, _draw_star)
        draw(surf, size, color)
        return surf


# 속성별 모양 함수 — 새 속성 추가 시 함수만 등록하면 됨
def _draw_star(surf, size, color):
    """별 모양 기본 발사체를 그린다."""
    points = [
        (size // 2, 0),
        (size * 6 // 10, size * 3 // 10),
        (size, size * 3 // 10),
        (size * 7 // 10, size * 6 // 10),
        (size * 8 // 10, size),
        (size // 2, size * 7 // 10),
        (size * 2 // 10, size),
        (size * 3 // 10, size * 6 // 10),
        (0, size * 3 // 10),
        (size * 4 // 10, size * 3 // 10),
    ]
    pg.draw.polygon(surf, color, points)


def _draw_fire(surf, size, color):
    """불 속성 발사체를 원형 불꽃 느낌으로 그린다."""
    pg.draw.circle(surf, color, (size // 2, size // 2), size // 2)
    pg.draw.circle(surf, (255, 200, 50), (size // 2, size // 2), size // 4)


def _draw_electric(surf, size, color):
    """전기 속성 발사체를 번개 모양으로 그린다."""
    s = size
    pts = [
        (s * 0.55, 0),
        (s * 0.25, s * 0.48),
        (s * 0.50, s * 0.48),
        (s * 0.20, s),
        (s * 0.75, s * 0.52),
        (s * 0.50, s * 0.52),
        (s * 0.80, 0),
    ]
    pg.draw.polygon(surf, color, pts)


def _draw_water(surf, size, color):
    """물 속성 발사체를 물방울 느낌으로 그린다."""
    pg.draw.circle(surf, color, (size // 2, size // 2), size // 2)
    pg.draw.circle(surf, (160, 220, 255), (size // 3, size // 3), size // 5)


def _draw_earth(surf, size, color):
    """땅 속성 발사체를 돌멩이 느낌으로 그린다."""
    pg.draw.circle(surf, color, (size // 2, size // 2), size // 2)
    pg.draw.circle(surf, (100, 60, 20), (size // 2 - 2, size // 2 - 2), size // 4)


_DRAWERS = {
    # 속성 이름을 그리기 함수에 연결해 새 속성을 추가하기 쉽게 한다.
    "star": _draw_star,
    "fire": _draw_fire,
    "electric": _draw_electric,
    "water": _draw_water,
    "earth": _draw_earth,
}
