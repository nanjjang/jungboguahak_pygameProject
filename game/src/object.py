from dataclasses import dataclass
from pathlib import Path

import pygame as pg

from src.constants import SCREEN_HEIGHT, SCREEN_WIDTH


SCENERY_ROOT = Path(__file__).resolve().parent / "assets" / "scenery"


@dataclass(frozen=True)
class SceneryObject:
    image: pg.Surface
    x: int
    y: int
    parallax: float = 1.0

    def draw(self, surface, camera_x):
        screen_x = round(self.x - camera_x * self.parallax)
        if screen_x > surface.get_width() + 80:
            return
        if screen_x + self.image.get_width() < -80:
            return
        surface.blit(self.image, (screen_x, self.y))


class StageScenery:
    """Image-backed scenery and route props for the scrolling stages."""

    def __init__(self, world, substage, world_width, ground_y):
        self.world = world
        self.substage = substage
        self.world_width = world_width
        self.ground_y = ground_y
        self.sky = _load_scenery("background1.png").convert()
        self.ground_strip = _load_scenery("scene1.png").convert_alpha()
        self.backdrop_objects = self._make_backdrop_objects()
        self.route_objects = self._make_route_objects()

    def draw(self, surface, camera_x):
        self._draw_sky(surface, camera_x)
        self._draw_backdrop_objects(surface, camera_x)
        self._draw_ground(surface, camera_x)
        self._draw_route_objects(surface, camera_x)

    def _draw_sky(self, surface, camera_x):
        sky = pg.transform.scale(self.sky, (SCREEN_WIDTH, SCREEN_HEIGHT))
        x_offset = -round(camera_x * 0.16) % SCREEN_WIDTH
        for x in range(x_offset - SCREEN_WIDTH, SCREEN_WIDTH + 1, SCREEN_WIDTH):
            surface.blit(sky, (x, 0))

    def _draw_ground(self, surface, camera_x):
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

    def _draw_backdrop_objects(self, surface, camera_x):
        for scenery_object in self.backdrop_objects:
            scenery_object.draw(surface, camera_x)

    def _draw_route_objects(self, surface, camera_x):
        for scenery_object in self.route_objects:
            scenery_object.draw(surface, camera_x)

    def _make_backdrop_objects(self):
        objects = []
        spacing = 520
        for index, x in enumerate(range(180, self.world_width + spacing, spacing)):
            height = 78 + ((self.world + index) % 3) * 22
            objects.append(
                SceneryObject(
                    _make_moon_hill(160, height, self.world),
                    x,
                    self.ground_y - height - 8,
                    parallax=0.42,
                )
            )
        return objects

    def _make_route_objects(self):
        objects = []
        for index, x in enumerate(range(300, self.world_width - 180, 430)):
            variant = (self.world + self.substage + index) % 3
            if variant == 0:
                image = _make_star_grass()
                y = self.ground_y - image.get_height() + 4
            elif variant == 1:
                image = _make_crystal_cluster()
                y = self.ground_y - image.get_height() + 5
            else:
                image = _make_route_marker()
                y = self.ground_y - image.get_height() + 6
            objects.append(SceneryObject(image, x, y))

        for index, x in enumerate(range(540, self.world_width - 300, 700)):
            image = _make_floating_island(index)
            objects.append(
                SceneryObject(
                    image,
                    x,
                    self.ground_y - 148 - (index % 2) * 26,
                    parallax=0.92,
                )
            )
        return objects


def _load_scenery(filename):
    return pg.image.load(SCENERY_ROOT / filename)


def _make_moon_hill(width, height, world):
    image = pg.Surface((width, height), pg.SRCALPHA)
    colors = (
        (115, 73, 120, 150),
        (92, 88, 145, 150),
        (98, 120, 88, 150),
        (126, 70, 72, 150),
        (88, 112, 128, 150),
    )
    color = colors[(world - 1) % len(colors)]
    pg.draw.ellipse(image, color, (0, 16, width, height * 2))
    for x, y, radius in ((38, 28, 9), (87, 42, 5), (126, 24, 7)):
        pg.draw.circle(image, (255, 235, 190, 62), (x, y), radius)
    return image


def _make_star_grass():
    image = pg.Surface((76, 34), pg.SRCALPHA)
    pg.draw.ellipse(image, (52, 125, 76), (0, 14, 76, 28))
    pg.draw.ellipse(image, (91, 190, 91), (8, 8, 48, 20))
    for x, y in ((18, 17), (42, 12), (61, 20)):
        _draw_star(image, x, y, 6, (255, 235, 108))
    return image


def _make_crystal_cluster():
    image = pg.Surface((70, 50), pg.SRCALPHA)
    crystals = (
        ((16, 48), (24, 16), (34, 48), (123, 210, 255)),
        ((33, 48), (44, 5), (55, 48), (214, 115, 255)),
        ((46, 48), (54, 20), (66, 48), (255, 218, 91)),
    )
    for left, top, right, color in crystals:
        pg.draw.polygon(image, color, (left, top, right))
        pg.draw.polygon(image, (255, 255, 255, 120), (left, top, right), 1)
    pg.draw.ellipse(image, (44, 35, 58, 190), (4, 38, 64, 12))
    return image


def _make_route_marker():
    image = pg.Surface((44, 82), pg.SRCALPHA)
    pg.draw.rect(image, (58, 36, 70), (17, 20, 10, 56), border_radius=4)
    pg.draw.circle(image, (255, 224, 80), (22, 20), 18)
    pg.draw.circle(image, (122, 50, 102), (22, 20), 13)
    _draw_star(image, 22, 20, 8, (255, 248, 150))
    return image


def _make_floating_island(index):
    image = pg.Surface((118, 42), pg.SRCALPHA)
    pg.draw.rect(image, (65, 150, 75), (8, 10, 102, 18), border_radius=8)
    pg.draw.rect(image, (112, 207, 85), (12, 5, 94, 12), border_radius=6)
    pg.draw.polygon(
        image,
        (84, 55, 58),
        ((18, 25), (102, 25), (82, 40), (38, 40)),
    )
    if index % 2:
        pg.draw.circle(image, (255, 190, 220), (84, 4), 5)
        pg.draw.circle(image, (255, 238, 90), (92, 7), 4)
    else:
        pg.draw.circle(image, (175, 225, 255), (32, 4), 5)
        pg.draw.circle(image, (255, 238, 90), (42, 7), 4)
    return image


def _draw_star(surface, x, y, radius, color):
    points = (
        (x, y - radius),
        (x + radius // 3, y - radius // 3),
        (x + radius, y),
        (x + radius // 3, y + radius // 3),
        (x, y + radius),
        (x - radius // 3, y + radius // 3),
        (x - radius, y),
        (x - radius // 3, y - radius // 3),
    )
    pg.draw.polygon(surface, color, points)
