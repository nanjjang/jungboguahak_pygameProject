"""플레이 중 바뀌는 모든 상태를 한곳에 묶어 관리한다."""

import pygame as pg

from src.constants import DIFFICULTY_SETTINGS, SCREEN_WIDTH
from src.kirby import Kirby
from src.stage import StageManager


def _create_run(difficulty, ground_y, world=1, substage=1):
    """새 게임 또는 재시작 때 필요한 플레이어, 스테이지, 적 목록을 만든다."""
    stage = StageManager(difficulty, ground_y)
    stage.world = world
    stage.substage = substage
    stage.completed = False
    enemies = stage.spawn_current()
    player = Kirby(x=70, y=ground_y - 26)
    player.set_world_bounds(stage.world_width)
    player.set_spawn_point(70, ground_y - player.rect.height)
    player.reset_position()
    return player, stage, enemies


class GameState:
    """게임 한 판에서 계속 변하는 객체들을 담는 상태 컨테이너."""

    def __init__(self, difficulty, ground_y):
        # difficulty와 ground_y는 재시작할 때도 계속 재사용되는 기본 설정이다.
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
        """현재 난이도로 처음부터 다시 시작한다."""
        self.player, self.stage, self.enemies = _create_run(
            self.difficulty,
            self.ground_y,
        )
        self._clear_runtime_state()

    def reload_current_stage(self):
        """현재 world/substage는 유지하고 스테이지를 새로 불러온다."""
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
        """앞으로 생성되는 적과 HUD가 사용할 난이도를 변경한다."""
        if difficulty not in DIFFICULTY_SETTINGS:
            return
        self.difficulty = difficulty
        if self.stage is not None:
            self.stage.difficulty = difficulty

    def _clear_runtime_state(self):
        """발사체, 데미지 숫자, 카메라처럼 스테이지 재로딩 때 비울 값을 정리한다."""
        self.projectiles.empty()
        self.enemy_projectiles.empty()
        self.damage_numbers.clear()
        self.camera_x = 0.0

    def enter_stage(self, enemies):
        """다음 스테이지로 넘어갈 때 적/발사체/카메라를 새 상태로 정리한다."""
        self.enemies = enemies
        self.projectiles.empty()
        self.enemy_projectiles.empty()
        self.damage_numbers.clear()
        self.camera_x = 0.0
        if self.stage.completed:
            # 전체 클리어 상태에서는 플레이어 위치를 새 스테이지용으로 바꾸지 않는다.
            return

        self.player.set_world_bounds(self.stage.world_width)
        self.player.set_spawn_point(
            70,
            self.ground_y - self.player.rect.height,
        )
        self.player.reset_position()
        # 새 스테이지 시작 직후 바로 맞지 않도록 짧은 무적 시간을 준다.
        self.player.invulnerable_until = pg.time.get_ticks() + 900

    def update_camera(self, reset=False):
        """플레이어가 화면 중앙 근처에 오도록 가로 카메라 위치를 계산한다."""
        if reset:
            self.camera_x = 0.0

        # 카메라는 월드 양 끝을 넘어가지 않게 0과 최대값 사이로 제한한다.
        max_camera_x = max(0, self.stage.world_width - SCREEN_WIDTH)
        target = self.player.rect.centerx - SCREEN_WIDTH // 2
        if target < 0:
            target = 0
        if target > max_camera_x:
            target = max_camera_x
        self.camera_x = float(target)

    def update_damage_numbers(self):
        """떠오르는 데미지 숫자를 움직이고, 시간이 끝난 숫자는 제거한다."""
        visible_numbers = []
        for number in self.damage_numbers:
            number.update()
            if number.alive:
                visible_numbers.append(number)
        self.damage_numbers = visible_numbers
