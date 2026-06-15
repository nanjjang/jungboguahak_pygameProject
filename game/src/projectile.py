import pygame as pg

from src.constants import ELEMENTS, SCREEN_HEIGHT, SCREEN_WIDTH


class Projectile(pg.sprite.Sprite):
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
        surf = pg.Surface((size, size), pg.SRCALPHA)
        draw = _DRAWERS.get(self.element, _draw_star)
        draw(surf, size, color)
        return surf


# 속성별 모양 함수 — 새 속성 추가 시 함수만 등록하면 됨
def _draw_star(surf, size, color):
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
    pg.draw.circle(surf, color, (size // 2, size // 2), size // 2)
    pg.draw.circle(surf, (255, 200, 50), (size // 2, size // 2), size // 4)


def _draw_electric(surf, size, color):
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
    pg.draw.circle(surf, color, (size // 2, size // 2), size // 2)
    pg.draw.circle(surf, (160, 220, 255), (size // 3, size // 3), size // 5)


def _draw_earth(surf, size, color):
    pg.draw.circle(surf, color, (size // 2, size // 2), size // 2)
    pg.draw.circle(surf, (100, 60, 20), (size // 2 - 2, size // 2 - 2), size // 4)


_DRAWERS = {
    "star": _draw_star,
    "fire": _draw_fire,
    "electric": _draw_electric,
    "water": _draw_water,
    "earth": _draw_earth,
}
