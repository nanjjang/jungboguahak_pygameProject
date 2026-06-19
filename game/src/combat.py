# 데미지 숫자

import random

import pygame as pg


class DamageNumber:
    # 떠오르는 숫자

    def __init__(self, amount, target_rect):
        # 숫자 위치 살짝 흔듦
        self.amount = max(1, int(amount))
        self.x = float(target_rect.centerx + random.randint(-14, 14))
        self.y = float(target_rect.top + random.randint(-12, 6))
        self.created_at = pg.time.get_ticks()
        self.life_ms = 720
        self.font = pg.font.Font(None, 25)

    @property
    def alive(self):
        # 아직 보이는지
        return pg.time.get_ticks() - self.created_at < self.life_ms

    def update(self):
        # 위로 올라감
        self.y -= 0.65

    def draw(self, surface, camera_x=0):
        # 숫자 그리기
        text = self.font.render(f"-{self.amount}", True, (225, 30, 30))
        shadow = self.font.render(f"-{self.amount}", True, (65, 0, 0))
        rect = text.get_rect(
            center=(round(self.x - camera_x), round(self.y)),
        )
        surface.blit(shadow, rect.move(1, 1))
        surface.blit(text, rect)
