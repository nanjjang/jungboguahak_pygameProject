"""전투 중 화면에 뜨는 데미지 숫자 표시를 담당한다."""

import random

import pygame as pg


class DamageNumber:
    """피해를 입은 위치 근처에 잠깐 떠오르는 빨간 데미지 숫자."""

    def __init__(self, amount, target_rect):
        # 숫자가 항상 최소 1 이상 보이도록 하고, 위치는 맞은 대상 주변으로 살짝 흔든다.
        self.amount = max(1, int(amount))
        self.x = float(target_rect.centerx + random.randint(-14, 14))
        self.y = float(target_rect.top + random.randint(-12, 6))
        self.created_at = pg.time.get_ticks()
        self.life_ms = 720
        self.font = pg.font.Font(None, 25)

    @property
    def alive(self):
        """표시 시간이 아직 남아 있으면 True를 반환한다."""
        return pg.time.get_ticks() - self.created_at < self.life_ms

    def update(self):
        """매 프레임 숫자를 위로 조금씩 올려 떠오르는 효과를 만든다."""
        self.y -= 0.65

    def draw(self, surface, camera_x=0):
        """카메라 위치를 빼서 월드 좌표를 화면 좌표로 바꾼 뒤 숫자를 그린다."""
        text = self.font.render(f"-{self.amount}", True, (225, 30, 30))
        shadow = self.font.render(f"-{self.amount}", True, (65, 0, 0))
        rect = text.get_rect(
            center=(round(self.x - camera_x), round(self.y)),
        )
        surface.blit(shadow, rect.move(1, 1))
        surface.blit(text, rect)
