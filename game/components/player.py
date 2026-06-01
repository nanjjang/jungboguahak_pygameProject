import pygame
from src.constants import BLUE, SCREEN_WIDTH, SCREEN_HEIGHT


class Player:
    def __init__(self, x, y, size):
        self.rect = pygame.Rect(x, y, size, size)
        self.color = BLUE
        self.speed = 5

        self.velocity_y = 0
        self.gravity = 0.6
        self.jump_power = -12
        self.is_jumping = False

    def move(self):
        keys = pygame.key.get_pressed()

        if keys[pygame.K_LEFT]:
            self.rect.x -= self.speed
            if self.rect.left < 0:
                self.rect.left = 0
        if keys[pygame.K_RIGHT]:
            self.rect.x += self.speed
            if self.rect.right > SCREEN_WIDTH:
                self.rect.right = SCREEN_WIDTH

        if keys[pygame.K_SPACE] and not self.is_jumping:
            self.velocity_y = self.jump_power
            self.is_jumping = True

    def update_physics(self):
        self.velocity_y += self.gravity
        self.rect.y += self.velocity_y

        ground_level = SCREEN_HEIGHT - 50 - self.rect.height
        if self.rect.y >= ground_level:
            self.rect.y = ground_level
            self.velocity_y = 0
            self.is_jumping = False

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect)
