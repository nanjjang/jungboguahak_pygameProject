"""스테이지 배경과 바닥 이미지를 그리는 오브젝트 파일."""

from pathlib import Path

import pygame as pg

from src.constants import SCREEN_HEIGHT, SCREEN_WIDTH


SCENERY_ROOT = Path(__file__).resolve().parent / "assets" / "scenery"

class StageScenery:
    """스크롤 스테이지의 하늘과 바닥 이미지를 담당한다."""

    def __init__(self, world, substage, world_width, ground_y):
        self.world = world
        self.substage = substage
        self.world_width = world_width
        self.ground_y = ground_y
        self.sky = _load_scenery("background1.png").convert()
        self.ground_strip = _load_scenery("scene1.png").convert_alpha()

    def draw(self, surface, camera_x):
        """하늘을 먼저 그리고, 그 위에 바닥 타일을 반복해서 그린다."""
        self._draw_sky(surface, camera_x)
        self._draw_ground(surface, camera_x)

    def _draw_sky(self, surface, camera_x):
        """카메라보다 천천히 움직이는 하늘 배경으로 깊이감을 만든다."""
        sky = pg.transform.scale(self.sky, (SCREEN_WIDTH, SCREEN_HEIGHT))
        x_offset = -round(camera_x * 0.16) % SCREEN_WIDTH
        for x in range(x_offset - SCREEN_WIDTH, SCREEN_WIDTH + 1, SCREEN_WIDTH):
            surface.blit(sky, (x, 0))

    def _draw_ground(self, surface, camera_x):
        """바닥 이미지를 가로로 반복해서 긴 스테이지처럼 보이게 한다."""
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


def _load_scenery(filename):
    """assets/scenery 폴더에서 배경 이미지를 읽는다."""
    return pg.image.load(SCENERY_ROOT / filename)


# def make_obstacle():
