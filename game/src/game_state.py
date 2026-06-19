# 게임 상태

import pygame as pg

from src.constants import DIFFICULTY_SETTINGS, SCREEN_WIDTH
from src.kirby import Kirby
from src.stage import StageManager


def _create_run(difficulty, ground_y, world=1, substage=1):
    # 새 게임 준비
    stage = StageManager(difficulty, ground_y)
    stage.world = world
    stage.substage = substage
    stage.completed = False
    enemies = stage.spawn_current()
    spawn_x, spawn_bottom = stage.spawn_position
    player = Kirby(x=spawn_x, y=spawn_bottom - 26)
    player.set_world_bounds(stage.world_width)
    player.set_spawn_point(spawn_x, spawn_bottom - player.rect.height)
    player.reset_position()
    return player, stage, enemies


class GameState:
    # 게임 한 판 상태

    def __init__(self, difficulty, ground_y):
        self.difficulty = difficulty
        self.ground_y = ground_y
        self.projectiles = pg.sprite.Group()
        self.enemy_projectiles = pg.sprite.Group()
        self.damage_numbers = []
        self.camera_x = 0.0
        self.player = None
        self.stage = None
        self.enemies = []
        self.restart()

    def restart(self):
        # 처음부터 다시
        self.player, self.stage, self.enemies = _create_run(
            self.difficulty,
            self.ground_y,
        )
        self._clear_runtime_state()

    def reload_current_stage(self):
        # 현재 스테이지 다시
        world = 1
        substage = 1
        if self.stage is not None:
            world = self.stage.world
            substage = self.stage.substage

        self.player, self.stage, self.enemies = _create_run(
            self.difficulty,
            self.ground_y,
            world,
            substage,
        )
        self._clear_runtime_state()

    def set_difficulty(self, difficulty):
        # 난이도 변경
        if difficulty not in DIFFICULTY_SETTINGS:
            return
        self.difficulty = difficulty
        if self.stage is not None:
            self.stage.difficulty = difficulty

    def _clear_runtime_state(self):
        # 진행 중 값 정리
        self.projectiles.empty()
        self.enemy_projectiles.empty()
        self.damage_numbers.clear()
        self.camera_x = 0.0

    def enter_stage(self, enemies):
        # 다음 스테이지
        self.enemies = enemies
        self.projectiles.empty()
        self.enemy_projectiles.empty()
        self.damage_numbers.clear()
        self.camera_x = 0.0
        if self.stage.completed:
            # 전체 클리어
            return

        self.player.set_world_bounds(self.stage.world_width)
        spawn_x, spawn_bottom = self.stage.spawn_position
        self.player.set_spawn_point(
            spawn_x,
            spawn_bottom - self.player.rect.height,
        )
        self.player.reset_position()
        # 시작 무적
        self.player.invulnerable_until = pg.time.get_ticks() + 900

    def enter_room(self, enemies):
        # 방 이동
        self.enemies = enemies
        self.projectiles.empty()
        self.enemy_projectiles.empty()
        self.damage_numbers.clear()
        self.camera_x = 0.0
        self.player.set_world_bounds(self.stage.world_width)
        self.player.invulnerable_until = pg.time.get_ticks() + 650

    def update_camera(self, reset=False):
        # 카메라 이동
        if reset:
            self.camera_x = 0.0

        # 맵 밖으로 못 나가게
        max_camera_x = max(0, self.stage.world_width - SCREEN_WIDTH)
        target = self.player.rect.centerx - SCREEN_WIDTH // 2
        if target < 0:
            target = 0
        if target > max_camera_x:
            target = max_camera_x
        self.camera_x = float(target)

    def update_damage_numbers(self):
        # 데미지 숫자
        visible_numbers = []
        for number in self.damage_numbers:
            number.update()
            if number.alive:
                visible_numbers.append(number)
        self.damage_numbers = visible_numbers
