import pygame as pg
import math
import load

from src.constants import ELEMENTS, KEYS, SCREEN_WIDTH, SCREEN_HEIGHT


class Kirby(pg.sprite.Sprite):
    def __init__(self, x, y):
        pg.sprite.Sprite.__init__(self)
        self._load_frames()
        self._init_state(x, y)

    # ---------------------------------------------------------------- init

    def is_empty(self):
        return len(self.ability_stack) <= 0

    def push(self, element):
        self.ability_stack.append(element)

    def pop(self):
        if self.is_empty():
            return '스택이 비어있음'
        return self.ability_stack.pop()

    def pop_same_ability(self, element):
        if self.is_empty():
            return '스택이 비어있음'
        return self.ability_stack.remove(element)

    def peek(self):
        if self.is_empty():
            return '스택이 비어있음'
        ptr = len(self.ability_stack) - 1
        return self.ability_stack[ptr]

    # ---------------------------------------------------------------------------------- stack functions

    def _load_frames(self):
        self.idle_frames = [load.load_image("Kirby1.png")]
        self.move_frames = [load.load_image(f"KirbyMove{i}.png") for i in range(1, 11)]
        self.jump_up     = load.load_image("kirbyJump1.png")
        self.jump_down   = load.load_image("kirbyJump7.png")

    def _init_state(self, x, y):
        self.image        = self.idle_frames[0]
        self.rect         = self.image.get_rect(topleft=(x, y))
        self.y_float      = float(y)
        self.speed        = 5
        self.velocity_y   = 0.0
        self.gravity      = 0.6
        self.is_jumping   = False
        self.air_jumps    = 0
        self.facing_right = True
        self.frame_w      = 0
        self.anim_timer   = 0
        self.anim_speed   = 80
        self.inhaling     = False
        self.inhale_range = 180
        self.held_element = None   # 입에 문 속성 (삼키기 전)
        self.ability_stack: list[str] = []   # 삼킨 능력 스택, 마지막 = 현재
        self.pending_projectiles: list[dict] = []
        self.font = load.get_korean_font(18)  # 매 프레임 생성하지 않도록 캐시

    # ---------------------------------------------------------------- update
    def update(self, key, jump_pressed=False, spit_pressed=False,
               attack_pressed=False, enemies=None, gulp_pressed=False):
        # 입에 문 상태일 때는 흡입 불가
        self.inhaling = bool(key[KEYS['inhale']]) and self.held_element is None
        self._handle_inhale(enemies)
        if spit_pressed:   self._on_spit()
        if attack_pressed: self._on_attack()
        if gulp_pressed: self._on_gulp()
        self._move(key)
        self._apply_gravity(jump_pressed)

    # ---------------------------------------------------------------- inhale
    def _get_inhale_rect(self):
        x  = self.rect.right if self.facing_right else self.rect.left - self.inhale_range
        return pg.Rect(x, self.rect.centery - 35, self.inhale_range, 70)

    def _handle_inhale(self, enemies):
        if enemies is None:
            return
        zone = self._get_inhale_rect()
        for enemy in list(enemies):
            if self.inhaling:
                if zone.colliderect(enemy.rect):
                    enemy.being_inhaled = True
            else:
                enemy.being_inhaled = False

            if enemy.being_inhaled and self.rect.colliderect(enemy.rect):
                self.held_element = enemy.element
                self.inhaling     = False
                enemies.remove(enemy)

    # ---------------------------------------------------------------- actions (context-aware)
    def _on_spit(self):
        """X키: 입에 문 상태 → 별 뱉기 / 능력 있음 → 능력 잃고 별 뱉기."""
        if self.held_element is not None:
            self.held_element = None
        elif self.ability_stack and not self.is_empty():
            self.pop()
        self._shoot('star')
    def _on_gulp(self):
        if self.held_element is not None:
            self._push_ability(self.held_element)
            self.held_element = None
    def _on_attack(self):
        """V키: 입에 문 상태 → 아무것도 안됨 / 능력 있음 → 속성 공격(능력 유지)."""
        if self.held_element is not None:
            pass
        elif not self.is_empty():
            self._shoot(self.peek())

    # ---------------------------------------------------------------- ability
    def _push_ability(self, element):
        """중복 제거 후 top에 추가 (move-to-top unique stack)."""
        if element in self.ability_stack:
            self.pop_same_ability(element)
        self.push(element)

    def _shoot(self, element):
        x = self.rect.right if self.facing_right else self.rect.left
        self.pending_projectiles.append({
            'x': x, 'y': self.rect.centery,
            'facing_right': self.facing_right,
            'element': element,
        })

    # ---------------------------------------------------------------- movement
    def _move(self, key):
        moving = False
        if key[pg.K_LEFT]:
            self.rect.x = max(0, self.rect.x - self.speed)
            self.facing_right = False
            moving = True
        if key[pg.K_RIGHT]:
            self.rect.x = min(SCREEN_WIDTH - self.rect.width, self.rect.x + self.speed)
            self.facing_right = True
            moving = True

        if not self.is_jumping:
            frame = self._anim_frame(moving)
        else:
            frame = self.jump_up if self.velocity_y < 0 else self.jump_down
        self.image = frame if self.facing_right else pg.transform.flip(frame, True, False)

    def _anim_frame(self, moving):
        if not moving:
            return self.idle_frames[0]
        now = pg.time.get_ticks()
        if now - self.anim_timer >= self.anim_speed:
            self.anim_timer = now
            self.frame_w = (self.frame_w + 1) % len(self.move_frames)
        return self.move_frames[self.frame_w]

    def _apply_gravity(self, jump_pressed):
        if jump_pressed:
            if not self.is_jumping:
                self.velocity_y = -10.0
                self.is_jumping = True
            else:
                self.velocity_y = -6.0
                self.air_jumps += 1

        if self.is_jumping:
            self.velocity_y += self.gravity
            self.y_float    += self.velocity_y
            self.rect.y      = int(self.y_float)

        ground = SCREEN_HEIGHT - 50 - self.rect.height
        if self.rect.y >= ground:
            self.rect.y   = ground
            self.y_float  = float(ground)
            self.velocity_y = 0.0
            self.is_jumping = False
            self.air_jumps  = 0
        if self.rect.y < 10:
            self.rect.y  = 10
            self.y_float = 10.0
            self.velocity_y = 0.0

    # ---------------------------------------------------------------- draw
    def draw(self, surface):
        surface.blit(self.image, self.rect)
        if self.held_element is not None:
            color = ELEMENTS[self.held_element]['color']
            bx = self.rect.right + 4 if self.facing_right else self.rect.left - 4
            r  = 10 + int(3 * abs(math.sin(pg.time.get_ticks() / 150)))
            pg.draw.circle(surface, color,          (bx, self.rect.centery), r)
            pg.draw.circle(surface, (255, 255, 255),(bx, self.rect.centery), r, 2)

    def draw_inhale_effect(self, surface):
        if not self.inhaling:
            return
        now     = pg.time.get_ticks()
        mouth_x = self.rect.right if self.facing_right else self.rect.left
        mouth_y = self.rect.centery

        pg.draw.rect(surface, (100, 180, 255), self._get_inhale_rect(), 2)

        for i in range(6):
            t      = (now / 300 + i / 6) % 1.0
            spread = (1 - t) * 50
            oy     = (i - 2.5) * (spread / 2.5)
            px     = int(mouth_x + (1 - t) * self.inhale_range * (1 if self.facing_right else -1))
            py     = int(mouth_y + oy)
            r      = max(3, int(9 * (1 - t) + 3))
            blue   = int(120 + 135 * t)
            pg.draw.circle(surface, (30, 140, blue), (px, py), r)

    def draw_hud(self, surface, key=None):
        font = self.font

        # Z키 감지 상태 (우상단)
        if key is not None:
            z_on  = key[KEYS['inhale']]
            color = (0, 180, 0) if z_on else (180, 0, 0)
            dbg   = font.render(f"Z키: {'ON' if z_on else 'OFF'}  inhaling: {self.inhaling}", True, color)
            surface.blit(dbg, (SCREEN_WIDTH - 220, 10))

        # 조작 안내 (하단)
        if self.held_element is not None:
            el    = ELEMENTS[self.held_element]
            guide = font.render(
                f"[{el['label']} 입에 문 중]  X: 뱉기   ↓: 삼키기   SPACE: 점프",
                True, el['color'])
        else:
            guide = font.render(
                "Z(홀드): 흡입   X: 능력뱉기   V: 능력사용   SPACE: 점프",
                True, (80, 80, 80))
        surface.blit(guide, (10, SCREEN_HEIGHT - 30))

        # 능력 스택 (좌상단)
        if not self.ability_stack:
            return
        surface.blit(font.render("능력 스택 (오른쪽=현재):", True, (40, 40, 40)), (10, 10))
        for i, element in enumerate(self.ability_stack):
            el        = ELEMENTS[element]
            is_active = (i == len(self.ability_stack) - 1)
            cx, cy    = 220 + i * 50, 18
            r         = 17 if is_active else 12
            pg.draw.circle(surface, el['color'],       (cx, cy), r)
            if is_active:
                pg.draw.circle(surface, (255, 255, 255), (cx, cy), r, 2)
            surface.blit(font.render(el['label'], True, (255, 255, 255)),
                         font.render(el['label'], True, (255, 255, 255)).get_rect(center=(cx, cy)))
