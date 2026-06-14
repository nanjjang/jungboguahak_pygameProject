import os
import pygame as pg
import math
import random

BEAM_MAX_ENERGY = 180   # 60fps 기준 3초
BEAM_ELEMENTS   = {'fire', 'water', 'electric', 'earth'}

# 에너지 회복 속도 (프레임당)
_REGEN = 0.8

# ─── FireBeam: 스프라이트 기반 방향성 불 빔 ──────────────────────

_FIRE_FRAME_COUNT = 8
_FIRE_FRAME_MS    = 80   # 프레임당 ms

_FIRE_SIZES = {          # (width, height) — 커비(26px) 기준 조율
    'horizontal': (84, 48),
    'vertical':   (40, 80),
    'diagonal':   (72, 52),
}
_FIRE_FOLDERS = {
    'horizontal': '01_horizontal_fire',
    'vertical':   '02_vertical_fire',
    'diagonal':   '06_diagonal_fire',
}


def _load_fire_frames(direction):
    folder = _FIRE_FOLDERS[direction]
    size   = _FIRE_SIZES[direction]
    frames = []
    for i in range(1, _FIRE_FRAME_COUNT + 1):
        path = os.path.join('src', 'assets', 'images', folder, f'frame_{i:03d}.png')
        raw  = pg.image.load(path).convert_alpha()
        frames.append(pg.transform.scale(raw, size))
    return frames


class FireBeam:
    """스프라이트 기반 방향성 불 빔. BeamEffect와 동일한 인터페이스."""

    def __init__(self):
        self._frames   = {d: _load_fire_frames(d) for d in _FIRE_FOLDERS}
        self.energy    = BEAM_MAX_ENERGY
        self.active    = False
        self.direction = 'horizontal'
        self._frame_t  = 0.0
        self._frame_i  = 0
        self._kr       = None   # 커비 rect (update마다 갱신)
        self._facing   = True

    def try_activate(self, direction='horizontal'):
        if self.energy > 0:
            self.active = True
            if self.direction != direction:
                self.direction = direction
                self._frame_i  = 0      # 방향 전환 시 첫 프레임부터
            return True
        return False

    def deactivate(self):
        self.active = False

    @property
    def energy_ratio(self):
        return self.energy / BEAM_MAX_ENERGY

    def update(self, mouth_x, mouth_y, facing_right, kirby_rect=None, **_):
        if self.active:
            self.energy -= 1
            if self.energy <= 0:
                self.energy = 0
                self.active = False
        else:
            self.energy = min(BEAM_MAX_ENERGY, self.energy + _REGEN)

        self._facing = facing_right
        if kirby_rect is not None:
            self._kr = kirby_rect.copy()

        if self.active:
            self._frame_t += 1000 / 60
            if self._frame_t >= _FIRE_FRAME_MS:
                self._frame_t -= _FIRE_FRAME_MS
                n             = len(self._frames[self.direction])
                self._frame_i = (self._frame_i + 1) % n

    def draw(self, surface):
        if not self.active or self._kr is None:
            return
        raw = self._frames[self.direction][self._frame_i]
        kr  = self._kr
        fr  = self._facing

        if self.direction == 'horizontal':
            img  = raw if fr else pg.transform.flip(raw, True, False)
            rect = img.get_rect()
            if fr:
                rect.midleft  = (kr.right, kr.centery)
            else:
                rect.midright = (kr.left,  kr.centery)

        elif self.direction == 'vertical':
            img  = raw
            rect = img.get_rect()
            rect.midbottom = (kr.centerx, kr.top + 4)

        else:   # diagonal — 아래 대각선
            img  = raw if fr else pg.transform.flip(raw, True, False)
            rect = img.get_rect()
            if fr:
                rect.topleft  = (kr.right, kr.centery + 4)
            else:
                rect.topright = (kr.left,  kr.centery + 4)

        surface.blit(img, rect)


class Particle:
    __slots__ = ('x', 'y', 'dx', 'dy', 'color', 'size', 'life', 'max_life', 'gravity')

    def __init__(self, x, y, dx, dy, color, size, life, gravity=0.0):
        self.x, self.y   = float(x), float(y)
        self.dx, self.dy = float(dx), float(dy)
        self.color       = color
        self.size        = float(size)
        self.life        = life
        self.max_life    = life
        self.gravity     = gravity

    @property
    def dead(self):
        return self.life <= 0

    def update(self):
        self.dy  += self.gravity
        self.x   += self.dx
        self.y   += self.dy
        self.life -= 1


class BeamEffect:
    def __init__(self, element):
        self.element   = element
        self.particles = []
        self.energy    = BEAM_MAX_ENERGY
        self.active    = False

    def try_activate(self):
        if self.energy > 0:
            self.active = True
            return True
        return False

    def deactivate(self):
        self.active = False

    @property
    def energy_ratio(self):
        return self.energy / BEAM_MAX_ENERGY

    def update(self, mouth_x, mouth_y, facing_right, **_):
        if self.active:
            self.energy -= 1
            if self.energy <= 0:
                self.energy = 0
                self.active = False
            else:
                spawn = _SPAWNERS.get(self.element)
                if spawn:
                    spawn(self.particles, mouth_x, mouth_y, facing_right)
        else:
            self.energy = min(BEAM_MAX_ENERGY, self.energy + _REGEN)

        for p in self.particles:
            p.update()
        self.particles = [p for p in self.particles if not p.dead]

    def draw(self, surface):
        if not self.particles:
            return
        overlay = pg.Surface(surface.get_size(), pg.SRCALPHA)
        for p in self.particles:
            ratio = p.life / p.max_life
            r     = max(1, int(p.size * ratio))
            alpha = int(220 * ratio)
            pos   = (int(p.x), int(p.y))
            pg.draw.circle(overlay, (*p.color, alpha), pos, r)
            # 불·빛은 안쪽에 밝은 코어 추가 → 자연스러운 발광
            if self.element in ('fire', 'electric') and r > 3:
                inner_r = max(1, r // 2)
                bright  = tuple(min(255, c + 110) for c in p.color)
                pg.draw.circle(overlay, (*bright, alpha), pos, inner_r)

        # 불·빛: 가산 합성으로 겹치는 곳일수록 밝아짐
        flags = pg.BLEND_RGBA_ADD if self.element in ('fire', 'electric') else 0
        surface.blit(overlay, (0, 0), special_flags=flags)


# ─── 속성별 파티클 스포너 ──────────────────────────────────────

def _spawn_water(particles, mx, my, facing_right):
    d = 1 if facing_right else -1
    for _ in range(5):
        speed = random.uniform(6, 10)
        angle = random.uniform(-0.25, 0.25)
        dx    = d * speed * math.cos(angle)
        dy    = speed * math.sin(angle) - random.uniform(0.0, 1.5)
        color = (random.randint(80, 160), random.randint(180, 230), 255)
        size  = random.uniform(8, 16)
        life  = random.randint(18, 30)
        particles.append(Particle(mx, my, dx, dy, color, size, life, gravity=0.28))


def _spawn_electric(particles, mx, my, facing_right):
    d = 1 if facing_right else -1
    # 주 빔 — 빠르고 직선
    for _ in range(10):
        speed = random.uniform(18, 26)
        angle = random.uniform(-0.08, 0.08)
        dx    = d * speed * math.cos(angle)
        dy    = speed * math.sin(angle)
        b     = random.randint(200, 255)
        color = (b, b, random.randint(150, 220))
        size  = random.uniform(5, 11)
        life  = random.randint(6, 12)
        particles.append(Particle(mx, my, dx, dy, color, size, life, gravity=0.0))
    # 전기 스파크 — 넓게 흩어짐
    for _ in range(4):
        speed = random.uniform(8, 15)
        angle = random.uniform(-0.5, 0.5)
        dx    = d * speed * math.cos(angle)
        dy    = speed * math.sin(angle)
        color = (255, 255, random.randint(80, 200))
        size  = random.uniform(3, 6)
        life  = random.randint(4, 8)
        particles.append(Particle(mx, my, dx, dy, color, size, life, gravity=0.0))


def _spawn_earth(particles, mx, my, facing_right):
    d = 1 if facing_right else -1
    # 큰 돌덩이
    for _ in range(3):
        speed = random.uniform(5, 9)
        angle = random.uniform(-0.3, 0.3)
        dx    = d * speed * math.cos(angle)
        dy    = speed * math.sin(angle) - random.uniform(1, 2)
        color = random.choice([(139, 90, 43), (100, 60, 20), (120, 75, 30)])
        size  = random.uniform(13, 22)
        life  = random.randint(22, 38)
        particles.append(Particle(mx, my, dx, dy, color, size, life, gravity=0.45))
    # 흙먼지 잔여물
    for _ in range(5):
        speed = random.uniform(3, 7)
        angle = random.uniform(-0.5, 0.5)
        dx    = d * speed * math.cos(angle)
        dy    = speed * math.sin(angle) - random.uniform(0, 1)
        color = (random.randint(150, 180), random.randint(110, 140), random.randint(60, 90))
        size  = random.uniform(4, 8)
        life  = random.randint(10, 20)
        particles.append(Particle(mx, my, dx, dy, color, size, life, gravity=0.35))


_SPAWNERS = {
    'water':    _spawn_water,
    'electric': _spawn_electric,
    'earth':    _spawn_earth,
    # 'fire' 는 FireBeam이 스프라이트로 처리 — 여기서 제외
}
