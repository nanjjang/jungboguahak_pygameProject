import pygame as pg
import os, load

from src.constants import SCREEN_WIDTH, SCREEN_HEIGHT

class Kirby(pg.sprite.Sprite):
    def __init__(self, x, y):
        pg.sprite.Sprite.__init__(self)
        self.loadMove()
        self.loadJump()
        self.init(x, y)

    def init(self, x, y):
        self.image = self.idle_frames[0]
        self.rect = self.image.get_rect(topleft=(x, y))
        self.y_float = float(y)
        self.speed = 5
        self.velocity_y = 0.0
        self.gravity = 0.6
        self.is_jumping = False
        self.air_jumps = 0
        self.facing_right = True
        self.frame_w = 0
        self.anim_timer = 0
        self.anim_speed = 80

    def loadMove(self):
        self.kirby1 = load.load_image("Kirby1.png")
        self.kirbyMove1 = load.load_image("KirbyMove1.png")
        self.kirbyMove2 = load.load_image("KirbyMove2.png")
        self.kirbyMove3 = load.load_image("KirbyMove3.png")
        self.kirbyMove4 = load.load_image("KirbyMove4.png")
        self.kirbyMove5 = load.load_image("KirbyMove5.png")
        self.kirbyMove6 = load.load_image("KirbyMove6.png")
        self.kirbyMove7 = load.load_image("KirbyMove7.png")
        self.kirbyMove8 = load.load_image("KirbyMove8.png")
        self.kirbyMove9 = load.load_image("KirbyMove9.png")
        self.kirbyMove10 = load.load_image("KirbyMove10.png")
        self.idle_frames = [self.kirby1]
        self.move_frames = [self.kirbyMove1, self.kirbyMove2, self.kirbyMove3,
                            self.kirbyMove4, self.kirbyMove5, self.kirbyMove6,
                            self.kirbyMove7, self.kirbyMove8, self.kirbyMove9,
                            self.kirbyMove10]

    def loadJump(self):
        self.kirbyJump1 = load.load_image("kirbyJump1.png")
        self.kirbyJump7 = load.load_image("kirbyJump7.png")

    def update(self, screen, key, jump_pressed=False):
        self.kirbyControl(screen, key)
        self.checkState(jump_pressed)

    def kirbyControl(self, screen, key):
        moving = False
        if key[pg.K_LEFT]:
            self.rect.x -= self.speed
            if self.rect.left < 0:
                self.rect.left = 0
            self.facing_right = False
            moving = True
        if key[pg.K_RIGHT]:
            self.rect.x += self.speed
            if self.rect.right > SCREEN_WIDTH:
                self.rect.right = SCREEN_WIDTH
            self.facing_right = True
            moving = True

        if not self.is_jumping:
            frame = self._getMoveFrame(moving)
        elif self.velocity_y < 0:
            frame = self.kirbyJump1
        else:
            frame = self.kirbyJump7
        self.image = frame if self.facing_right else pg.transform.flip(frame, True, False)
        screen.blit(self.image, self.rect)

    def _getMoveFrame(self, moving):
        if not moving:
            return self.idle_frames[0]
        now = pg.time.get_ticks()
        if now - self.anim_timer >= self.anim_speed:
            self.anim_timer = now
            self.frame_w = (self.frame_w + 1) % len(self.move_frames)
        return self.move_frames[self.frame_w]

    def checkState(self, jump_pressed):
        if jump_pressed:
            if not self.is_jumping:
                self.velocity_y = -10.0
                self.is_jumping = True
            else :
                self.velocity_y = -6.0
                self.air_jumps += 1

        if self.is_jumping:
            self.velocity_y += self.gravity
            self.y_float += self.velocity_y
            self.rect.y = int(self.y_float)

        ground_level = SCREEN_HEIGHT - 50 - self.rect.height
        if self.rect.y >= ground_level:
            self.rect.y = ground_level
            self.y_float = float(ground_level)
            self.velocity_y = 0.0
            self.is_jumping = False
            self.air_jumps = 0

        if self.rect.y < 10:
            self.rect.y = 10
            self.y_float = 10.0
            self.velocity_y = 0.0

    def draw(self, surface):
        surface.blit(self.image, self.rect)
