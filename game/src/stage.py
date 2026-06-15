import math

import pygame as pg

from src.constants import DIFFICULTY_SETTINGS
from src.enemy import create_enemy


class StageManager:
    """Five worlds made of two scrolling routes and one boss area."""

    TOTAL_WORLDS = 5
    SUBSTAGES = 3
    CLEAR_DELAY_MS = 550

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
        if self.is_boss_stage:
            return [self._spawn_boss()]
        return self._spawn_route_enemies()

    def goal_unlocked(self, enemies):
        return not self.is_boss_stage or not any(
            enemy.is_boss and not enemy.defeated for enemy in enemies
        )

    def near_goal(self, player_rect):
        return player_rect.colliderect(self.goal_rect.inflate(36, 20))

    def update(self, enemies, player_rect=None, enter_pressed=False):
        """Advance only when Kirby enters the exit door."""
        if self.completed:
            return None

        now = pg.time.get_ticks()
        if self.transitioning:
            if now - self.clear_started_at < self.CLEAR_DELAY_MS:
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
        """Draw lightweight route staging while the full background is deferred."""
        camera_x = round(camera_x)
        palette = (
            ((205, 239, 255), (120, 205, 130), (75, 155, 85)),
            ((255, 232, 190), (205, 174, 95), (145, 115, 65)),
            ((220, 213, 255), (145, 125, 205), (92, 77, 150)),
            ((195, 235, 230), (90, 185, 170), (55, 125, 120)),
            ((235, 213, 230), (185, 105, 145), (120, 65, 100)),
        )[self.world - 1]
        sky, ground, ground_dark = palette
        surface.fill(sky)

        # Distant rounded hills move more slowly than the route.
        parallax = round(camera_x * 0.28)
        for x in range(-300, self.world_width + 500, 360):
            sx = x - parallax
            pg.draw.circle(surface, ground, (sx, self.ground_y + 55), 190)

        pg.draw.rect(
            surface,
            ground,
            (
                0,
                self.ground_y,
                surface.get_width(),
                surface.get_height() - self.ground_y,
            ),
        )
        pg.draw.line(
            surface,
            ground_dark,
            (0, self.ground_y),
            (surface.get_width(), self.ground_y),
            5,
        )

        # Sparse route markers make forward movement and camera scrolling readable.
        for x in range(260, self.world_width - 140, 420):
            sx = x - camera_x
            if -60 <= sx <= surface.get_width() + 60:
                pg.draw.rect(surface, ground_dark, (sx - 5, self.ground_y - 45, 10, 45))
                pg.draw.circle(surface, ground, (sx, self.ground_y - 58), 24)

        self._draw_goal(surface, camera_x, enemies, font)

    def _draw_goal(self, surface, camera_x, enemies, font):
        rect = self.goal_rect.move(-round(camera_x), 0)
        if rect.right < -50 or rect.left > surface.get_width() + 50:
            return

        unlocked = self.goal_unlocked(enemies)
        pulse = 8 + round(4 * math.sin(pg.time.get_ticks() / 160))
        glow = pg.Surface((rect.width + 50, rect.height + 50), pg.SRCALPHA)
        glow_color = (255, 255, 220, 80) if unlocked else (80, 85, 100, 65)
        pg.draw.rect(
            glow,
            glow_color,
            glow.get_rect().inflate(-pulse, -pulse),
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
        return 2550 + (self.world - 1) * 180 + (self.substage - 1) * 220

    def _make_goal_rect(self):
        return pg.Rect(self.world_width - 100, self.ground_y - 108, 58, 108)

    def _spawn_route_enemies(self):
        settings = DIFFICULTY_SETTINGS[self.difficulty]
        count = max(
            4,
            5 + settings["spawn_bonus"] + (self.world - 1) // 2 + self.substage - 1,
        )
        elements = ("fire", "electric", "water", "earth")
        enemies = []
        route_start = 470
        route_end = self.world_width - 330
        spacing = (route_end - route_start) / max(1, count - 1)

        for index in range(count):
            element = elements[(index + self.world + self.substage - 2) % len(elements)]
            offset = ((index * 83 + self.world * 41 + self.substage * 29) % 121) - 60
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
            fly_offset = 90 + (index % 2) * 35 if element == "water" else 0
            enemy.set_spawn_bottom(self.ground_y - fly_offset)
            enemies.append(enemy)
        return enemies

    def _spawn_boss(self):
        boss_elements = ("earth", "fire", "electric", "water", "earth")
        element = boss_elements[self.world - 1]
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
