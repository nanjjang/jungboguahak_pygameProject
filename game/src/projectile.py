# 플레이어 발사체

import pygame as pg
import load

from src.constants import ELEMENTS, SCREEN_HEIGHT, SCREEN_WIDTH


class Projectile(pg.sprite.Sprite):
    # 날아가는 공격

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
        # 속성값 가져오기
        cfg = ELEMENTS[element]
        self.dx = cfg["proj_speed"] if facing_right else -cfg["proj_speed"]
        self.dy = float(cfg["proj_dy"])
        self.gravity = cfg["proj_gravity"]
        self.damage = cfg["damage"]
        self.world_width = world_width
        self.image = self._make_image(cfg["proj_size"])
        self.rect = self.image.get_rect(center=(x, y))
        self._y_float = float(y)

    def update(self):
        # 발사체 이동
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

    # 이미지 만들기
    def _make_image(self, size):
        # 속성 이미지
        image_name = PROJECTILE_IMAGES.get(self.element, PROJECTILE_IMAGES["star"])
        return _load_projectile_image(image_name, size)


PROJECTILE_IMAGES = {
    "star": "frame_141.png",
    "fire": "flame1.png",
    "electric": "sparkIcon.png",
    "water": "spark1.png",
    "earth": "shotzoBullet.png",
}


def _load_projectile_image(image_name, size):
    # 이미지 크기 맞춤
    image = load.load_image(image_name).convert_alpha()
    return pg.transform.smoothscale(image, (size, size))
