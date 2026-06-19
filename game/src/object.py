# 스테이지 배경

from functools import lru_cache
from pathlib import Path

import pygame as pg

from src.constants import SCREEN_HEIGHT, SCREEN_WIDTH


SCENERY_ROOT = Path(__file__).resolve().parent / "assets" / "scenery"
STAGE_PARTS_ROOT = SCENERY_ROOT / "stage_parts"


class StageScenery:
    # 배경 오브젝트

    def __init__(self, world, substage, world_width, ground_y, layout=None):
        self.world = world
        self.substage = substage
        self.world_width = world_width
        self.ground_y = ground_y
        self.layout = layout
        self.sky = _load_scenery("background1.png").convert()
        self.ground_strip = _load_scenery("scene1.png").convert_alpha()

    def draw(self, surface, camera_x):
        # 배경 그리기
        self._draw_sky(surface, camera_x)
        self._draw_layout_layer(surface, camera_x, "back")
        self._draw_ground(surface, camera_x)
        self._draw_layout_layer(surface, camera_x, "front")

    def _draw_sky(self, surface, camera_x):
        # 하늘 배경
        sky = pg.transform.scale(self.sky, (SCREEN_WIDTH, SCREEN_HEIGHT))
        x_offset = -round(camera_x * 0.16) % SCREEN_WIDTH
        for x in range(x_offset - SCREEN_WIDTH, SCREEN_WIDTH + 1, SCREEN_WIDTH):
            surface.blit(sky, (x, 0))

    def _draw_ground(self, surface, camera_x):
        # 바닥 배경
        if self.layout is not None and self.substage != 3:
            fill_y = self.layout.floor_y - 4
            pg.draw.rect(
                surface,
                (57, 35, 54),
                (0, fill_y, SCREEN_WIDTH, SCREEN_HEIGHT - fill_y),
            )
            return

        strip_y = self.ground_y - 40
        tile_w = self.ground_strip.get_width()
        start_x = -round(camera_x) % tile_w - tile_w
        end_x = SCREEN_WIDTH + tile_w
        for x in range(start_x, end_x, tile_w):
            surface.blit(self.ground_strip, (x, strip_y))

        fill_y = self.ground_y + 42
        pg.draw.rect(
            surface,
            (72, 33, 60),
            (0, fill_y, SCREEN_WIDTH, SCREEN_HEIGHT - fill_y),
        )

    def _draw_layout_layer(self, surface, camera_x, layer):
        # 맵 조각
        if self.layout is None:
            return

        offset = round(camera_x)
        for piece in self.layout.pieces:
            if piece.layer != layer:
                continue
            image = _load_stage_part(piece.image_name, piece.scale)
            screen_x = piece.x - offset
            if screen_x > SCREEN_WIDTH + 80 or screen_x + image.get_width() < -80:
                continue
            surface.blit(image, (screen_x, piece.y))


def _load_scenery(filename):
    # 배경 이미지 읽기
    return pg.image.load(SCENERY_ROOT / filename)


@lru_cache(maxsize=None)
def _load_stage_part(filename, scale):
    # 맵 조각 읽기
    image = pg.image.load(STAGE_PARTS_ROOT / filename).convert_alpha()
    if scale == 1.0:
        return image
    size = (
        max(1, round(image.get_width() * scale)),
        max(1, round(image.get_height() * scale)),
    )
    return pg.transform.scale(image, size)
