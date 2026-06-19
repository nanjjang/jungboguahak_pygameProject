# 스테이지 관리

import pygame as pg

from src.constants import DIFFICULTY_SETTINGS
from src.enemy import create_enemy
from src.object import StageScenery
from src.delay_goingNext import animation_duration_ms
from src.door_animation import DoorAnimation
from src.stage_map import build_stage_layout, local_door_rect
from src import sfx

BOSS_ELEMENTS = ("earth", "fire", "electric", "water", "earth")
FLOOR_STEP_UP = 36
FLOOR_STEP_DOWN = 80


class StageManager:
    # 스테이지 진행

    TOTAL_WORLDS = 5
    SUBSTAGES = 3

    def __init__(self, difficulty, ground_y):
        # 첫 스테이지
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
        self.door_animation = DoorAnimation()

    @property
    def label(self):
        # 스테이지 번호
        return f"{self.world}-{self.substage}"

    @property
    def is_boss_stage(self):
        # 보스 스테이지
        return self.substage == self.SUBSTAGES

    @property
    def transitioning(self):
        # 전환 중
        return self.clear_started_at is not None

    def spawn_current(self):
        # 현재 스테이지 생성
        self.stage_started_at = pg.time.get_ticks()
        self.clear_started_at = None
        self.room_id = None
        self.layout = self._make_layout()
        self.world_width = self.layout.world_width
        self.goal_rect = self._make_goal_rect()
        self.scenery = self._make_scenery()
        self.door_animation.reset()
        if self.is_boss_stage:
            return [self._spawn_boss()]
        return self._spawn_route_enemies()

    @property
    def terrain_rects(self):
        # 발판 목록
        return self.layout.platforms

    @property
    def floor_y(self):
        # 기본 바닥
        return self.layout.floor_y

    @property
    def spawn_position(self):
        # 시작 위치
        return self.layout.spawn_x, self.layout.spawn_bottom

    def floor_at_x(self, x, preferred_y=None):
        # 위치별 바닥
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
        # 출구 열림
        if not self.is_boss_stage:
            # 일반 스테이지
            return True
        for enemy in enemies:
            # 보스 먼저 잡기
            if enemy.is_boss and not enemy.defeated:
                return False
        return True

    def near_goal(self, player_rect):
        # 출구 근처
        if self.goal_rect is None:
            return False
        return player_rect.colliderect(self.goal_rect.inflate(36, 20))

    def _near_local_door(self, player_rect):
        # 가까운 동굴문
        for door in self.layout.doors:
            if self._near_door_rect(player_rect, local_door_rect(door)):
                return door
        return None

    def _near_door_rect(self, player_rect, door_rect):
        # 문 판정
        return player_rect.colliderect(door_rect.inflate(42, 96))

    def try_enter_local_door(self, player):
        # 방 이동 시도
        source = self._near_local_door(player.rect)
        if source is None:
            return None

        sfx.stop_all()
        self.room_id = source.target_room
        self.layout = self._make_layout()
        self.world_width = self.layout.world_width
        self.goal_rect = self._make_goal_rect()
        self.scenery = self._make_scenery()
        self.door_animation.reset()

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
        # 스테이지 전환
        if self.completed:
            return None

        now = pg.time.get_ticks()
        if self.transitioning:
            # 클리어 대기
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
            # 클리어 시작
            sfx.stop_all()
            self.clear_started_at = now
        return None

    def draw_environment(self, surface, camera_x, enemies, font, player_rect=None):
        # 배경이랑 문
        self.scenery.draw(surface, camera_x)
        self._draw_local_doors(surface, camera_x, font, player_rect)
        self._draw_goal(surface, camera_x, enemies, font, player_rect)

    def _draw_local_doors(self, surface, camera_x, font, player_rect):
        # 동굴문 그리기
        for door in self.layout.doors:
            world_rect = local_door_rect(door)
            rect = world_rect.move(-round(camera_x), 0)
            if rect.right < -80 or rect.left > surface.get_width() + 80:
                continue

            near = player_rect is not None and self._near_door_rect(
                player_rect, world_rect
            )

            if near:
                self._draw_enter_label(surface, font, "↑ 이동", rect)

    def _draw_goal(self, surface, camera_x, enemies, font, player_rect):
        # 출구 그리기
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
        self.door_animation.set_open(open_requested)

        if unlocked:
            label_text = "↑ 입장"
            color = (255, 255, 255)
        else:
            label_text = "보스를 쓰러뜨리세요"
            color = (255, 205, 120)
        self._draw_enter_label(surface, font, label_text, rect, color=color)

    def _draw_enter_label(self, surface, font, text, rect, color=(255, 255, 255)):
        # 입장 안내
        shadow = font.render(text, True, (45, 20, 30))
        label = font.render(text, True, color)
        label_rect = label.get_rect(midbottom=(rect.centerx, rect.top - 12))
        surface.blit(shadow, label_rect.move(2, 2))
        surface.blit(label, label_rect)

    def _advance(self):
        # 다음 스테이지

        # ===== 임시: 첫 보스(1-3)만 깨면 ALL STAGES CLEAR =====
        # 아래 블록(이 주석 ~ 다음 ===== 줄)을 지우면 원래대로 끝까지 진행됩니다.
        if self.world == 1 and self.is_boss_stage:
            self.completed = True
            self.clear_started_at = None
            return
        # ===== 임시 끝 =====

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
        # 출구 영역
        return self.layout.goal_rect

    def _make_layout(self):
        # 맵 구성
        return build_stage_layout(
            self.world,
            self.substage,
            self.ground_y,
            self.room_id,
        )

    def _make_scenery(self):
        # 배경 구성
        return StageScenery(
            self.world,
            self.substage,
            self.world_width,
            self.ground_y,
            self.layout,
        )

    def _spawn_route_enemies(self):
        # 일반 적 생성
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
            # 최소 적 수
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
            # 속성 돌아가며 배치
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
                # 물 속성은 공중에
                fly_offset = 90
                if index % 2 == 1:
                    fly_offset = 125
            spawn_floor = self.floor_at_x(x, preferred_y=self.floor_y)
            enemy.set_spawn_bottom(spawn_floor - fly_offset)
            enemies.append(enemy)
        return enemies

    def _spawn_boss(self):
        # 보스 생성
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
