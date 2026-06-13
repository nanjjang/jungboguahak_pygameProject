import pygame as pg
import math
import load

from src.constants import ELEMENTS, ENEMY_DATA


class Enemy(pg.sprite.Sprite):
    def __init__(self, x, y, element, frames, speed, patrol_range):
        super().__init__()
        self.element     = element
        self.color       = ELEMENTS[element]['color']
        self.frames      = frames
        self.frame_idx   = 0
        self.anim_timer  = 0
        self.anim_speed  = 150
        self.image       = self.frames[0]
        self.rect        = self.image.get_rect(topleft=(x, y))
        self.speed       = speed
        self.patrol_range = patrol_range
        self.start_x     = x
        self.facing_right = True
        self.being_inhaled = False

    def update(self, kirby_rect=None):
        if self.being_inhaled and kirby_rect:
            self._pull_toward(kirby_rect)
        else:
            self._patrol()
        self._animate()

    def draw(self, surface):
        surface.blit(self.image, self.rect)
        pg.draw.circle(surface, self.color,       (self.rect.centerx, self.rect.top - 10), 7)
        pg.draw.circle(surface, (255, 255, 255),  (self.rect.centerx, self.rect.top - 10), 7, 1)

    # -------------------------------------------------------------- private
    def _patrol(self):
        if self.facing_right:
            self.rect.x += self.speed
            if self.rect.x > self.start_x + self.patrol_range:
                self.facing_right = False
        else:
            self.rect.x -= self.speed
            if self.rect.x < self.start_x:
                self.facing_right = True

    def _pull_toward(self, kirby_rect):
        dx = kirby_rect.centerx - self.rect.centerx
        dy = kirby_rect.centery - self.rect.centery
        dist = math.hypot(dx, dy)
        if dist > 0:
            self.rect.x += int(dx / dist * 10)
            self.rect.y += int(dy / dist * 10)

    def _animate(self):
        now = pg.time.get_ticks()
        if now - self.anim_timer >= self.anim_speed:
            self.anim_timer = now
            self.frame_idx = (self.frame_idx + 1) % len(self.frames)
        raw = self.frames[self.frame_idx]
        self.image = raw if self.facing_right else pg.transform.flip(raw, True, False)


def create_enemy(element, x, y):
    """ENEMY_DATA 설정만으로 적 생성 — 서브클래스 불필요."""
    data   = ENEMY_DATA[element]
    frames = [load.load_image(name) for name in data['frames']]
    return Enemy(x, y, element, frames, data['speed'], data['patrol'])
