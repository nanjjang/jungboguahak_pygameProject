"""한 번에 하나의 원본 맵 조각만 보여주는 방 단위 스테이지 데이터."""

from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

import pygame as pg

from src.constants import SCREEN_WIDTH


STAGE_PARTS_ROOT = Path(__file__).resolve().parent / "assets" / "scenery" / "stage_parts"
DOOR_OPENING_SIZE = (36, 50)
PLAY_FLOOR_OFFSET = 50


@dataclass(frozen=True)
class SceneryPiece:
    """한 장의 맵 이미지를 월드 좌표에 배치한다."""

    image_name: str
    x: int
    y: int
    layer: str = "front"
    scale: float = 1.0


@dataclass(frozen=True)
class LocalDoor:
    """현재 방에서 다른 방으로 넘어가는 검은 입구 핫스팟."""

    door_id: str
    target_room: str
    x: int
    bottom: int
    draw_sprite: bool = False


@dataclass(frozen=True)
class StageLayout:
    """현재 방 하나를 그리는 데 필요한 데이터."""

    room_id: str
    world_width: int
    floor_y: int
    spawn_x: int
    spawn_bottom: int
    pieces: tuple[SceneryPiece, ...]
    platforms: tuple[pg.Rect, ...]
    doors: tuple[LocalDoor, ...]
    goal_rect: pg.Rect | None


@dataclass(frozen=True)
class _DoorSpec:
    door_id: str
    target_room: str
    x: int
    bottom_y: int | None = None
    draw_sprite: bool = False


@dataclass(frozen=True)
class _PlatformSpec:
    x: int
    y: int
    width: int
    height: int = 16


@dataclass(frozen=True)
class _RoomSpec:
    image_name: str
    size: tuple[int, int]
    surface_y: int
    spawn_x: int
    goal_x: int | None = None
    goal_bottom_y: int | None = None
    doors: tuple[_DoorSpec, ...] = ()
    platforms: tuple[_PlatformSpec, ...] = ()


ROOMS = {
    "ice_path": _RoomSpec(
        image_name="ice_grass_path.png",
        size=(800, 143),
        surface_y=111,
        spawn_x=80,
        doors=(
            _DoorSpec("ice-cave", "rock_bridge", 776, bottom_y=48),
        ),
        platforms=(
            _PlatformSpec(0, 0, 32),
            _PlatformSpec(192, 0, 32),
            _PlatformSpec(256, 0, 112),
            _PlatformSpec(416, 0, 32),
            _PlatformSpec(544, 0, 32),
            _PlatformSpec(608, 0, 32),
            _PlatformSpec(82, 47, 60),
            _PlatformSpec(182, 103, 84),
            _PlatformSpec(190, 95, 68),
            _PlatformSpec(198, 87, 52),
            _PlatformSpec(207, 79, 34),
            _PlatformSpec(438, 103, 164),
            _PlatformSpec(446, 95, 148),
            _PlatformSpec(454, 87, 84),
            _PlatformSpec(463, 79, 66),
            _PlatformSpec(678, 103, 122),
            _PlatformSpec(686, 95, 114),
            _PlatformSpec(694, 87, 106),
            _PlatformSpec(702, 80, 98),
        ),
    ),
    "rock_bridge": _RoomSpec(
        image_name="vegetable_rock_bridge.png",
        size=(768, 176),
        surface_y=142,
        spawn_x=64,
        doors=(
            _DoorSpec("rock-door", "palm_beach", 712, bottom_y=144),
        ),
        platforms=(
            _PlatformSpec(0, 142, 112),
            _PlatformSpec(112, 134, 32),
            _PlatformSpec(144, 126, 32),
            _PlatformSpec(176, 118, 32),
            _PlatformSpec(208, 110, 32),
            _PlatformSpec(240, 142, 496),
            _PlatformSpec(736, 96, 32),
        ),
    ),
    "palm_beach": _RoomSpec(
        image_name="ice_palm_beach.png",
        size=(528, 176),
        surface_y=131,
        spawn_x=64,
        goal_x=488,
        goal_bottom_y=128,
        platforms=(
            _PlatformSpec(275, 34, 122),
            _PlatformSpec(147, 50, 74),
            _PlatformSpec(451, 50, 26),
            _PlatformSpec(115, 66, 42),
            _PlatformSpec(83, 98, 42),
            _PlatformSpec(0, 130, 77),
            _PlatformSpec(195, 130, 333),
            _PlatformSpec(67, 146, 218),
        ),
    ),
    "vegetable_field": _RoomSpec(
        image_name="vegetable_upper_fields.png",
        size=(1280, 115),
        surface_y=84,
        spawn_x=60,
        doors=(
            _DoorSpec(
                "field-cave",
                "orange_cavern",
                1212,
                bottom_y=66,
                draw_sprite=True,
            ),
        ),
        platforms=(
            _PlatformSpec(0, 84, 1280),
        ),
    ),
    "orange_cavern": _RoomSpec(
        image_name="vegetable_orange_cavern.png",
        size=(1024, 176),
        surface_y=150,
        spawn_x=58,
        goal_x=968,
        goal_bottom_y=64,
        platforms=(
            _PlatformSpec(0, 72, 560),
            _PlatformSpec(592, 82, 392),
            _PlatformSpec(768, 117, 112),
            _PlatformSpec(736, 144, 32),
            _PlatformSpec(832, 144, 32),
        ),
    ),
    "sandy_cavern": _RoomSpec(
        image_name="ice_sandy_cavern.png",
        size=(800, 176),
        surface_y=146,
        spawn_x=64,
        goal_x=488,
        goal_bottom_y=128,
        platforms=(
            _PlatformSpec(0, 146, 800),
        ),
    ),
}


ROUTES = {
    1: ("ice_path", "rock_bridge", "palm_beach"),
    2: ("vegetable_field", "orange_cavern"),
}


def build_stage_layout(world, substage, base_ground_y, room_id=None):
    """현재 스테이지의 현재 방 하나만 골라 배치한다."""
    if substage == 3:
        room_id = "sandy_cavern"
    else:
        route = ROUTES[1 if substage == 1 else 2]
        if room_id not in route:
            room_id = route[0]

    spec = ROOMS[room_id]
    width, height = spec.size
    scale = max(1.0, SCREEN_WIDTH / width)
    scaled_width = round(width * scale)
    image_x = 0
    world_width = max(SCREEN_WIDTH, scaled_width)
    floor_y = base_ground_y - PLAY_FLOOR_OFFSET
    image_y = round(floor_y - spec.surface_y * scale)

    pieces = (SceneryPiece(spec.image_name, image_x, image_y, scale=scale),)
    platforms = _make_platforms(spec, image_x, image_y, scale)
    doors = _make_doors(spec, image_x, image_y, floor_y, scale)
    goal_rect = _make_goal_rect(spec, image_x, image_y, scale)

    return StageLayout(
        room_id=room_id,
        world_width=world_width,
        floor_y=floor_y,
        spawn_x=round(image_x + spec.spawn_x * scale),
        spawn_bottom=floor_y,
        pieces=pieces,
        platforms=platforms,
        doors=doors,
        goal_rect=goal_rect,
    )


def local_door_rect(door):
    """동굴문 충돌/렌더링에 쓰는 월드 좌표 사각형을 반환한다."""
    rect = pg.Rect(0, 0, *DOOR_OPENING_SIZE)
    rect.midbottom = (door.x, door.bottom)
    return rect


def _make_platforms(spec, image_x, image_y, scale):
    platforms = []
    source_platforms = spec.platforms if spec.platforms else _auto_platforms(spec)
    for platform in source_platforms:
        platforms.append(
            pg.Rect(
                round(image_x + platform.x * scale),
                round(image_y + platform.y * scale),
                round(platform.width * scale),
                max(10, round(platform.height * scale)),
            )
        )
    return tuple(platforms)


@lru_cache(maxsize=None)
def _auto_platforms(spec):
    """맵 이미지에서 눈에 보이는 지형 윗면만 자동 발판으로 추출한다."""
    image = pg.image.load(STAGE_PARTS_ROOT / spec.image_name)
    width, height = image.get_size()
    platforms = []
    min_width = 14

    for y in range(height):
        start = None
        for x in range(width):
            is_top = _is_top_surface_pixel(image, spec.image_name, x, y)
            if is_top and start is None:
                start = x
            if (not is_top or x == width - 1) and start is not None:
                end = x if not is_top else x + 1
                if end - start >= min_width:
                    platforms.append(_PlatformSpec(start, y, end - start, 12))
                start = None
    return tuple(_merge_close_platforms(platforms))


def _merge_close_platforms(platforms):
    """같은 높이의 가까운 조각은 하나의 발판으로 합쳐 작은 틈 오판을 줄인다."""
    if not platforms:
        return ()
    ordered = sorted(platforms, key=lambda p: (p.y, p.x))
    merged = [ordered[0]]
    for platform in ordered[1:]:
        last = merged[-1]
        gap = platform.x - (last.x + last.width)
        if platform.y == last.y and 0 <= gap <= 2:
            merged[-1] = _PlatformSpec(
                last.x,
                last.y,
                platform.x + platform.width - last.x,
                max(last.height, platform.height),
            )
        else:
            merged.append(platform)
    return tuple(merged)


def _is_top_surface_pixel(image, image_name, x, y):
    color = image.get_at((x, y))
    if color.a == 0 or not _is_surface_color(image_name, color):
        return False

    if y > 0 and _is_surface_color(image_name, image.get_at((x, y - 1))):
        return False

    support = 0
    for yy in range(y, min(image.get_height(), y + 8)):
        if image.get_at((x, yy)).a:
            support += 1
    return support >= 4


def _is_surface_color(image_name, color):
    r, g, b, a = color
    if a == 0:
        return False

    green_top = g >= 145 and r <= 125 and b <= 125
    snow_top = r >= 150 and g >= 145 and b >= 135
    stone_top = r >= 165 and g >= 120 and 60 <= b <= 135
    orange_edge = r >= 150 and g >= 120 and b >= 95

    if image_name in {
        "ice_grass_path.png",
        "ice_palm_beach.png",
        "vegetable_upper_fields.png",
    }:
        return green_top or stone_top
    if image_name in {"vegetable_rock_bridge.png", "ice_sandy_cavern.png"}:
        return snow_top
    if image_name == "vegetable_orange_cavern.png":
        return snow_top or orange_edge
    return green_top or snow_top or stone_top


def _make_doors(spec, image_x, image_y, floor_y, scale):
    doors = []
    for door in spec.doors:
        bottom = floor_y if door.bottom_y is None else round(image_y + door.bottom_y * scale)
        doors.append(
            LocalDoor(
                door_id=door.door_id,
                target_room=door.target_room,
                x=round(image_x + door.x * scale),
                bottom=bottom,
                draw_sprite=door.draw_sprite,
            )
        )
    return tuple(doors)


def _make_goal_rect(spec, image_x, image_y, scale):
    if spec.goal_x is None:
        return None

    bottom = image_y + (
        spec.surface_y * scale
        if spec.goal_bottom_y is None
        else spec.goal_bottom_y * scale
    )
    rect = pg.Rect(0, 0, *DOOR_OPENING_SIZE)
    rect.midbottom = (round(image_x + spec.goal_x * scale), round(bottom))
    return rect
