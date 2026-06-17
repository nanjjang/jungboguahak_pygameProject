import pygame as pg

from src.constants import DIFFICULTY_SETTINGS
from src.enemy import create_enemy
from src.object import StageScenery
from src.stage_clear_animation import animation_duration_ms

ROUTE_WIDTHS = {
    1: (2550, 2770),
    2: (2730, 2950),
    3: (2910, 3130),
    4: (3090, 3310),
    5: (3270, 3490),
}

BOSS_ELEMENTS = ("earth", "fire", "electric", "water", "earth")


class StageManager:
    """Five worlds made of two scrolling routes and one boss area."""

    TOTAL_WORLDS = 5
    SUBSTAGES = 3

    def __init__(self, difficulty, ground_y):
        if difficulty not in DIFFICULTY_SETTINGS:
            raise ValueError(f"Unknown difficulty: {difficulty}")
        self.difficulty = difficulty
        self.ground_y = ground_y
        self.world = 1
        self.substage = 1
        self.completed = False
        self.stage_started_at = pg.time.get_ticks()
        self.clear_started_at = None
        self.world_width = self._stage_width()
        self.goal_rect = self._make_goal_rect()
        self.scenery = self._make_scenery()

    @property
    def label(self):
        return f"{self.world}-{self.substage}"

    @property
    def is_boss_stage(self):
        return self.substage == self.SUBSTAGES

    @property
    def transitioning(self):
        return self.clear_started_at is not None

    def spawn_current(self):
        self.stage_started_at = pg.time.get_ticks()
        self.clear_started_at = None
        self.world_width = self._stage_width()
        self.goal_rect = self._make_goal_rect()
        self.scenery = self._make_scenery()
        if self.is_boss_stage:
            return [self._spawn_boss()]
        return self._spawn_route_enemies()

    def goal_unlocked(self, enemies):
        if not self.is_boss_stage:
            return True
        for enemy in enemies:
            if enemy.is_boss and not enemy.defeated:
                return False
        return True

    def near_goal(self, player_rect):
        return player_rect.colliderect(self.goal_rect.inflate(36, 20))

    def update(self, enemies, player_rect=None, enter_pressed=False):
        """Advance only when Kirby enters the exit door."""
        if self.completed:
            return None

        now = pg.time.get_ticks()
        if self.transitioning:
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
            self.clear_started_at = now
        return None

    def draw_environment(self, surface, camera_x, enemies, font):
        """Draw the image-backed scenery and exit door."""
        self.scenery.draw(surface, camera_x)
        self._draw_goal(surface, camera_x, enemies, font)

    def _draw_goal(self, surface, camera_x, enemies, font):
        rect = self.goal_rect.move(-round(camera_x), 0)
        if rect.right < -50 or rect.left > surface.get_width() + 50:
            return

        unlocked = self.goal_unlocked(enemies)
        glow = pg.Surface((rect.width + 50, rect.height + 50), pg.SRCALPHA)
        glow_color = (255, 255, 220, 80) if unlocked else (80, 85, 100, 65)
        pg.draw.rect(
            glow,
            glow_color,
            glow.get_rect().inflate(-8, -8),
            border_radius=18,
        )
        surface.blit(glow, glow.get_rect(center=rect.center))

        frame_color = (255, 248, 185) if unlocked else (85, 85, 95)
        inside_color = (255, 255, 250) if unlocked else (45, 45, 55)
        pg.draw.rect(surface, frame_color, rect, border_radius=9)
        pg.draw.rect(surface, inside_color, rect.inflate(-12, -10), border_radius=6)

        if unlocked:
            label = font.render("↑ 입장", True, (60, 60, 70))
        else:
            label = font.render("보스를 쓰러뜨리세요", True, (170, 45, 50))
        surface.blit(label, label.get_rect(midbottom=(rect.centerx, rect.top - 8)))

    def _advance(self):
        if self.substage < self.SUBSTAGES:
            self.substage += 1
            return
        if self.world < self.TOTAL_WORLDS:
            self.world += 1
            self.substage = 1
            return
        self.completed = True
        self.clear_started_at = None

    def _stage_width(self):
        if self.is_boss_stage:
            return 1120
        widths = ROUTE_WIDTHS[self.world]
        return widths[self.substage - 1]

    def _make_goal_rect(self):
        return pg.Rect(self.world_width - 100, self.ground_y - 108, 58, 108)

    def _make_scenery(self):
        return StageScenery(self.world, self.substage, self.world_width, self.ground_y)

    def _spawn_route_enemies(self):
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
            count = 4

        elements = ("fire", "electric", "water", "earth")
        enemies = []
        route_start = 470
        route_end = self.world_width - 330
        spacing = (route_end - route_start) / (count - 1)

        for index in range(count):
            element = elements[index % len(elements)]
            offset = -35 if index % 2 == 0 else 35
            x = round(route_start + spacing * index + offset)
            enemy = create_enemy(
                element,
                x,
                0,
                difficulty=self.difficulty,
                level=self.world,
                ground_y=self.ground_y,
                world_width=self.world_width,
            )
            fly_offset = 0
            if element == "water":
                fly_offset = 90
                if index % 2 == 1:
                    fly_offset = 125
            enemy.set_spawn_bottom(self.ground_y - fly_offset)
            enemies.append(enemy)
        return enemies

    def _spawn_boss(self):
        element = BOSS_ELEMENTS[self.world - 1]
        enemy = create_enemy(
            element,
            760,
            0,
            difficulty=self.difficulty,
            is_boss=True,
            level=self.world,
            ground_y=self.ground_y,
            world_width=self.world_width,
        )
        fly_offset = 65 if element == "water" else 0
        enemy.set_spawn_bottom(self.ground_y - fly_offset)
        return enemy
