import pygame as pg
import load

from src.constants import ELEMENTS, SCREEN_WIDTH, SCREEN_HEIGHT
from src.beam_effect import BEAM_ELEMENTS, BeamEffect, FireBeam
from src import sfx

_BODY_SIZE = (26, 26)
_SPRITE_SIZE = (42, 36)


def _sprite(name, authored_left=False, canvas_size=_SPRITE_SIZE, angle=0):
    # 스프라이트 맞춤
    image = load.load_image(name)
    if authored_left:
        image = pg.transform.flip(image, True, False)
    if angle:
        image = pg.transform.rotate(image, angle)

    max_w, max_h = canvas_size[0] - 2, canvas_size[1] - 2
    scale = min(max_w / image.get_width(), max_h / image.get_height(), 1.0)
    if scale < 1.0:
        size = (
            max(1, round(image.get_width() * scale)),
            max(1, round(image.get_height() * scale)),
        )
        image = pg.transform.scale(image, size)

    canvas = pg.Surface(canvas_size, pg.SRCALPHA)
    canvas.blit(
        image, image.get_rect(midbottom=(canvas.get_width() // 2, canvas.get_height()))
    )
    return canvas


def _left_to_right(i):
    # 방향 맞춤
    return _sprite(f"07_kirby_collection/frame_{i:03d}.png", authored_left=True)


def _basic_frames(*indices):
    # 기본 프레임
    frames = []
    for index in indices:
        frames.append(_sprite(f"03_basic_kirby/frame_{index:03d}.png"))
    return frames


def _water_shot_frame(index):
    # 물 발사 프레임
    image = load.load_image(f"07_kirby_collection/frame_{index:03d}.png")
    canvas = pg.Surface((70, 42), pg.SRCALPHA)
    body_center_x = 10 if index != 258 else image.get_width() // 2
    x = canvas.get_width() // 2 - body_center_x
    canvas.blit(image, (x, canvas.get_height() - image.get_height()))
    return canvas


class _FrameAnimation:
    # 프레임 재생

    def __init__(self, frames=None, frame_interval_ms=80, loop=True):
        self.frames = frames or []
        self.frame_interval_ms = frame_interval_ms
        self.loop = loop
        self.frame_index = 0
        self.last_update = pg.time.get_ticks()
        self.active = bool(self.frames)

    def start(self, frames=None, frame_interval_ms=None):
        # 처음부터 재생
        if frames is not None:
            self.frames = frames
        if frame_interval_ms is not None:
            self.frame_interval_ms = frame_interval_ms
        self.frame_index = 0
        self.last_update = pg.time.get_ticks()
        self.active = bool(self.frames)

    def stop(self):
        # 재생 멈춤
        self.active = False

    def restart(self):
        # 다시 시작
        self.start()

    def use_frames(self, frames):
        # 프레임 바꾸기
        if self.frames is not frames:
            self.start(frames=frames)

    @property
    def current_frame(self):
        # 현재 프레임
        if not self.frames or not self.active:
            return None
        return self.frames[self.frame_index]

    def advance(self):
        # 다음 프레임
        if not self.frames or not self.active:
            return False

        now = pg.time.get_ticks()
        if now - self.last_update < self.frame_interval_ms:
            return False

        self.last_update = now
        next_index = self.frame_index + 1
        if next_index < len(self.frames):
            self.frame_index = next_index
            return True

        if self.loop:
            self.frame_index = 0
        else:
            self.stop()
        return True

    def frame(self):
        # 갱신하고 받기
        self.advance()
        return self.current_frame


class Kirby(pg.sprite.Sprite):
    # 플레이어

    def __init__(self, x, y):
        pg.sprite.Sprite.__init__(self)
        self._load_frames()
        self._init_state(x, y)

    # 능력 스택
    def is_empty(self):
        # 능력 없음
        return not self.ability_stack

    def push(self, element):
        # 능력 추가
        self.ability_stack.append(element)

    def pop(self):
        # 능력 빼기
        if self.is_empty():
            return "스택이 비어있음"
        return self.ability_stack.pop()

    def pop_same_ability(self, element):
        # 같은 능력 제거
        if self.is_empty():
            return "스택이 비어있음"
        return self.ability_stack.remove(element)

    def peek(self):
        # 현재 능력
        if self.is_empty():
            return "스택이 비어있음"
        return self.ability_stack[-1]

    # 이미지 로드
    def _load_frames(self):
        # 상태별 프레임
        # 기본 이동/근접
        self.idle_frames = _basic_frames(1)
        self.move_frames = _basic_frames(*range(15, 23))
        self.jump_up = _basic_frames(33)[0]
        self.jump_down = _basic_frames(23)[0]
        self.hover_frame = _sprite(
            "KSSU_Kirby_Hover_sprite.png",
        )

        # 흡입/물기/뱉기
        self.inhale_frames = []
        for index in range(98, 104):
            self.inhale_frames.append(_left_to_right(index))

        self.held_idle = _left_to_right(111)
        self.held_frames = []
        for index in range(112, 128):
            self.held_frames.append(_left_to_right(index))

        self.held_jump_up = _left_to_right(118)
        self.held_jump_down = _left_to_right(119)
        self.spit_frames = []
        for index in (107, 104, 108, 109):
            self.spit_frames.append(_left_to_right(index))

        breath_horizontal = _basic_frames(3, 49, 49, 3)
        water_move_frames = []
        for index in range(331, 347):
            frame_name = f"07_kirby_collection/frame_{index:03d}.png"
            water_move_frames.append(_sprite(frame_name))

        fire_vertical_frames = []
        for index in (3, 49, 49, 3):
            fire_vertical_frames.append(
                _sprite(
                    f"03_basic_kirby/frame_{index:03d}.png",
                    canvas_size=(46, 46),
                    angle=32,
                )
            )

        fire_diagonal_frames = []
        for index in (3, 49, 49, 3):
            fire_diagonal_frames.append(
                _sprite(
                    f"03_basic_kirby/frame_{index:03d}.png",
                    canvas_size=(44, 40),
                    angle=-18,
                )
            )

        water_shot_frames = []
        for index in (258, 254, 255, 256, 257, 256, 255, 254):
            water_shot_frames.append(_water_shot_frame(index))

        electric_frames = []
        for index in range(202, 214):
            electric_frames.append(
                _sprite(
                    f"07_kirby_collection/frame_{index:03d}.png",
                    canvas_size=(42, 52),
                )
            )

        self.element_forms = {
            # 장착 모습
            "water": {
                "idle": _sprite("07_kirby_collection/frame_337.png"),
                "move": water_move_frames,
                "jump_up": _sprite("07_kirby_collection/frame_351.png"),
                "jump_down": _sprite("07_kirby_collection/frame_357.png"),
            },
        }
        self.ability_frames = {
            # 빔 자세
            "fire": {
                "horizontal": breath_horizontal,
                "vertical": fire_vertical_frames,
                "diagonal": fire_diagonal_frames,
            },
            "water": {
                "horizontal": water_shot_frames,
            },
            "electric": {
                "horizontal": electric_frames,
            },
            "earth": {"horizontal": breath_horizontal},
        }

        # 펀치/킥 콤보
        self.attack_combos = {
            "punch": [
                {
                    "name": "잽",
                    "frames": _basic_frames(1, 64, 68, 66, 1),
                    "frame_interval_ms": 36,
                    "hit_frames": (2, 3),
                    "hitbox": (28, 2, 22),
                    "damage": 12,
                    "motion": {2: 1},
                },
                {
                    "name": "크로스",
                    "frames": _basic_frames(1, 69, 72, 76, 77, 1),
                    "frame_interval_ms": 38,
                    "hit_frames": (2, 3, 4),
                    "hitbox": (34, 0, 25),
                    "damage": 18,
                    "motion": {2: 2, 3: 1},
                },
                {
                    "name": "브레이크 피니시",
                    "frames": _basic_frames(1, 55, 58, 68, 76, 77, 1),
                    "frame_interval_ms": 40,
                    "hit_frames": (3, 4, 5),
                    "hitbox": (40, -4, 32),
                    "damage": 30,
                    "motion": {2: 2, 3: 3, 4: 2},
                },
            ],
            "kick": [
                {
                    "name": "단발 킥",
                    "frames": _basic_frames(1, 100, 101, 104, 1),
                    "frame_interval_ms": 42,
                    "hit_frames": (1, 2, 3),
                    "hitbox": (32, -8, 34),
                    "damage": 16,
                    "motion": {1: 1, 2: 1},
                },
                {
                    "name": "에어리얼 체인",
                    "frames": _basic_frames(1, 90, 91, 94, 96, 99, 1),
                    "frame_interval_ms": 40,
                    "hit_frames": (1, 3, 4, 5),
                    "hitbox": (38, -8, 38),
                    "damage": 23,
                    "motion": {2: 2, 3: 2, 4: 2},
                },
                {
                    "name": "소머솔트 피니시",
                    "frames": _basic_frames(1, 94, 96, 100, 101, 104, 1),
                    "frame_interval_ms": 42,
                    "hit_frames": (1, 2, 4, 5, 6),
                    "hitbox": (42, -12, 40),
                    "damage": 36,
                    "motion": {2: 2, 3: 2, 4: 3, 5: 2},
                },
            ],
        }

    # 초기값
    def _init_state(self, x, y):
        # 커비 상태
        self.image = self.idle_frames[0]
        self.rect = pg.Rect(x, y, *_BODY_SIZE)
        self.y_float = float(y)
        self.spawn_point = (x, y)
        self.world_width = SCREEN_WIDTH

        # 체력 / 생명
        self.max_hp = 100
        self.hp = self.max_hp
        self.lives = 3
        self.game_over = False
        self.invulnerable_until = 0
        self.hit_flash_until = 0

        # 이동
        self.speed = 3
        self.velocity_y = 0.0
        self.gravity = 0.6
        self.is_jumping = False
        self.facing_right = True
        self.walk_animation = _FrameAnimation(self.move_frames, 80)

        # 입력 확인
        self._prev_jump_held = False
        self._was_punch_held = False
        self._was_kick_held = False

        # 흡입 / 호버
        self.inhaling = False
        self.inhale_animation = _FrameAnimation(self.inhale_frames, 75)
        self.hovering = False
        self.jump_held = False
        self.hover_held = False
        self.inhale_range = 180

        # 물기 / 능력
        self.held_element = None
        self.ability_stack = []
        self.held_animation = _FrameAnimation(self.held_frames, 85)
        self.ability_animation = _FrameAnimation(frame_interval_ms=70)
        self.ability_frame_key = None

        # 뱉기 애니메이션
        self.spit_animation = _FrameAnimation(self.spit_frames, 60, loop=False)
        self.spit_animation.stop()

        # 근접 콤보
        self.attack_kind = None
        self.attack_stage = -1
        self.attack_animation = _FrameAnimation(loop=False)
        self.attack_buffer_count = 0
        self.attack_chain_kind = None
        self.attack_chain_stage = 0
        self.attack_chain_expires_at = 0
        self.attack_chain_window_ms = 220
        self.attack_serial = 0

        # 기타
        self.pending_projectiles = []
        self._beams = {}
        self.beam_hit_cooldown_frames = 0
        self.font = load.get_korean_font(18)

    def _beam_sound_name(self, element):
        # 빔 효과음
        return {
            "fire": "beam_fire",
            "water": "beam_water",
            "earth": "beam_earth",
        }.get(element, "beam")

    def _stop_held_sounds(self):
        # 지속음 끄기
        sfx.stop("inhale")
        for name in ("beam", "beam_fire", "beam_water", "beam_earth"):
            sfx.stop(name)

    def _sync_beam_sound(self, active_name):
        # 지속음 맞춤
        for name in ("beam", "beam_fire", "beam_water", "beam_earth"):
            if name == active_name:
                sfx.loop(name)
            else:
                sfx.stop(name)

    # 업데이트
    def update(
        self,
        controls,
        enemies=None,
        *,
        terrain_rects=None,
        ground_y=None,
        spit_pressed=False,
        gulp_pressed=False,
        punch_pressed=False,
        kick_pressed=False,
    ):
        # 한 프레임 처리
        # 흡입 가능 여부
        self.inhaling = (
            controls.inhale_held
            and self.held_element is None
            and not self._in_attack()
        )
        if self.inhaling:
            sfx.loop("inhale")
        else:
            sfx.stop("inhale")

        self.jump_held = controls.jump_held
        self.hover_held = self.jump_held and controls.hover_modifier_held

        # 펀치/킥 입력
        d_held = controls.punch_held
        f_held = controls.kick_held
        just_punch = punch_pressed or (d_held and not self._was_punch_held)
        just_kick = kick_pressed or (f_held and not self._was_kick_held)
        self._was_punch_held = d_held
        self._was_kick_held = f_held

        can_attack = (
            self.held_element is None
            and not self.spit_animation.active
            and not self.inhaling
        )
        if just_punch and can_attack:
            self._on_attack("punch")
        if just_kick and can_attack:
            self._on_attack("kick")

        self._handle_inhale(enemies)
        # 단발 입력 처리
        if spit_pressed and not self._in_attack():
            self._on_spit()
        if gulp_pressed:
            self._on_gulp()
        self._update_beams(controls.beam_held, controls)
        moving = self._move(controls)
        self._apply_gravity(
            self.jump_held,
            self.hover_held,
            terrain_rects=terrain_rects,
            ground_y=ground_y,
        )
        self._update_image(moving)

    # 도움 함수
    def _in_attack(self):
        # 공격 중
        return self.attack_kind is not None

    def _current_attack(self):
        # 현재 콤보
        if not self._in_attack():
            return None
        return self.attack_combos[self.attack_kind][self.attack_stage]

    # 흡입
    def _get_inhale_rect(self):
        # 흡입 판정
        x = self.rect.right if self.facing_right else self.rect.left - self.inhale_range
        return pg.Rect(x, self.rect.centery - 35, self.inhale_range, 70)

    def _handle_inhale(self, enemies):
        # 적 빨아들이기
        if enemies is None:
            return
        zone = self._get_inhale_rect()
        for enemy in list(enemies):
            if not enemy.inhaleable or enemy.defeated:
                enemy.being_inhaled = False
                continue
            if self.inhaling:
                if zone.colliderect(enemy.rect):
                    enemy.being_inhaled = True
            else:
                enemy.being_inhaled = False

            if enemy.being_inhaled and self.rect.colliderect(enemy.rect):
                # 닿으면 물기
                self.held_element = enemy.element
                self.inhaling = False
                self.held_animation.restart()
                enemies.remove(enemy)

    # 행동
    def _on_spit(self):
        # 뱉기
        if self.held_element is not None:
            self.held_element = None
        elif not self.is_empty():
            self.pop()
        sfx.play_sfx("spit", cooldown_ms=220)
        self.spit_animation.start()
        self._shoot("star")

    def _on_gulp(self):
        # 삼키기
        if self.held_element is not None:
            self._push_ability(self.held_element)
            self.held_element = None

    def _on_attack(self, kind):
        # 근접 공격
        if not self._in_attack():
            now = pg.time.get_ticks()
            stage = (
                self.attack_chain_stage
                if (
                    kind == self.attack_chain_kind
                    and now <= self.attack_chain_expires_at
                )
                else 0
            )
            self._start_attack(kind, stage)
            return
        if self.attack_kind != kind:
            return
        remaining_stages = len(self.attack_combos[kind]) - self.attack_stage - 1
        if self.attack_buffer_count < remaining_stages:
            self.attack_buffer_count += 1

    def _start_attack(self, kind, stage, buffer_count=0):
        # 콤보 시작
        self.attack_kind = kind
        self.attack_stage = stage
        attack = self._current_attack()
        self.attack_animation.start(
            frames=attack["frames"],
            frame_interval_ms=attack["frame_interval_ms"],
        )
        self.attack_buffer_count = buffer_count
        self.attack_serial += 1
        self.attack_chain_kind = None
        self.attack_chain_stage = 0
        self.attack_chain_expires_at = 0
        sfx.play_sfx("melee", cooldown_ms=90)
        self._apply_attack_motion()

    def _finish_attack(self):
        # 공격 끝
        kind = self.attack_kind
        next_stage = self.attack_stage + 1
        self.attack_kind = None
        self.attack_stage = -1
        self.attack_animation.stop()
        self.attack_buffer_count = 0
        if kind is not None and next_stage < len(self.attack_combos[kind]):
            self.attack_chain_kind = kind
            self.attack_chain_stage = next_stage
            self.attack_chain_expires_at = (
                pg.time.get_ticks() + self.attack_chain_window_ms
            )
        else:
            self.attack_chain_kind = None
            self.attack_chain_stage = 0
            self.attack_chain_expires_at = 0

    # 빔
    def _get_beam(self, element):
        # 빔 가져오기
        if element not in self._beams:
            self._beams[element] = (
                FireBeam() if element == "fire" else BeamEffect(element)
            )
        return self._beams[element]

    def _get_fire_direction(self, controls):
        # 불 빔 방향
        if controls.up_held:
            return "vertical"
        if controls.down_held and self.is_jumping:
            return "diagonal"
        return "horizontal"

    def _update_beams(self, attack_held, controls=None):
        # 빔 상태
        active_sound = None
        if self.is_empty() or self.held_element is not None or self._in_attack():
            for beam in self._beams.values():
                beam.deactivate()
        else:
            current = self.peek()
            if current in BEAM_ELEMENTS:
                beam = self._get_beam(current)
                if attack_held:
                    if current == "fire" and controls is not None:
                        beam.try_activate(self._get_fire_direction(controls))
                    else:
                        beam.try_activate()
                    if beam.active:
                        active_sound = self._beam_sound_name(current)
                else:
                    beam.deactivate()

        for element, beam in self._beams.items():
            # 입 위치 기준
            direction = beam.direction
            mouth_x, mouth_y = self._beam_mouth_position(direction)
            if element == "fire":
                beam.update(mouth_x, mouth_y, self.facing_right, kirby_rect=self.rect)
            else:
                beam.update(mouth_x, mouth_y, self.facing_right)

        if self.beam_hit_cooldown_frames > 0:
            self.beam_hit_cooldown_frames -= 1
        self._sync_beam_sound(active_sound)

    def _active_beam_state(self):
        # 활성 빔
        if self.is_empty() or self.held_element is not None:
            return None
        current = self.peek()
        beam = self._beams.get(current)
        if current not in self.ability_frames or beam is None or not beam.active:
            return None
        return current, beam.direction

    def _equipped_form(self):
        # 장착 모습
        if self.is_empty() or self.held_element is not None:
            return None
        current = self.peek()
        return current if current in self.element_forms else None

    def _beam_mouth_position(self, direction):
        # 빔 시작점
        if direction == "vertical":
            x_offset = 6 if self.facing_right else -6
            return self.rect.centerx + x_offset, self.rect.top - 10
        if direction == "diagonal":
            x = self.rect.right if self.facing_right else self.rect.left
            return x, self.rect.centery + 5
        x = self.rect.right if self.facing_right else self.rect.left
        return x, self.rect.centery - 1

    @property
    def active_beam_rect(self):
        # 빔 판정
        if self.is_empty() or self.held_element is not None:
            return None
        current = self.peek()
        if current not in BEAM_ELEMENTS or current not in self._beams:
            return None
        beam = self._beams[current]
        if not beam.active:
            return None
        facing_right = self.facing_right
        direction = beam.direction
        mouth_x, mouth_y = self._beam_mouth_position(direction)
        if direction == "vertical":
            return pg.Rect(mouth_x - 20, mouth_y - 80, 40, 80)
        if direction == "diagonal":
            x = mouth_x if facing_right else mouth_x - 72
            return pg.Rect(x, mouth_y, 72, 52)
        x = mouth_x if facing_right else mouth_x - 84
        return pg.Rect(x, mouth_y - 24, 84, 48)

    @property
    def melee_hit_rect(self):
        # 근접 판정
        attack = self._current_attack()
        if (
            attack is None
            or self.attack_animation.frame_index not in attack["hit_frames"]
        ):
            return None

        body_rect = self.rect
        reach, top_offset, height = attack["hitbox"]
        x = body_rect.right - 4 if self.facing_right else body_rect.left - reach + 4
        return pg.Rect(x, body_rect.top + top_offset, reach, height)

    @property
    def melee_damage(self):
        # 근접 데미지
        attack = self._current_attack()
        if (
            attack is None
            or self.attack_animation.frame_index not in attack["hit_frames"]
        ):
            return 0
        return attack["damage"]

    @property
    def beam_damage(self):
        # 빔 데미지
        if self.is_empty():
            return 0
        return {
            "fire": 10,
            "water": 7,
            "electric": 9,
            "earth": 12,
        }.get(self.peek(), 0)

    # 능력
    def _push_ability(self, element):
        # 능력 복사
        if element in self.ability_stack:
            self.pop_same_ability(element)
        self.push(element)
        sfx.play_sfx("copy", cooldown_ms=250)

    def _shoot(self, element):
        # 발사 예약
        x = self.rect.right if self.facing_right else self.rect.left
        self.pending_projectiles.append(
            {
                "x": x,
                "y": self.rect.centery,
                "facing_right": self.facing_right,
                "element": element,
            }
        )

    # 체력
    @property
    def invulnerable(self):
        # 무적 상태
        return pg.time.get_ticks() < self.invulnerable_until

    def set_spawn_point(self, x, y):
        # 시작 위치
        self.spawn_point = (x, y)

    def set_world_bounds(self, width):
        # 이동 범위
        self.world_width = max(SCREEN_WIDTH, int(width))
        self.rect.x = min(self.rect.x, self.world_width - self.rect.width)

    def reset_position(self):
        # 위치 초기화
        self.rect.topleft = self.spawn_point
        self.y_float = float(self.rect.y)
        self.velocity_y = 0.0
        self.is_jumping = False
        self.hovering = False
        self.inhaling = False
        self._finish_attack()
        self.attack_chain_kind = None
        self.attack_chain_stage = 0
        self.attack_chain_expires_at = 0
        for beam in self._beams.values():
            beam.deactivate()
        self._stop_held_sounds()

    def take_damage(self, amount, source_x=None):
        # 피해 받기
        if self.game_over or self.invulnerable:
            return 0
        dealt = min(self.hp, max(1, round(amount)))
        self.hp -= dealt
        now = pg.time.get_ticks()
        self.hit_flash_until = now + 180
        self.invulnerable_until = now + 900

        if source_x is not None:
            # 넉백
            direction = 1 if self.rect.centerx >= source_x else -1
            self.rect.x = max(
                0,
                min(self.world_width - self.rect.width, self.rect.x + direction * 24),
            )
        self.velocity_y = -4.2
        self.is_jumping = True
        self._stop_held_sounds()

        if self.hp <= 0:
            sfx.play_sfx("player_down", cooldown_ms=600)
            # 목숨 처리
            self.lives -= 1
            if self.lives > 0:
                self.hp = self.max_hp
                self.reset_position()
                self.invulnerable_until = now + 1600
            else:
                self.hp = 0
                self.game_over = True
                self.inhaling = False
                self._finish_attack()
                for beam in self._beams.values():
                    beam.deactivate()
        else:
            sfx.play_sfx("player_hit", cooldown_ms=420)
        return dealt

    # 프레임 고르기
    def _get_inhale_frame(self):
        # 흡입 프레임
        return self.inhale_animation.frame()

    def _get_held_frame(self, moving):
        # 물고 있는 프레임
        if not moving:
            self.held_animation.restart()
            return self.held_idle
        return self.held_animation.frame()

    def _get_ability_frame(self, element, direction):
        # 능력 프레임
        frame_sets = self.ability_frames[element]
        direction = direction if direction in frame_sets else "horizontal"
        frame_key = (element, direction)
        frames = frame_sets[direction]

        if self.ability_frame_key != frame_key:
            self.ability_frame_key = frame_key
            self.ability_animation.start(frames=frames)

        return self.ability_animation.frame()

    def _advance_attack_frame(self):
        # 공격 프레임
        attack = self._current_attack()
        if attack is None:
            return

        if not self.attack_animation.advance():
            return

        if self.attack_animation.active:
            self._apply_attack_motion()
            return

        if (
            self.attack_buffer_count > 0
            and self.attack_stage < len(self.attack_combos[self.attack_kind]) - 1
        ):
            # 같은 키면 예약
            kind = self.attack_kind
            self._start_attack(
                kind,
                self.attack_stage + 1,
                buffer_count=self.attack_buffer_count - 1,
            )
        else:
            self._finish_attack()

    def _apply_attack_motion(self):
        # 공격 이동
        attack = self._current_attack()
        if attack is None:
            return
        distance = attack["motion"].get(self.attack_animation.frame_index, 0)
        if distance == 0:
            return
        direction = 1 if self.facing_right else -1
        self.rect.x = max(
            0,
            min(self.world_width - self.rect.width, self.rect.x + distance * direction),
        )

    # 이동
    def _move(self, controls):
        # 좌우 이동
        if self._in_attack():
            return False

        moving = False
        if controls.left_held:
            self.rect.x = max(0, self.rect.x - self.speed)
            self.facing_right = False
            moving = True
        if controls.right_held:
            self.rect.x = min(
                self.world_width - self.rect.width, self.rect.x + self.speed
            )
            self.facing_right = True
            moving = True
        return moving

    def _update_image(self, moving):
        # 최종 이미지
        spit_frame = self.spit_animation.frame()
        self._advance_attack_frame()

        attack = self._current_attack()
        if attack is not None:
            # 공격 우선
            frame = self.attack_animation.current_frame
        elif spit_frame is not None:
            frame = spit_frame
        elif self.inhaling:
            frame = self._get_inhale_frame()
        elif self.held_element is not None:
            # 입에 문 상태
            if self.is_jumping:
                frame = (
                    self.held_jump_up if self.velocity_y < 0 else self.held_jump_down
                )
            else:
                frame = self._get_held_frame(moving)
        else:
            ability_state = self._active_beam_state()
            form_element = self._equipped_form()
            if ability_state is not None:
                # 빔 자세
                frame = self._get_ability_frame(
                    ability_state[0],
                    ability_state[1],
                )
            elif form_element is not None:
                form = self.element_forms[form_element]
                if self.is_jumping:
                    if self.velocity_y < 0:
                        frame = form["jump_up"]
                    else:
                        frame = form["jump_down"]
                elif moving:
                    frame = self._get_walk_frame(moving, form["move"])
                else:
                    frame = form["idle"]
            elif self.hovering and self.hover_held:
                frame = self.hover_frame
            elif not self.is_jumping:
                frame = self._get_walk_frame(moving)
            else:
                frame = self.jump_up if self.velocity_y < 0 else self.jump_down

        if not self.inhaling:
            # 흡입 프레임 리셋
            self.inhale_animation.restart()
        if self._active_beam_state() is None:
            self.ability_animation.stop()
            self.ability_frame_key = None
        self.image = (
            frame if self.facing_right else pg.transform.flip(frame, True, False)
        )

    def _get_walk_frame(self, moving, frames=None):
        # 걷기 프레임
        frames = self.move_frames if frames is None else frames
        if not moving:
            self.walk_animation.restart()
            return self.idle_frames[0]
        self.walk_animation.use_frames(frames)
        return self.walk_animation.frame()

    # 점프/중력
    def _apply_gravity(
        self,
        jump_held,
        hover_held=False,
        terrain_rects=None,
        ground_y=None,
    ):
        # 점프 처리
        terrain_rects = terrain_rects or ()
        floor_y = SCREEN_HEIGHT - 50 if ground_y is None else ground_y
        if not self.is_jumping:
            walking_floor = self._walkable_floor(terrain_rects, floor_y)
            if walking_floor is None:
                if self.rect.bottom < floor_y:
                    # 발판 밖이면 낙하
                    self.is_jumping = True
                    self.velocity_y = max(self.velocity_y, 2.0)
            else:
                self.rect.bottom = walking_floor
                self.y_float = float(self.rect.y)

        just_pressed = jump_held and not self._prev_jump_held
        self._prev_jump_held = jump_held

        if just_pressed:
            if not self.is_jumping:
                # 첫 점프
                self.velocity_y = -10.0
                self.is_jumping = True
                self.hovering = False
                sfx.play_sfx("jump", cooldown_ms=120)
            else:
                # 공중 호버
                self.velocity_y = -6.0
                self.hovering = True

        if self.is_jumping:
            if self.hovering and hover_held and self.velocity_y >= 0:
                # 호버 낙하 제한
                self.velocity_y = min(self.velocity_y + 0.08, 1.2)
            else:
                self.velocity_y += self.gravity
            previous_bottom = self.rect.bottom
            self.y_float += self.velocity_y
            self.rect.y = int(self.y_float)
        else:
            previous_bottom = self.rect.bottom

        landing_y = self._landing_floor(
            terrain_rects,
            floor_y,
            previous_bottom,
        )
        ground = landing_y - self.rect.height
        if self.rect.y >= ground:
            # 착지
            self.rect.y = ground
            self.y_float = float(ground)
            self.velocity_y = 0.0
            self.is_jumping = False
            self.hovering = False
        if self.rect.y < 10:
            self.rect.y = 10
            self.y_float = 10.0
            self.velocity_y = 0.0

    def _walkable_floor(self, terrain_rects, ground_y):
        # 걷는 바닥
        floors = []
        max_step_up = 26
        max_step_down = 34

        ground_delta = ground_y - self.rect.bottom
        if -max_step_up <= ground_delta <= max_step_down or self.rect.bottom >= ground_y:
            floors.append(ground_y)

        for rect in terrain_rects:
            if not self._overlaps_x(rect):
                continue
            delta = rect.top - self.rect.bottom
            if -max_step_up <= delta <= max_step_down:
                floors.append(rect.top)

        if not floors:
            return None
        return min(floors)

    def _landing_floor(self, terrain_rects, ground_y, previous_bottom):
        # 착지 바닥
        landing_y = ground_y
        if self.velocity_y < 0:
            return landing_y

        for rect in terrain_rects:
            if not self._overlaps_x(rect):
                continue
            if previous_bottom > rect.top + 8:
                continue
            if self.rect.bottom < rect.top:
                continue
            if rect.top < landing_y:
                landing_y = rect.top
        return landing_y

    def _overlaps_x(self, rect):
        # 발판 위인지
        foot_x = self.rect.centerx
        return rect.left + 3 <= foot_x <= rect.right - 3

    # 빔 그리기
    def draw_beams(self, surface, camera_x=0):
        # 빔 표시
        for beam in self._beams.values():
            beam.draw(surface, camera_x)

    def _draw_beam_energy(self, surface):
        # 빔 에너지
        if self.is_empty():
            return
        current = self.peek()
        if current not in BEAM_ELEMENTS or current not in self._beams:
            return
        beam = self._beams[current]
        color = ELEMENTS[current]["color"]
        bar_w, bar_h = 180, 8
        bx, by = 10, 42
        pg.draw.rect(surface, (40, 40, 40), (bx - 1, by - 1, bar_w + 2, bar_h + 2))
        filled = int(bar_w * beam.energy_ratio)
        if filled > 0:
            pg.draw.rect(surface, color, (bx, by, filled, bar_h))
        pg.draw.rect(surface, (200, 200, 200), (bx, by, bar_w, bar_h), 1)

    # 그리기
    def draw(self, surface, camera_x=0):
        # 커비 표시
        if self.invulnerable and (pg.time.get_ticks() // 80) % 2:
            # 무적 깜빡임
            return
        image_rect = self.image.get_rect(
            midbottom=(self.rect.centerx - round(camera_x), self.rect.bottom),
        )
        image = self.image
        if pg.time.get_ticks() < self.hit_flash_until:
            image = image.copy()
            image.fill((255, 70, 70, 120), special_flags=pg.BLEND_RGBA_ADD)
        surface.blit(image, image_rect)
        # 입에 문 속성
        if (
            self.held_element is not None
            and not self.spit_animation.active
            and not self._in_attack()
        ):
            color = ELEMENTS[self.held_element]["color"]
            bx = self.rect.right + 4 if self.facing_right else self.rect.left - 4
            bx -= round(camera_x)
            radius = 13 if (pg.time.get_ticks() // 150) % 2 == 0 else 10
            pg.draw.circle(surface, color, (bx, self.rect.centery), radius)
            pg.draw.circle(
                surface,
                (255, 255, 255),
                (bx, self.rect.centery),
                radius,
                2,
            )

    def draw_inhale_effect(self, surface, camera_x=0):
        # 흡입 효과
        if not self.inhaling:
            return
        mouth_x = self.rect.right if self.facing_right else self.rect.left
        mouth_y = self.rect.centery
        direction = 1 if self.facing_right else -1
        phase = (pg.time.get_ticks() // 60) % 5
        y_offsets = (-20, -10, 0, 10, 20)

        for index in range(5):
            step = (index + phase) % 5 + 1
            distance = step * 30
            x = mouth_x - camera_x + direction * distance
            y = mouth_y + y_offsets[index]
            radius = 9 - step
            blue = 140 + step * 20
            pg.draw.circle(surface, (30, 140, blue), (int(x), y), radius)

    def draw_UI(self, surface):
        # 커비 UI
        font = self.font

        if self.held_element is not None:
            # 뱉기 안내
            el = ELEMENTS[self.held_element]
            guide = font.render(
                f"[{el['label']} 입에 문 중]  X: 뱉기   ↓: 삼키기   SPACE: 점프",
                True,
                el["color"],
            )
        else:
            guide = font.render(
                "Z:흡입  X:뱉기  D연타:펀치 3단  F연타:킥 3단  V:빔  SPACE:점프",
                True,
                (80, 80, 80),
            )
        surface.blit(guide, (10, SCREEN_HEIGHT - 30))

        attack = self._current_attack()
        if attack is not None:
            # 콤보 안내
            buffered = (
                f"  NEXT x{self.attack_buffer_count}"
                if self.attack_buffer_count
                else ""
            )
            combo = font.render(
                f"{attack['name']}  {self.attack_stage + 1}/3{buffered}",
                True,
                (190, 40, 40),
            )
            surface.blit(combo, (10, 40))

        if not self.ability_stack:
            return
        # 능력 스택
        surface.blit(
            font.render("능력 스택 (오른쪽=현재):", True, (40, 40, 40)), (10, 10)
        )
        for i, element in enumerate(self.ability_stack):
            el = ELEMENTS[element]
            is_active = i == len(self.ability_stack) - 1
            cx, cy = 220 + i * 50, 18
            r = 17 if is_active else 12
            pg.draw.circle(surface, el["color"], (cx, cy), r)
            if is_active:
                pg.draw.circle(surface, (255, 255, 255), (cx, cy), r, 2)
            lbl = font.render(el["label"], True, (255, 255, 255))
            surface.blit(lbl, lbl.get_rect(center=(cx, cy)))
        self._draw_beam_energy(surface)
