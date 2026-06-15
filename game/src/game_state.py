import pygame as pg

from src.constants import SCREEN_WIDTH
from src.kirby import Kirby
from src.stage import StageManager


def _create_run(difficulty, ground_y):
    stage = StageManager(difficulty, ground_y)
    player = Kirby(x=70, y=ground_y - 26)
    player.set_world_bounds(stage.world_width)
    player.set_spawn_point(70, ground_y - player.rect.height)
    player.reset_position()
    return player, stage, stage.spawn_current()


class GameState:
    """Mutable state for one game session."""

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
        self.player, self.stage, self.enemies = _create_run(
            self.difficulty,
            self.ground_y,
        )
        self.projectiles.empty()
        self.enemy_projectiles.empty()
        self.damage_numbers.clear()
        self.camera_x = 0.0

    def enter_stage(self, enemies):
        self.enemies = enemies
        self.projectiles.empty()
        self.enemy_projectiles.empty()
        self.damage_numbers.clear()
        self.camera_x = 0.0
        if self.stage.completed:
            return

        self.player.set_world_bounds(self.stage.world_width)
        self.player.set_spawn_point(
            70,
            self.ground_y - self.player.rect.height,
        )
        self.player.reset_position()
        self.player.invulnerable_until = pg.time.get_ticks() + 900

    def update_camera(self, reset=False):
        if reset:
            self.camera_x = 0.0
        max_camera_x = max(0, self.stage.world_width - SCREEN_WIDTH)
        target = max(
            0,
            min(
                max_camera_x,
                self.player.rect.centerx - round(SCREEN_WIDTH * 0.42),
            ),
        )
        self.camera_x += (target - self.camera_x) * 0.14
        if abs(target - self.camera_x) < 0.5:
            self.camera_x = float(target)

    def update_damage_numbers(self):
        for number in self.damage_numbers:
            number.update()
        self.damage_numbers = [number for number in self.damage_numbers if number.alive]
