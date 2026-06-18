"""적 캐릭터, 적 발사체, 적 AI 행동을 정의하는 파일."""

import random

import pygame as pg

import load
from src.constants import (
    DIFFICULTY_SETTINGS,
    ELEMENTS,
    ENEMY_DATA,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
)

LEVEL_MULTIPLIERS = {
    # 월드가 뒤로 갈수록 적 체력/능력치를 조금씩 올리기 위한 배율이다.
    1: 1.0,
    2: 1.12,
    3: 1.24,
    4: 1.36,
    5: 1.48,
}


class EnemyProjectile(pg.sprite.Sprite):
    """적이 쏘는 발사체 Sprite."""

    def __init__(
        self,
        x,
        y,
        dx,
        dy,
        damage,
        element,
        radius=7,
        world_width=SCREEN_WIDTH,
    ):
        super().__init__()
        # dx/dy는 매 프레임 더해지는 이동량이다.
        self.dx = float(dx)
        self.dy = float(dy)
        self.damage = max(1, int(damage))
        self.element = element
        self.world_width = world_width
        self.frames = self._make_frames(radius)
        self.frame_index = 0
        self.frame_timer = pg.time.get_ticks()
        self.frame_ms = 75
        self.image = self.frames[0]
        self.rect = self.image.get_rect(center=(x, y))
        self._x = float(self.rect.x)
        self._y = float(self.rect.y)

    def update(self):
        """발사체를 움직이고, 월드 밖으로 나가면 제거한다."""
        self._animate()
        self._x += self.dx
        self._y += self.dy
        self.rect.x = round(self._x)
        self.rect.y = round(self._y)
        if (
            self.rect.right < -20
            or self.rect.left > self.world_width + 20
            or self.rect.bottom < -20
            or self.rect.top > SCREEN_HEIGHT + 20
        ):
            self.kill()

    def _make_frames(self, radius):
        """속성에 맞는 발사체 이미지를 만든다."""
        if self.element == "electric":
            size = 36 if radius >= 9 else 28
            frames = []
            for index in range(1, 4):
                image = load.load_image(f"spark{index}.png")
                frames.append(pg.transform.scale(image, (size, size)))
            return frames

        image = pg.Surface((radius * 2, radius * 2), pg.SRCALPHA)
        color = ELEMENTS[self.element]["color"]
        pg.draw.circle(image, color, (radius, radius), radius)
        pg.draw.circle(
            image,
            (255, 255, 255),
            (radius, radius),
            max(2, radius // 3),
        )
        return [image]

    def _animate(self):
        """여러 프레임이 있는 발사체만 애니메이션을 진행한다."""
        if len(self.frames) == 1:
            return
        now = pg.time.get_ticks()
        if now - self.frame_timer < self.frame_ms:
            return
        center = self.rect.center
        self.frame_timer = now
        self.frame_index = (self.frame_index + 1) % len(self.frames)
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_rect(center=center)
        self._x = float(self.rect.x)
        self._y = float(self.rect.y)


class Enemy(pg.sprite.Sprite):
    """일반 적과 보스를 모두 표현하는 Sprite 클래스."""

    def __init__(
        self,
        x,
        y,
        element,
        frames,
        data,
        difficulty="normal",
        is_boss=False,
        level=1,
        ground_y=None,
        world_width=SCREEN_WIDTH,
    ):
        super().__init__()
        settings = DIFFICULTY_SETTINGS[difficulty]
        # element와 ai_type은 적의 색, 공격 방식, 스프라이트를 결정한다.
        self.element = element
        self.color = ELEMENTS[element]["color"]
        self.ai_type = data["ai"]
        self.is_boss = is_boss
        self.inhaleable = not is_boss
        self.being_inhaled = False
        self.defeated = False

        scale = 1.65 if is_boss else 1.0
        self.frames = []
        for frame in frames:
            # 보스는 같은 스프라이트를 더 크게 키워 사용한다.
            width = max(1, round(frame.get_width() * scale))
            height = max(1, round(frame.get_height() * scale))
            self.frames.append(pg.transform.scale(frame, (width, height)))
        self.frame_idx = 0
        self.anim_timer = 0
        self.anim_speed = 105 if is_boss else 145
        self.image = self.frames[0]
        self.rect = self.image.get_rect(topleft=(x, y))

        level_multiplier = LEVEL_MULTIPLIERS.get(level, LEVEL_MULTIPLIERS[5])
        boss_hp_multiplier = 5.5 if is_boss else 1.0
        boss_damage_multiplier = 1.45 if is_boss else 1.0
        # 난이도, 월드 번호, 보스 여부를 모두 반영해 실제 전투 수치를 만든다.
        self.max_hp = max(
            1,
            round(
                data["hp"] * settings["hp_mult"] * level_multiplier * boss_hp_multiplier
            ),
        )
        self.hp = self.max_hp
        self.contact_damage = max(
            1,
            round(
                data["contact_damage"]
                * settings["damage_mult"]
                * boss_damage_multiplier
            ),
        )
        self.attack_damage = max(
            1,
            round(
                data["attack_damage"] * settings["damage_mult"] * boss_damage_multiplier
            ),
        )
        self.speed = data["speed"] * settings["speed_mult"] * (1.08 if is_boss else 1.0)
        self.patrol_range = data["patrol"] * (1.35 if is_boss else 1.0)
        self.detect_range = data["detect_x"] * settings["detect_mult"]
        self.detect_height = data["detect_y"] * settings["detect_mult"]
        self.lose_range = self.detect_range * 1.35
        self.lose_height = self.detect_height * 1.25
        self.attack_cooldown = round(data["cooldown"] * settings["cooldown_mult"])
        self.reaction_ms = settings["reaction_ms"]
        self.aim_error = settings["aim_error"]

        self.start_x = float(x)
        self.home_y = float(y)
        self.ground_y = ground_y if ground_y is not None else SCREEN_HEIGHT - 50
        self.world_width = world_width
        self.facing_right = False
        self.engaged = False
        self.state = "patrol"
        self.state_until = 0
        self.next_attack_at = pg.time.get_ticks() + random.randint(500, 1000)
        # 돌진형 공격은 시작 시점에 방향을 잠가 중간에 휘지 않게 한다.
        self.locked_direction = -1
        self.swoop_target = None
        self.air_moving_down = True
        self.pending_projectiles = []
        self.hit_flash_until = 0
        self.last_melee_serial = -1

    def set_spawn_bottom(self, bottom):
        """적의 바닥 위치를 맞추고 순찰 기준 위치도 함께 갱신한다."""
        self.rect.bottom = bottom
        self.home_y = float(self.rect.y)
        self.start_x = float(self.rect.x)

    def update(self, kirby=None, kirby_rect=None, ground_y=None, engage=True):
        """현재 상태에 따라 흡입, AI 행동, 순찰, 애니메이션을 진행한다."""
        if self.defeated:
            return
        if ground_y is not None:
            self.ground_y = ground_y
        target_rect = kirby.rect if kirby is not None else kirby_rect
        if self.being_inhaled and target_rect is not None and self.inhaleable:
            # Kirby가 흡입 중이면 AI보다 흡입 이동이 우선이다.
            self._pull_toward(target_rect)
        elif target_rect is not None and (self.is_boss or engage):
            self.engaged = True
            self._run_ai(target_rect)
        else:
            # 멀리 있는 적은 적극 공격 대신 가벼운 순찰만 한다.
            self.engaged = False
            self._passive_patrol()
            self._keep_in_bounds()
        self._animate()

    def can_recognize(self, target_rect):
        """플레이어가 이 적의 인식 범위 안에 있는지 확인한다."""
        if self.is_boss:
            return True
        horizontal = abs(target_rect.centerx - self.rect.centerx)
        vertical = abs(target_rect.centery - self.rect.centery)
        range_x = self.lose_range if self.engaged else self.detect_range
        # 이미 교전 중이면 바로 포기하지 않도록 lose_range를 더 넓게 쓴다.
        range_y = self.lose_height if self.engaged else self.detect_height
        return horizontal <= range_x and vertical <= range_y

    def take_damage(self, amount, source_x=None):
        """피해를 적용하고, 체력이 0이 되면 defeated 상태로 바꾼다."""
        if self.defeated:
            return 0
        dealt = round(amount)
        if dealt < 1:
            dealt = 1
        if dealt > self.hp:
            dealt = self.hp
        self.hp -= dealt
        now = pg.time.get_ticks()
        self.hit_flash_until = now + 110
        if source_x is not None and not self.is_boss:
            # 일반 적은 맞은 방향 반대로 살짝 밀려난다.
            direction = 1 if self.rect.centerx >= source_x else -1
            self.rect.x += direction * 5
        if self.hp <= 0:
            self.hp = 0
            self.defeated = True
            self.being_inhaled = False
        return dealt

    def draw(self, surface, camera_x=0):
        """적 이미지, 속성 마커, 체력바를 화면에 그린다."""
        image = self.image
        if pg.time.get_ticks() < self.hit_flash_until:
            image = image.copy()
            image.fill((255, 90, 90, 130), special_flags=pg.BLEND_RGBA_ADD)
        draw_rect = self.rect.move(-round(camera_x), 0)
        surface.blit(image, draw_rect)

        marker_y = draw_rect.top - 12
        pg.draw.circle(surface, self.color, (draw_rect.centerx, marker_y), 7)
        pg.draw.circle(surface, (255, 255, 255), (draw_rect.centerx, marker_y), 7, 1)
        self._draw_hp(surface, camera_x)

    # -------------------------------------------------------------- AI
    def _run_ai(self, target):
        """적 종류에 맞는 AI 함수로 행동을 분기한다."""
        now = pg.time.get_ticks()
        horizontal_distance = abs(target.centerx - self.rect.centerx)
        vertical_distance = abs(target.centery - self.rect.centery)
        self.facing_right = target.centerx >= self.rect.centerx

        if self.is_boss:
            self._boss_ai(target, horizontal_distance, now)
        elif self.ai_type == "chaser":
            self._chaser_ai(target, horizontal_distance, now)
        elif self.ai_type == "shooter":
            self._shooter_ai(target, horizontal_distance, now)
        elif self.ai_type == "swooper":
            self._swooper_ai(
                target,
                horizontal_distance,
                vertical_distance,
                now,
            )
        else:
            self._charger_ai(target, horizontal_distance, now)
        self._keep_in_bounds()

    def _chaser_ai(self, target, horizontal_distance, now):
        """불 속성처럼 플레이어에게 다가가 근접 돌진하는 AI."""
        if horizontal_distance > self.lose_range:
            self.state = "patrol"
            self._patrol()
            return
        if now >= self.next_attack_at and horizontal_distance < 74:
            self.state = "lunge"
            self.state_until = now + 300
            self.next_attack_at = now + self.attack_cooldown
        if self.state == "lunge" and now < self.state_until:
            self._move_x(self.speed * 2.8)
        else:
            self.state = "chase"
            self._move_x(self.speed * 1.25)

    def _shooter_ai(self, target, horizontal_distance, now):
        """전기 속성처럼 거리를 유지하며 발사체를 쏘는 AI."""
        if horizontal_distance > self.lose_range:
            self.state = "patrol"
            self._patrol()
            return
        if horizontal_distance < 120:
            self.state = "retreat"
            self._move_x(-self.speed)
        elif horizontal_distance > 225:
            self.state = "approach"
            self._move_x(self.speed)
        else:
            self.state = "aim"
        if now >= self.next_attack_at:
            self._shoot_at(target, speed=5.8)
            self.state = "shoot"
            self.next_attack_at = now + self.attack_cooldown

    def _swooper_ai(self, target, horizontal_distance, vertical_distance, now):
        """물 속성처럼 공중에서 목표 지점으로 급강하하는 AI."""
        if self.state == "swoop" and now < self.state_until and self.swoop_target:
            self._move_toward(*self.swoop_target, self.speed * 2.0)
            return
        if self.state == "recover":
            self._move_toward(self.start_x, self.home_y, self.speed * 1.35)
            if abs(self.rect.y - self.home_y) < 5:
                self.state = "patrol"
            return
        target_is_near = (
            horizontal_distance <= self.detect_range
            and vertical_distance <= self.detect_height
        )
        if target_is_near and now >= self.next_attack_at:
            error = random.randint(-self.aim_error, self.aim_error)
            self.swoop_target = (target.centerx + error, target.centery)
            self.state = "swoop"
            self.state_until = now + 620
            self.next_attack_at = now + self.attack_cooldown
            return
        if self.state == "swoop":
            self.state = "recover"
        else:
            self._air_patrol()

    def _charger_ai(self, target, horizontal_distance, now):
        """땅 속성처럼 준비 동작 후 한 방향으로 돌진하는 AI."""
        if self.state == "windup":
            if now >= self.state_until:
                self.state = "charge"
                self.state_until = now + 650
            return
        if self.state == "charge":
            if now < self.state_until:
                self.rect.x += round(self.locked_direction * self.speed * 3.4)
                return
            self.state = "patrol"
        if horizontal_distance <= self.detect_range and now >= self.next_attack_at:
            self.state = "windup"
            self.state_until = now + self.reaction_ms
            self.locked_direction = 1 if target.centerx > self.rect.centerx else -1
            self.next_attack_at = now + self.attack_cooldown
            return
        self._patrol()

    def _boss_ai(self, target, horizontal_distance, now):
        """보스 전용 AI. 돌진과 다중 발사체 공격을 섞어서 사용한다."""
        if self.state == "boss_dash":
            if now < self.state_until:
                self.rect.x += round(self.locked_direction * self.speed * 3.2)
                return
            self.state = "boss_chase"
        if now >= self.next_attack_at:
            if horizontal_distance < 185 or random.random() < 0.5:
                self.state = "boss_dash"
                self.locked_direction = 1 if target.centerx > self.rect.centerx else -1
                self.state_until = now + 720
            else:
                self.state = "boss_burst"
                for dy in (-2.3, 0, 2.3):
                    self._shoot_at(target, speed=6.5, dy_override=dy, radius=9)
            self.next_attack_at = now + max(600, self.attack_cooldown)
            return
        self.state = "boss_chase"
        if self.ai_type == "swooper":
            self._move_toward(target.centerx, target.centery - 45, self.speed)
        elif abs(target.centerx - self.rect.centerx) > 105:
            self._move_x(self.speed)

    def _shoot_at(self, target, speed, dy_override=None, radius=7):
        """목표 방향을 향해 적 발사체를 만들고 pending_projectiles에 저장한다."""
        direction = 1 if target.centerx >= self.rect.centerx else -1
        shot_dx = speed * direction

        shot_dy = dy_override
        if shot_dy is None:
            # 난이도별 aim_error를 넣어 쉬운 난이도에서는 조준이 덜 정확하게 한다.
            target_y = target.centery
            target_y += random.randint(-self.aim_error, self.aim_error)
            vertical_difference = target_y - self.rect.centery
            if vertical_difference < -25:
                shot_dy = -speed / 2
            elif vertical_difference > 25:
                shot_dy = speed / 2
            else:
                shot_dy = 0

        self.pending_projectiles.append(
            EnemyProjectile(
                self.rect.centerx,
                self.rect.centery,
                shot_dx,
                shot_dy,
                self.attack_damage,
                self.element,
                radius=radius,
                world_width=self.world_width,
            )
        )

    # -------------------------------------------------------------- movement
    def _patrol(self):
        """시작 위치와 patrol_range 사이를 좌우로 오가는 기본 순찰."""
        self.state = "patrol"
        if self.facing_right:
            self.rect.x += round(self.speed)
            if self.rect.x > self.start_x + self.patrol_range:
                self.facing_right = False
        else:
            self.rect.x -= round(self.speed)
            if self.rect.x < self.start_x:
                self.facing_right = True

    def _passive_patrol(self):
        """비활성 상태에서 적 종류에 맞는 기본 순찰을 한다."""
        if self.ai_type == "swooper":
            self._air_patrol()
        else:
            self._patrol()

    def _air_patrol(self):
        """공중 적이 좌우 이동과 함께 위아래로 살짝 떠다니게 한다."""
        self._patrol()
        if self.air_moving_down:
            self.rect.y += 1
            if self.rect.y >= self.home_y + 8:
                self.air_moving_down = False
        else:
            self.rect.y -= 1
            if self.rect.y <= self.home_y - 8:
                self.air_moving_down = True

    def _move_x(self, amount):
        """현재 바라보는 방향으로 amount만큼 이동한다."""
        direction = 1 if self.facing_right else -1
        self.rect.x += round(direction * amount)

    def _move_toward(self, x, y, speed):
        """목표 좌표 쪽으로 x/y를 각각 조금씩 이동한다."""
        step = max(1, round(speed))
        if x < self.rect.centerx:
            self.rect.x -= step
        elif x > self.rect.centerx:
            self.rect.x += step

        if y < self.rect.centery:
            self.rect.y -= step
        elif y > self.rect.centery:
            self.rect.y += step

    def _pull_toward(self, kirby_rect):
        """흡입될 때 Kirby 중심을 향해 빠르게 끌려가게 한다."""
        self._move_toward(kirby_rect.centerx, kirby_rect.centery, 10)

    def _keep_in_bounds(self):
        """적이 스테이지 밖이나 땅 아래로 빠지지 않게 위치를 제한한다."""
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > self.world_width:
            self.rect.right = self.world_width
        if self.ai_type != "swooper" and self.rect.bottom > self.ground_y:
            self.rect.bottom = self.ground_y
        if self.rect.top < 8:
            self.rect.top = 8

    def _animate(self):
        """현재 방향에 맞춰 스프라이트 프레임을 넘긴다."""
        now = pg.time.get_ticks()
        if now - self.anim_timer >= self.anim_speed:
            self.anim_timer = now
            self.frame_idx = (self.frame_idx + 1) % len(self.frames)
        raw = self.frames[self.frame_idx]
        self.image = raw if self.facing_right else pg.transform.flip(raw, True, False)

    def _draw_hp(self, surface, camera_x=0):
        """적 머리 위에 작은 체력바를 그린다."""
        width = 74 if self.is_boss else max(28, self.rect.width)
        height = 7 if self.is_boss else 4
        x = self.rect.centerx - round(camera_x) - width // 2
        y = self.rect.top - (28 if self.is_boss else 23)
        pg.draw.rect(surface, (45, 25, 25), (x, y, width, height))
        fill = round(width * self.hp / self.max_hp)
        pg.draw.rect(surface, (225, 45, 55), (x, y, fill, height))
        pg.draw.rect(surface, (255, 255, 255), (x, y, width, height), 1)


def create_enemy(
    element,
    x,
    y,
    difficulty="normal",
    is_boss=False,
    level=1,
    ground_y=None,
    world_width=SCREEN_WIDTH,
):
    """상수 데이터와 이미지 파일을 읽어 Enemy 객체 하나를 생성한다."""
    data = ENEMY_DATA[element]
    frames = []
    for name in data["frames"]:
        frames.append(load.load_image(name))
    return Enemy(
        x,
        y,
        element,
        frames,
        data,
        difficulty=difficulty,
        is_boss=is_boss,
        level=level,
        ground_y=ground_y,
        world_width=world_width,
    )
