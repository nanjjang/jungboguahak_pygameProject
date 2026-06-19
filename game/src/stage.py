"""스테이지 진행, 적 배치, 출구 문 상태를 관리하는 파일."""

import pygame as pg

from src.constants import DIFFICULTY_SETTINGS
from src.enemy import create_enemy
from src.object import StageScenery
from src.delay_goingNext import animation_duration_ms
from src.stage_door import DOOR_ANIMATION_MS, draw_cave_door, draw_stage_door
from src.stage_map import build_stage_layout, local_door_rect

BOSS_ELEMENTS = ("earth", "fire", "electric", "water", "earth")
FLOOR_STEP_UP = 36
FLOOR_STEP_DOWN = 80


class StageManager:
    """5개 월드와 각 월드의 일반 스테이지 2개, 보스 스테이지 1개를 관리한다."""

    TOTAL_WORLDS = 5
    SUBSTAGES = 3

    def __init__(self, difficulty, ground_y):
        """새 게임을 시작할 때 첫 스테이지 상태를 만든다."""
        if difficulty not in DIFFICULTY_SETTINGS:
            raise ValueError(f"Unknown difficulty: {difficulty}")
        self.difficulty = difficulty
        self.ground_y = ground_y
        self.world = 1
        self.substage = 1
        self.room_id = None
        self.completed = False
        self.stage_started_at = pg.time.get_ticks()
        self.clear_started_at = None
        self.layout = self._make_layout()
        self.world_width = self.layout.world_width
        self.goal_rect = self._make_goal_rect()
        self.scenery = self._make_scenery()
        self.door_open = False
        self.door_changed_at = pg.time.get_ticks() - DOOR_ANIMATION_MS

    @property
    def label(self):
        """HUD에 표시할 현재 스테이지 번호를 만든다."""
        return f"{self.world}-{self.substage}"

    @property
    def is_boss_stage(self):
        """각 월드의 세 번째 스테이지는 보스 스테이지이다."""
        return self.substage == self.SUBSTAGES

    @property
    def transitioning(self):
        """클리어 연출 중이면 True이다."""
        return self.clear_started_at is not None

    def spawn_current(self):
        """현재 world/substage에 맞는 적 목록과 지형 정보를 새로 만든다."""
        self.stage_started_at = pg.time.get_ticks()
        self.clear_started_at = None
        self.room_id = None
        self.layout = self._make_layout()
        self.world_width = self.layout.world_width
        self.goal_rect = self._make_goal_rect()
        self.scenery = self._make_scenery()
        self.door_open = False
        self.door_changed_at = pg.time.get_ticks() - DOOR_ANIMATION_MS
        if self.is_boss_stage:
            return [self._spawn_boss()]
        return self._spawn_route_enemies()

    @property
    def terrain_rects(self):
        """Kirby가 착지할 수 있는 추가 발판 목록을 반환한다."""
        return self.layout.platforms

    @property
    def floor_y(self):
        """현재 방에서 플레이어와 적이 서는 기본 바닥 높이."""
        return self.layout.floor_y

    @property
    def spawn_position(self):
        """현재 방에 입장했을 때 Kirby가 나타날 위치."""
        return self.layout.spawn_x, self.layout.spawn_bottom

    def floor_at_x(self, x, preferred_y=None):
        """월드 x좌표에서 가장 알맞은 지형 윗면 높이를 찾는다."""
        candidates = []
        for rect in self.layout.platforms:
            if rect.left + 3 <= x <= rect.right - 3:
                candidates.append(rect.top)

        if preferred_y is None:
            return min(candidates) if candidates else self.floor_y

        reachable = []
        for floor_y in candidates:
            delta = floor_y - preferred_y
            if -FLOOR_STEP_UP <= delta <= FLOOR_STEP_DOWN:
                reachable.append(floor_y)

        if not reachable:
            return self.floor_y
        return min(reachable, key=lambda floor_y: abs(floor_y - preferred_y))

    def goal_unlocked(self, enemies):
        """출구 문을 열 수 있는 상태인지 확인한다."""
        if not self.is_boss_stage:
            # 일반 스테이지는 문 근처로 가면 바로 입장할 수 있다.
            return True
        for enemy in enemies:
            # 보스 스테이지는 보스를 쓰러뜨려야 문이 열린다.
            if enemy.is_boss and not enemy.defeated:
                return False
        return True

    def near_goal(self, player_rect):
        """플레이어가 문 근처에 있는지 약간 넓은 충돌 범위로 확인한다."""
        if self.goal_rect is None:
            return False
        return player_rect.colliderect(self.goal_rect.inflate(36, 20))

    def _near_local_door(self, player_rect):
        """플레이어가 닿은 로컬 동굴문을 찾는다."""
        for door in self.layout.doors:
            if self._near_door_rect(player_rect, local_door_rect(door)):
                return door
        return None

    def _near_door_rect(self, player_rect, door_rect):
        """문보다 살짝 넓은 입장 판정으로 가까이 있는지 확인한다."""
        return player_rect.colliderect(door_rect.inflate(42, 96))

    def try_enter_local_door(self, player):
        """동굴문 앞에서 입장하면 대상 방으로 맵을 교체하고 적을 새로 만든다."""
        source = self._near_local_door(player.rect)
        if source is None:
            return None

        self.room_id = source.target_room
        self.layout = self._make_layout()
        self.world_width = self.layout.world_width
        self.goal_rect = self._make_goal_rect()
        self.scenery = self._make_scenery()
        self.door_open = False
        self.door_changed_at = pg.time.get_ticks() - DOOR_ANIMATION_MS

        player.set_world_bounds(self.world_width)
        spawn_x, spawn_bottom = self.spawn_position
        player.rect.midbottom = (spawn_x, spawn_bottom)
        player.y_float = float(player.rect.y)
        player.velocity_y = 0.0
        player.is_jumping = False
        player.hovering = False
        player.set_spawn_point(player.rect.x, player.rect.y)
        player.invulnerable_until = pg.time.get_ticks() + 450
        return self._spawn_route_enemies()

    def update(self, enemies, player_rect=None, enter_pressed=False):
        """문 앞에서 입장 키를 눌렀을 때 스테이지 전환을 시작하거나 끝낸다."""
        if self.completed:
            return None

        now = pg.time.get_ticks()
        if self.transitioning:
            # 클리어 하면 일정 시간 후 다음 스테이지로 이동
            if now - self.clear_started_at < animation_duration_ms():
                return None
            self._advance()
            if self.completed:
                return []
            return self.spawn_current()

        if (
            enter_pressed
            and player_rect is not None
            and self.near_goal(player_rect)
            and self.goal_unlocked(enemies)
        ):
            # 조건이 모두 맞으면 지금 시간을 기록해서 클리어 연출 상태로 들어간다.
            self.clear_started_at = now
        return None

    def draw_environment(self, surface, camera_x, enemies, font, player_rect=None):
        """스테이지 배경과 출구 문을 그린다."""
        self.scenery.draw(surface, camera_x)
        self._draw_local_doors(surface, camera_x, font, player_rect)
        self._draw_goal(surface, camera_x, enemies, font, player_rect)

    def _draw_local_doors(self, surface, camera_x, font, player_rect):
        """스테이지 안에서 서로 이어지는 작은 동굴문을 그린다."""
        for door in self.layout.doors:
            world_rect = local_door_rect(door)
            rect = world_rect.move(-round(camera_x), 0)
            if rect.right < -80 or rect.left > surface.get_width() + 80:
                continue

            near = player_rect is not None and self._near_door_rect(
                player_rect, world_rect
            )
            glow = pg.Surface((rect.width + 44, rect.height + 38), pg.SRCALPHA)
            glow_alpha = 68 if near else 38
            pg.draw.ellipse(
                glow,
                (142, 230, 255, glow_alpha),
                glow.get_rect(),
            )
            surface.blit(glow, glow.get_rect(center=rect.center))

            if door.draw_sprite:
                draw_cave_door(surface, world_rect, camera_x, 1.0 if near else 0.0)

            if near:
                self._draw_enter_label(surface, font, "↑ 이동", rect)

    def _draw_goal(self, surface, camera_x, enemies, font, player_rect):
        """문, 문 주변 빛, 입장 안내 문구를 그린다."""
        if self.goal_rect is None:
            return

        rect = self.goal_rect.move(-round(camera_x), 0)
        if rect.right < -140 or rect.left > surface.get_width() + 140:
            return

        unlocked = self.goal_unlocked(enemies)
        open_requested = unlocked and (
            self.transitioning
            or (player_rect is not None and self.near_goal(player_rect))
        )
        if open_requested != self.door_open:
            # 문 열림 상태가 바뀌는 순간을 기록해서 애니메이션 진행률을 계산한다.
            self.door_open = open_requested
            self.door_changed_at = pg.time.get_ticks()

        open_progress = self._door_open_progress()
        glow = pg.Surface((rect.width + 90, rect.height + 70), pg.SRCALPHA)
        glow_color = (255, 255, 170, 70) if unlocked else (80, 85, 100, 65)
        pg.draw.rect(
            glow,
            glow_color,
            glow.get_rect().inflate(-8, -8),
            border_radius=18,
        )
        surface.blit(glow, glow.get_rect(center=rect.center))

        if self.is_boss_stage:
            draw_stage_door(surface, self.goal_rect, camera_x, "boss", open_progress)

        if unlocked:
            label_text = "↑ 입장"
            color = (255, 255, 255)
        else:
            label_text = "보스를 쓰러뜨리세요"
            color = (255, 205, 120)
        self._draw_enter_label(surface, font, label_text, rect, color=color)

    def _draw_enter_label(self, surface, font, text, rect, color=(255, 255, 255)):
        """문 위에 입장 안내 문구를 그림자와 함께 그린다."""
        shadow = font.render(text, True, (45, 20, 30))
        label = font.render(text, True, color)
        label_rect = label.get_rect(midbottom=(rect.centerx, rect.top - 12))
        surface.blit(shadow, label_rect.move(2, 2))
        surface.blit(label, label_rect)

    def _door_open_progress(self):
        """문 애니메이션이 0.0에서 1.0 사이로 얼마나 진행됐는지 계산한다."""
        elapsed = pg.time.get_ticks() - self.door_changed_at
        progress = min(1.0, elapsed / DOOR_ANIMATION_MS)
        if self.door_open:
            return progress
        return 1.0 - progress

    def _advance(self):
        """다음 substage 또는 다음 world로 이동하고, 마지막이면 전체 클리어 처리한다."""
        if self.substage < self.SUBSTAGES:
            self.substage += 1
            return
        if self.world < self.TOTAL_WORLDS:
            self.world += 1
            self.substage = 1
            return
        self.completed = True
        self.clear_started_at = None

    def _make_goal_rect(self):
        """스테이지 오른쪽 끝 근처에 출구 문 충돌 영역을 만든다."""
        return self.layout.goal_rect

    def _make_layout(self):
        """잘라낸 이미지 조각을 현재 스테이지 길이에 맞게 배치한다."""
        return build_stage_layout(
            self.world,
            self.substage,
            self.ground_y,
            self.room_id,
        )

    def _make_scenery(self):
        """현재 world/substage에 맞는 배경 객체를 만든다."""
        return StageScenery(
            self.world,
            self.substage,
            self.world_width,
            self.ground_y,
            self.layout,
        )

    def _spawn_route_enemies(self):
        """일반 길 스테이지에 배치할 적들을 거리 간격에 맞춰 만든다."""
        settings = DIFFICULTY_SETTINGS[self.difficulty]
        count = 5
        if self.substage == 2:
            count += 1
        if self.world >= 3:
            count += 1
        if self.world == 5:
            count += 1
        count += settings["spawn_bonus"]
        if count < 4:
            # 쉬움 난이도 보정이 있어도 너무 적어지지는 않게 최소 수를 보장한다.
            count = 4
        room_cap = max(3, self.world_width // 320)
        count = min(count, room_cap)

        elements = ("fire", "electric", "water", "earth")
        enemies = []
        route_start = 220
        route_end = self.world_width - 220
        if route_end <= route_start:
            route_start = 220
            route_end = max(route_start + 1, self.world_width - 180)
        spacing = (route_end - route_start) / (count - 1)

        for index in range(count):
            # 속성은 fire/electric/water/earth 순서로 반복해서 다양하게 배치한다.
            element = elements[index % len(elements)]
            offset = -35 if index % 2 == 0 else 35
            x = round(route_start + spacing * index + offset)
            enemy = create_enemy(
                element,
                x,
                0,
                difficulty=self.difficulty,
                level=self.world,
                ground_y=self.floor_y,
                world_width=self.world_width,
            )
            fly_offset = 0
            if element == "water":
                # 물 속성 적은 새처럼 떠다니므로 바닥보다 위에 배치한다.
                fly_offset = 90
                if index % 2 == 1:
                    fly_offset = 125
            spawn_floor = self.floor_at_x(x, preferred_y=self.floor_y)
            enemy.set_spawn_bottom(spawn_floor - fly_offset)
            enemies.append(enemy)
        return enemies

    def _spawn_boss(self):
        """현재 월드 번호에 맞는 보스 한 마리를 만든다."""
        element = BOSS_ELEMENTS[self.world - 1]
        enemy = create_enemy(
            element,
            760,
            0,
            difficulty=self.difficulty,
            is_boss=True,
            level=self.world,
            ground_y=self.floor_y,
            world_width=self.world_width,
        )
        fly_offset = 65 if element == "water" else 0
        enemy.set_spawn_bottom(self.floor_at_x(enemy.rect.centerx, self.floor_y) - fly_offset)
        return enemy
