"""Kirby가 뱉거나 능력으로 만든 발사체 Sprite를 정의한다."""

import pygame as pg
import load

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
        self.image = self._make_image(cfg["proj_size"])
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
    def _make_image(self, size):
        """속성 이름에 맞는 이미지 파일을 불러와 발사체 이미지를 만든다."""
        image_name = PROJECTILE_IMAGES.get(self.element, PROJECTILE_IMAGES["star"])
        return _load_projectile_image(image_name, size)


PROJECTILE_IMAGES = {
    # 속성 이름을 이미지 파일에 연결해 새 속성을 추가하기 쉽게 한다.
    "star": "frame_141.png",
    "fire": "flame1.png",
    "electric": "sparkIcon.png",
    "water": "spark1.png",
    "earth": "shotzoBullet.png",
}


def _load_projectile_image(image_name, size):
    """원본 이미지를 발사체 크기에 맞게 불러온다."""
    image = load.load_image(image_name).convert_alpha()
    return pg.transform.smoothscale(image, (size, size))
