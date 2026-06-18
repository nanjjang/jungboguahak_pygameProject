"""플레이어 캐릭터 Kirby의 이동, 공격, 흡입, 능력, 애니메이션을 담당한다."""

import pygame as pg
import load

from src.constants import ELEMENTS, SCREEN_WIDTH, SCREEN_HEIGHT
from src.beam_effect import BEAM_ELEMENTS, BeamEffect, FireBeam

_BODY_SIZE = (26, 26)
_SPRITE_SIZE = (42, 36)


def _sprite(name, authored_left=False, canvas_size=_SPRITE_SIZE, angle=0):
    """픽셀아트 비율을 유지한 채 한 장의 스프라이트를 공통 캔버스에 올린다."""
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


def _c7(i):
    """왼쪽을 보고 있는 07 컬렉션 프레임을 오른쪽 기준으로 뒤집어 불러온다."""
    return _sprite(f"07_kirby_collection/frame_{i:03d}.png", authored_left=True)


def _basic_frames(*indices):
    """기본 Kirby 프레임 여러 장을 한 번에 불러온다."""
    frames = []
    for index in indices:
        frames.append(_sprite(f"03_basic_kirby/frame_{index:03d}.png"))
    return frames


def _water_shot_frame(index):
    """넓은 물 발사 프레임에서 Kirby 몸통 위치가 충돌 박스와 맞도록 정렬한다."""
    image = load.load_image(f"07_kirby_collection/frame_{index:03d}.png")
    canvas = pg.Surface((70, 42), pg.SRCALPHA)
    body_center_x = 10 if index != 258 else image.get_width() // 2
    x = canvas.get_width() // 2 - body_center_x
    canvas.blit(image, (x, canvas.get_height() - image.get_height()))
    return canvas


class _FrameAnimation:
    """프레임 넘김 계산을 Kirby 상태 코드 밖으로 분리한다."""

    def __init__(self, frames=None, frame_interval_ms=80, loop=True):
        self.frames = frames or []
        self.frame_interval_ms = frame_interval_ms
        self.loop = loop
        self.frame_index = 0
        self.last_update = pg.time.get_ticks()
        self.active = bool(self.frames)

    def start(self, frames=None, frame_interval_ms=None):
        """첫 프레임부터 애니메이션을 시작한다."""
        if frames is not None:
            self.frames = frames
        if frame_interval_ms is not None:
            self.frame_interval_ms = frame_interval_ms
        self.frame_index = 0
        self.last_update = pg.time.get_ticks()
        self.active = bool(self.frames)

    def stop(self):
        """원샷 애니메이션을 비활성화한다."""
        self.active = False

    def restart(self):
        """현재 프레임 목록을 처음부터 다시 준비한다."""
        self.start()

    def use_frames(self, frames):
        """프레임 목록이 바뀌면 첫 프레임부터 다시 재생한다."""
        if self.frames is not frames:
            self.start(frames=frames)

    @property
    def current_frame(self):
        """현재 표시할 프레임을 반환한다."""
        if not self.frames or not self.active:
            return None
        return self.frames[self.frame_index]

    def advance(self):
        """시간이 충분히 지났으면 다음 프레임으로 이동한다."""
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
        """필요하면 한 칸 넘긴 뒤 현재 프레임을 반환한다."""
        self.advance()
        return self.current_frame


class Kirby(pg.sprite.Sprite):
    """사용자가 조작하는 플레이어 캐릭터."""

    def __init__(self, x, y):
        pg.sprite.Sprite.__init__(self)
        self._load_frames()
        self._init_state(x, y)

    # ---------------------------------------------------------------- stack
    def is_empty(self):
        """능력 스택이 비어 있으면 True이다."""
        return not self.ability_stack

    def push(self, element):
        """새 능력을 스택 맨 위에 올린다."""
        self.ability_stack.append(element)

    def pop(self):
        """현재 사용 중인 능력을 스택에서 꺼낸다."""
        if self.is_empty():
            return "스택이 비어있음"
        return self.ability_stack.pop()

    def pop_same_ability(self, element):
        """이미 있는 같은 능력을 제거해 중복 저장을 막는다."""
        if self.is_empty():
            return "스택이 비어있음"
        return self.ability_stack.remove(element)

    def peek(self):
        """현재 사용할 능력, 즉 스택 맨 위 능력을 확인한다."""
        if self.is_empty():
            return "스택이 비어있음"
        return self.ability_stack[-1]

    # ---------------------------------------------------------------- load
    def _load_frames(self):
        """Kirby의 모든 상태별 애니메이션 프레임을 미리 불러온다."""
        # Keep normal movement and melee in the same basic Kirby sprite set.
        self.idle_frames = _basic_frames(1)
        self.move_frames = _basic_frames(*range(15, 23))
        self.jump_up = _basic_frames(33)[0]
        self.jump_down = _basic_frames(23)[0]
        self.hover_frame = _sprite(
            "KSSU_Kirby_Hover_sprite.png",
        )

        # Inhale, full-mouth movement, and spit/recovery.
        self.inhale_frames = []
        for index in range(98, 104):
            self.inhale_frames.append(_c7(index))

        self.held_idle = _c7(111)
        self.held_frames = []
        for index in range(112, 128):
            self.held_frames.append(_c7(index))

        self.held_jump_up = _c7(118)
        self.held_jump_down = _c7(119)
        self.spit_frames = []
        for index in (107, 104, 108, 109):
            self.spit_frames.append(_c7(index))

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
            # 일부 능력은 장착 중 Kirby의 기본 모습 자체가 달라진다.
            "water": {
                "idle": _sprite("07_kirby_collection/frame_337.png"),
                "move": water_move_frames,
                "jump_up": _sprite("07_kirby_collection/frame_351.png"),
                "jump_down": _sprite("07_kirby_collection/frame_357.png"),
            },
        }
        self.ability_frames = {
            # 빔 사용 중 입 모양/자세 애니메이션이다.
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

        # Same-key follow-ups form independent three-stage punch/kick combos.
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

    # ---------------------------------------------------------------- init
    def _init_state(self, x, y):
        """게임 시작 또는 Kirby 생성 시 필요한 모든 상태값을 초기화한다."""
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

        # 입력 엣지 감지
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

        # 뱉기 애니메이션 (원샷)
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

    # ---------------------------------------------------------------- update
    def update(
        self,
        controls,
        enemies=None,
        *,
        spit_pressed=False,
        gulp_pressed=False,
        punch_pressed=False,
        kick_pressed=False,
    ):
        """한 프레임 동안 Kirby 입력, 이동, 공격, 애니메이션을 모두 갱신한다."""
        # 흡입: 입에 문 상태이거나 공격 중이면 불가
        self.inhaling = (
            controls.inhale_held
            and self.held_element is None
            and not self._in_attack()
        )

        self.jump_held = controls.jump_held
        self.hover_held = self.jump_held and controls.hover_modifier_held

        # D / F 키 엣지 감지 (근접 공격)
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
        # 단발 입력은 update 바깥에서 FrameInput으로 감지해 여기서 행동으로 바꾼다.
        if spit_pressed and not self._in_attack():
            self._on_spit()
        if gulp_pressed:
            self._on_gulp()
        self._update_beams(controls.beam_held, controls)
        moving = self._move(controls)
        self._apply_gravity(self.jump_held, self.hover_held)
        self._update_image(moving)

    # ---------------------------------------------------------------- helpers
    def _in_attack(self):
        """현재 펀치/킥 콤보 중이면 True이다."""
        return self.attack_kind is not None

    def _current_attack(self):
        """현재 콤보 단계 설정 딕셔너리를 반환한다."""
        if not self._in_attack():
            return None
        return self.attack_combos[self.attack_kind][self.attack_stage]

    # ---------------------------------------------------------------- inhale
    def _get_inhale_rect(self):
        """Kirby 앞쪽에 흡입 판정 사각형을 만든다."""
        x = self.rect.right if self.facing_right else self.rect.left - self.inhale_range
        return pg.Rect(x, self.rect.centery - 35, self.inhale_range, 70)

    def _handle_inhale(self, enemies):
        """흡입 범위 안의 적을 끌어오고, Kirby와 닿으면 입에 문 상태로 만든다."""
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
                # 적과 Kirby가 겹치면 해당 적의 속성을 입에 문다.
                self.held_element = enemy.element
                self.inhaling = False
                self.held_animation.restart()
                enemies.remove(enemy)

    # ---------------------------------------------------------------- actions
    def _on_spit(self):
        """X키: 입에 문 → 별 뱉기 / 능력 있음 → 능력 잃고 별 뱉기."""
        if self.held_element is not None:
            self.held_element = None
        elif not self.is_empty():
            self.pop()
        self.spit_animation.start()
        self._shoot("star")

    def _on_gulp(self):
        """입에 문 속성을 삼켜 능력 스택에 추가한다."""
        if self.held_element is not None:
            self._push_ability(self.held_element)
            self.held_element = None

    def _on_attack(self, kind):
        """펀치/킥 입력을 현재 콤보 상태에 맞춰 시작하거나 예약한다."""
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
        """지정한 종류와 단계의 근접 공격 애니메이션을 시작한다."""
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
        self._apply_attack_motion()

    def _finish_attack(self):
        """현재 공격을 끝내고, 짧은 시간 안에 다음 콤보로 이어갈 수 있게 준비한다."""
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

    # ---------------------------------------------------------------- beam
    def _get_beam(self, element):
        """속성에 맞는 빔 객체를 가져오고, 없으면 새로 만든다."""
        if element not in self._beams:
            self._beams[element] = (
                FireBeam() if element == "fire" else BeamEffect(element)
            )
        return self._beams[element]

    def _get_fire_direction(self, controls):
        """불 능력은 방향키 상태에 따라 수평/수직/대각선 빔을 선택한다."""
        if controls.up_held:
            return "vertical"
        if controls.down_held and self.is_jumping:
            return "diagonal"
        return "horizontal"

    def _update_beams(self, attack_held, controls=None):
        """능력 빔의 활성화, 비활성화, 위치, 에너지 상태를 갱신한다."""
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
                else:
                    beam.deactivate()

        for element, beam in self._beams.items():
            # 빔은 Kirby 입 위치를 기준으로 매 프레임 새 위치를 받는다.
            direction = beam.direction
            mouth_x, mouth_y = self._beam_mouth_position(direction)
            if element == "fire":
                beam.update(mouth_x, mouth_y, self.facing_right, kirby_rect=self.rect)
            else:
                beam.update(mouth_x, mouth_y, self.facing_right)

        if self.beam_hit_cooldown_frames > 0:
            self.beam_hit_cooldown_frames -= 1

    def _active_beam_state(self):
        """현재 켜져 있는 빔이 있으면 애니메이션에 필요한 상태를 반환한다."""
        if self.is_empty() or self.held_element is not None:
            return None
        current = self.peek()
        beam = self._beams.get(current)
        if current not in self.ability_frames or beam is None or not beam.active:
            return None
        return current, beam.direction

    def _equipped_form(self):
        """장착만 해도 모습이 달라지는 능력이 현재 능력인지 확인한다."""
        if self.is_empty() or self.held_element is not None:
            return None
        current = self.peek()
        return current if current in self.element_forms else None

    def _beam_mouth_position(self, direction):
        """빔 방향별로 Kirby 입 위치 좌표를 계산한다."""
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
        """현재 활성 빔의 히트박스. 없으면 None."""
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
        """현재 콤보 단계가 타격 프레임일 때만 근접 공격 히트박스를 반환한다."""
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
        """현재 근접 공격이 실제로 맞는 프레임이면 데미지를 반환한다."""
        attack = self._current_attack()
        if (
            attack is None
            or self.attack_animation.frame_index not in attack["hit_frames"]
        ):
            return 0
        return attack["damage"]

    @property
    def beam_damage(self):
        """현재 장착 능력의 빔 데미지를 반환한다."""
        if self.is_empty():
            return 0
        return {
            "fire": 10,
            "water": 7,
            "electric": 9,
            "earth": 12,
        }.get(self.peek(), 0)

    # ---------------------------------------------------------------- ability
    def _push_ability(self, element):
        """같은 능력은 중복으로 쌓지 않고 맨 위로 올린다."""
        if element in self.ability_stack:
            self.pop_same_ability(element)
        self.push(element)

    def _shoot(self, element):
        """Projectile 생성을 위한 정보를 pending_projectiles에 임시 저장한다."""
        x = self.rect.right if self.facing_right else self.rect.left
        self.pending_projectiles.append(
            {
                "x": x,
                "y": self.rect.centery,
                "facing_right": self.facing_right,
                "element": element,
            }
        )

    # ---------------------------------------------------------------- health
    @property
    def invulnerable(self):
        """현재 무적 시간이 남아 있으면 True이다."""
        return pg.time.get_ticks() < self.invulnerable_until

    def set_spawn_point(self, x, y):
        """죽거나 다음 스테이지로 갈 때 돌아올 시작 위치를 정한다."""
        self.spawn_point = (x, y)

    def set_world_bounds(self, width):
        """현재 스테이지 가로 길이에 맞춰 Kirby 이동 범위를 정한다."""
        self.world_width = max(SCREEN_WIDTH, int(width))
        self.rect.x = min(self.rect.x, self.world_width - self.rect.width)

    def reset_position(self):
        """Kirby를 스폰 위치로 되돌리고 이동/공격 상태를 초기화한다."""
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

    def take_damage(self, amount, source_x=None):
        """플레이어가 피해를 입었을 때 체력, 목숨, 무적 시간을 처리한다."""
        if self.game_over or self.invulnerable:
            return 0
        dealt = min(self.hp, max(1, round(amount)))
        self.hp -= dealt
        now = pg.time.get_ticks()
        self.hit_flash_until = now + 180
        self.invulnerable_until = now + 900

        if source_x is not None:
            # 맞은 위치 반대 방향으로 살짝 밀려나는 넉백을 준다.
            direction = 1 if self.rect.centerx >= source_x else -1
            self.rect.x = max(
                0,
                min(self.world_width - self.rect.width, self.rect.x + direction * 24),
            )
        self.velocity_y = -4.2
        self.is_jumping = True

        if self.hp <= 0:
            # 체력이 0이 되면 목숨을 줄이고, 남은 목숨이 있으면 재배치한다.
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
        return dealt

    # ---------------------------------------------------------------- animation frames
    def _get_inhale_frame(self):
        """흡입 중 입 모양 애니메이션 프레임을 반환한다."""
        return self.inhale_animation.frame()

    def _get_held_frame(self, moving):
        """적을 입에 문 상태의 대기/이동 애니메이션 프레임을 고른다."""
        if not moving:
            self.held_animation.restart()
            return self.held_idle
        return self.held_animation.frame()

    def _get_ability_frame(self, element, direction):
        """능력 빔을 쓰는 동안 속성/방향별 자세 프레임을 고른다."""
        frame_sets = self.ability_frames[element]
        direction = direction if direction in frame_sets else "horizontal"
        frame_key = (element, direction)
        frames = frame_sets[direction]

        if self.ability_frame_key != frame_key:
            self.ability_frame_key = frame_key
            self.ability_animation.start(frames=frames)

        return self.ability_animation.frame()

    def _advance_attack_frame(self):
        """근접 공격 프레임을 진행하고, 예약된 콤보가 있으면 다음 단계로 넘어간다."""
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
            # 공격 중 같은 키를 누르면 다음 콤보 단계가 예약된다.
            kind = self.attack_kind
            self._start_attack(
                kind,
                self.attack_stage + 1,
                buffer_count=self.attack_buffer_count - 1,
            )
        else:
            self._finish_attack()

    def _apply_attack_motion(self):
        """공격 프레임별 전진 값을 적용해 타격감 있는 이동을 만든다."""
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

    # ---------------------------------------------------------------- movement
    def _move(self, controls):
        """좌우 이동 입력을 적용하고, 실제로 움직였는지 반환한다."""
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
        """현재 상태 우선순위에 따라 Kirby가 보여줄 최종 이미지를 고른다."""
        spit_frame = self.spit_animation.frame()
        self._advance_attack_frame()

        attack = self._current_attack()
        if attack is not None:
            # 공격 중에는 공격 프레임이 가장 우선이다.
            frame = self.attack_animation.current_frame
        elif spit_frame is not None:
            frame = spit_frame
        elif self.inhaling:
            frame = self._get_inhale_frame()
        elif self.held_element is not None:
            # 입에 문 상태에서는 일반 점프/이동과 다른 프레임을 사용한다.
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
                # 빔이 활성화되어 있으면 능력 사용 자세를 보여준다.
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
            # 흡입을 멈추면 다음 흡입 때 처음 프레임부터 시작한다.
            self.inhale_animation.restart()
        if self._active_beam_state() is None:
            self.ability_animation.stop()
            self.ability_frame_key = None
        self.image = (
            frame if self.facing_right else pg.transform.flip(frame, True, False)
        )

    def _get_walk_frame(self, moving, frames=None):
        """이동 중이면 걷기 프레임을 넘기고, 멈춰 있으면 idle 프레임을 반환한다."""
        frames = self.move_frames if frames is None else frames
        if not moving:
            self.walk_animation.restart()
            return self.idle_frames[0]
        self.walk_animation.use_frames(frames)
        return self.walk_animation.frame()

    # ---------------------------------------------------------------- gravity
    def _apply_gravity(self, jump_held, hover_held=False):
        """점프, 공중 재점프, 호버, 낙하, 바닥 충돌을 처리한다."""
        just_pressed = jump_held and not self._prev_jump_held
        self._prev_jump_held = jump_held

        if just_pressed:
            if not self.is_jumping:
                # 바닥에서 점프를 처음 누르면 위쪽 속도를 준다.
                self.velocity_y = -10.0
                self.is_jumping = True
                self.hovering = False
            else:
                # 공중에서 다시 점프를 누르면 호버 상태로 들어간다.
                self.velocity_y = -6.0
                self.hovering = True

        if self.is_jumping:
            if self.hovering and hover_held and self.velocity_y >= 0:
                # 호버 중에는 낙하 속도를 작게 제한한다.
                self.velocity_y = min(self.velocity_y + 0.08, 1.2)
            else:
                self.velocity_y += self.gravity
            self.y_float += self.velocity_y
            self.rect.y = int(self.y_float)

        ground = SCREEN_HEIGHT - 50 - self.rect.height
        if self.rect.y >= ground:
            # 바닥에 닿으면 점프 관련 상태를 모두 정리한다.
            self.rect.y = ground
            self.y_float = float(ground)
            self.velocity_y = 0.0
            self.is_jumping = False
            self.hovering = False
        if self.rect.y < 10:
            self.rect.y = 10
            self.y_float = 10.0
            self.velocity_y = 0.0

    # ---------------------------------------------------------------- beam draw
    def draw_beams(self, surface, camera_x=0):
        """활성화된 모든 빔과 현재 빔 에너지바를 그린다."""
        for beam in self._beams.values():
            beam.draw(surface, camera_x)
        self._draw_beam_energy(surface, camera_x)

    def _draw_beam_energy(self, surface, camera_x=0):
        """현재 능력 빔의 남은 에너지를 Kirby 아래쪽에 작은 바로 표시한다."""
        if self.is_empty():
            return
        current = self.peek()
        if current not in BEAM_ELEMENTS or current not in self._beams:
            return
        beam = self._beams[current]
        color = ELEMENTS[current]["color"]
        bar_w, bar_h = 60, 8
        bx = self.rect.centerx - round(camera_x) - bar_w // 2
        by = self.rect.bottom + 5
        pg.draw.rect(surface, (40, 40, 40), (bx - 1, by - 1, bar_w + 2, bar_h + 2))
        filled = int(bar_w * beam.energy_ratio)
        if filled > 0:
            pg.draw.rect(surface, color, (bx, by, filled, bar_h))
        pg.draw.rect(surface, (200, 200, 200), (bx, by, bar_w, bar_h), 1)

    # ---------------------------------------------------------------- draw
    def draw(self, surface, camera_x=0):
        """Kirby 본체와 입에 문 속성 표시를 그린다."""
        if self.invulnerable and (pg.time.get_ticks() // 80) % 2:
            # 무적 중에는 깜빡이게 해서 피격 후 상태를 보여준다.
            return
        image_rect = self.image.get_rect(
            midbottom=(self.rect.centerx - round(camera_x), self.rect.bottom),
        )
        image = self.image
        if pg.time.get_ticks() < self.hit_flash_until:
            image = image.copy()
            image.fill((255, 70, 70, 120), special_flags=pg.BLEND_RGBA_ADD)
        surface.blit(image, image_rect)
        # 입에 문 원소 표시 (뱉기/공격 중에는 숨김)
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
        """흡입 중 Kirby 앞쪽에 빨려 들어가는 원형 효과를 그린다."""
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

    def draw_hud(self, surface):
        """능력 스택, 조작 안내, 현재 콤보 상태를 화면에 표시한다."""
        font = self.font

        if self.held_element is not None:
            # 입에 문 속성이 있을 때는 뱉기/삼키기 안내를 우선 보여준다.
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
            # 근접 공격 중이면 현재 콤보 이름과 예약된 다음 입력 수를 표시한다.
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
        # 능력 스택은 오른쪽 원이 현재 사용 능력이다.
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
