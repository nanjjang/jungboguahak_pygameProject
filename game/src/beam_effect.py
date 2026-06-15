import random

import pygame as pg

import load

BEAM_MAX_ENERGY = 180  # 60fps 기준 3초
BEAM_ELEMENTS = {"fire", "water", "electric", "earth"}

# 에너지 회복 속도 (프레임당)
_REGEN = 0.8
_ELEMENT_FRAME_MS = 70

# ─── FireBeam: 스프라이트 기반 방향성 불 빔 ──────────────────────

_FIRE_FRAME_COUNT = 8
_FIRE_FRAME_MS = 80  # 프레임당 ms

_FIRE_SIZES = {  # (width, height) — 커비(26px) 기준 조율
    "horizontal": (84, 48),
    "vertical": (40, 80),
    "diagonal": (72, 52),
}
_FIRE_FOLDERS = {
    "horizontal": "01_horizontal_fire",
    "vertical": "02_vertical_fire",
    "diagonal": "06_diagonal_fire",
}


def _load_fire_frames(direction):
    folder = _FIRE_FOLDERS[direction]
    size = _FIRE_SIZES[direction]
    frames = []
    for i in range(1, _FIRE_FRAME_COUNT + 1):
        raw = load.load_image(f"{folder}/frame_{i:03d}.png").convert_alpha()
        frames.append(pg.transform.scale(raw, size))
    return frames


def _load_element_frames(element):
    if element == "water":
        return []
    if element == "electric":
        return [
            pg.transform.scale(
                load.load_image(f"spark{i}.png").convert_alpha(),
                (28, 28),
            )
            for i in range(1, 4)
        ]
    return []


class FireBeam:
    """스프라이트 기반 방향성 불 빔. BeamEffect와 동일한 인터페이스."""

    def __init__(self):
        self._frames = {}
        for direction in _FIRE_FOLDERS:
            self._frames[direction] = _load_fire_frames(direction)
        self.energy = BEAM_MAX_ENERGY
        self.active = False
        self.direction = "horizontal"
        self._frame_t = 0.0
        self._frame_i = 0
        self._kr = None  # 커비 rect (update마다 갱신)
        self._facing = True
        self._mouth = (0, 0)

    def try_activate(self, direction="horizontal"):
        if self.energy > 0:
            self.active = True
            if self.direction != direction:
                self.direction = direction
                self._frame_i = 0  # 방향 전환 시 첫 프레임부터
            return True
        return False

    def deactivate(self):
        self.active = False

    @property
    def energy_ratio(self):
        return self.energy / BEAM_MAX_ENERGY

    def update(self, mouth_x, mouth_y, facing_right, kirby_rect=None, **_):
        self._mouth = (mouth_x, mouth_y)
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
                n = len(self._frames[self.direction])
                self._frame_i = (self._frame_i + 1) % n

    def draw(self, surface, camera_x=0):
        if not self.active or self._kr is None:
            return
        raw = self._frames[self.direction][self._frame_i]
        fr = self._facing
        mx, my = self._mouth
        mx -= round(camera_x)

        if self.direction == "horizontal":
            img = raw if fr else pg.transform.flip(raw, True, False)
            rect = img.get_rect()
            if fr:
                rect.midleft = (mx, my)
            else:
                rect.midright = (mx, my)

        elif self.direction == "vertical":
            img = raw
            rect = img.get_rect()
            rect.midbottom = (mx, my)

        else:  # diagonal — 아래 대각선
            img = raw if fr else pg.transform.flip(raw, True, False)
            rect = img.get_rect()
            if fr:
                rect.topleft = (mx, my)
            else:
                rect.topright = (mx, my)

        surface.blit(img, rect)


class Particle:
    def __init__(self, x, y, dx, dy, color, size, life, gravity=0.0):
        self.x = float(x)
        self.y = float(y)
        self.dx = float(dx)
        self.dy = float(dy)
        self.color = color
        self.size = float(size)
        self.life = life
        self.max_life = life
        self.gravity = gravity

    @property
    def dead(self):
        return self.life <= 0

    def update(self):
        self.dy += self.gravity
        self.x += self.dx
        self.y += self.dy
        self.life -= 1


class BeamEffect:
    def __init__(self, element):
        self.element = element
        self.particles = []
        self.energy = BEAM_MAX_ENERGY
        self.active = False
        self._frames = _load_element_frames(element)
        self._frame_i = 0
        self._frame_t = 0.0
        self._mouth = (0, 0)
        self._facing = True
        self._water_splash = (
            load.load_image("07_kirby_collection/frame_259.png").convert_alpha()
            if element == "water"
            else None
        )

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
        self._mouth = (mouth_x, mouth_y)
        self._facing = facing_right

        if self.active:
            self.energy -= 1
            if self.energy <= 0:
                self.energy = 0
                self.active = False
            else:
                self._spawn_particles(mouth_x, mouth_y, facing_right)
        else:
            self.energy = min(BEAM_MAX_ENERGY, self.energy + _REGEN)

        active_particles = []
        for particle in self.particles:
            particle.update()
            if not particle.dead:
                active_particles.append(particle)
        self.particles = active_particles

        if self.active and self._frames:
            self._frame_t += 1000 / 60
            if self._frame_t >= _ELEMENT_FRAME_MS:
                self._frame_t -= _ELEMENT_FRAME_MS
                self._frame_i = (self._frame_i + 1) % len(self._frames)

    def _spawn_particles(self, mouth_x, mouth_y, facing_right):
        if self.element == "water":
            _spawn_water(self.particles, mouth_x, mouth_y, facing_right)
        elif self.element == "electric":
            _spawn_electric(self.particles, mouth_x, mouth_y, facing_right)
        elif self.element == "earth":
            _spawn_earth(self.particles, mouth_x, mouth_y, facing_right)

    def draw(self, surface, camera_x=0):
        has_sprite_effect = self.active and (
            self._frames or self._water_splash is not None
        )
        if not self.particles and not has_sprite_effect:
            return

        overlay = pg.Surface(surface.get_size(), pg.SRCALPHA)
        for p in self.particles:
            ratio = p.life / p.max_life
            r = max(1, int(p.size * ratio))
            alpha = int(220 * ratio)
            pos = (int(p.x - camera_x), int(p.y))
            pg.draw.circle(overlay, (*p.color, alpha), pos, r)
            # 불·빛은 안쪽에 밝은 코어 추가 → 자연스러운 발광
            if self.element in ("fire", "electric") and r > 3:
                inner_r = max(1, r // 2)
                red = min(255, p.color[0] + 110)
                green = min(255, p.color[1] + 110)
                blue = min(255, p.color[2] + 110)
                bright = (red, green, blue)
                pg.draw.circle(overlay, (*bright, alpha), pos, inner_r)

        # 불·빛: 가산 합성으로 겹치는 곳일수록 밝아짐
        flags = pg.BLEND_RGBA_ADD if self.element in ("fire", "electric") else 0
        surface.blit(overlay, (0, 0), special_flags=flags)

        if has_sprite_effect:
            self._draw_sprite_effect(surface, camera_x)

    def _draw_sprite_effect(self, surface, camera_x=0):
        mx, my = self._mouth
        mx -= round(camera_x)
        direction = 1 if self._facing else -1

        if self.element == "water":
            splash = self._water_splash
            if not self._facing:
                splash = pg.transform.flip(splash, True, False)
            splash_x = mx + direction * 43
            surface.blit(splash, splash.get_rect(center=(splash_x, my)))
            return

        if self.element == "electric":
            for i, distance in enumerate((12, 40, 68)):
                image = self._frames[(self._frame_i + i) % len(self._frames)]
                rect = image.get_rect(center=(mx + direction * distance, my))
                surface.blit(image, rect)


# ─── 속성별 파티클 스포너 ──────────────────────────────────────


def _spawn_water(particles, mx, my, facing_right):
    direction = 1 if facing_right else -1
    for _ in range(3):
        dx = direction * random.uniform(5, 8)
        dy = random.uniform(-2, 2)
        color = (random.randint(80, 160), random.randint(180, 230), 255)
        size = random.uniform(3, 7)
        life = random.randint(12, 20)
        particles.append(
            Particle(
                mx + direction * 24,
                my,
                dx,
                dy,
                color,
                size,
                life,
                gravity=0.18,
            )
        )


def _spawn_electric(particles, mx, my, facing_right):
    direction = 1 if facing_right else -1
    for _ in range(10):
        dx = direction * random.uniform(18, 26)
        dy = random.uniform(-2, 2)
        brightness = random.randint(200, 255)
        color = (brightness, brightness, random.randint(150, 220))
        size = random.uniform(5, 11)
        life = random.randint(6, 12)
        particles.append(Particle(mx, my, dx, dy, color, size, life, gravity=0.0))

    for _ in range(4):
        dx = direction * random.uniform(8, 15)
        dy = random.uniform(-6, 6)
        color = (255, 255, random.randint(80, 200))
        size = random.uniform(3, 6)
        life = random.randint(4, 8)
        particles.append(Particle(mx, my, dx, dy, color, size, life, gravity=0.0))


def _spawn_earth(particles, mx, my, facing_right):
    direction = 1 if facing_right else -1
    for _ in range(3):
        dx = direction * random.uniform(5, 9)
        dy = random.uniform(-4, 1)
        color = random.choice([(139, 90, 43), (100, 60, 20), (120, 75, 30)])
        size = random.uniform(13, 22)
        life = random.randint(22, 38)
        particles.append(Particle(mx, my, dx, dy, color, size, life, gravity=0.45))
    for _ in range(5):
        dx = direction * random.uniform(3, 7)
        dy = random.uniform(-4, 3)
        color = (
            random.randint(150, 180),
            random.randint(110, 140),
            random.randint(60, 90),
        )
        size = random.uniform(4, 8)
        life = random.randint(10, 20)
        particles.append(Particle(mx, my, dx, dy, color, size, life, gravity=0.35))
