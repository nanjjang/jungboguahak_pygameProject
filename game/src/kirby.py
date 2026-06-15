import pygame as pg
import math
import load

from src.constants import ELEMENTS, KEYS, SCREEN_WIDTH, SCREEN_HEIGHT
from src.beam_effect import BEAM_ELEMENTS, BeamEffect, FireBeam

_BODY_SIZE = (26, 26)
_SPRITE_SIZE = (42, 36)


def _sprite(name, authored_left=False, canvas_size=_SPRITE_SIZE, angle=0):
    """Load one sprite without stretching its pixel-art proportions."""
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
    canvas.blit(image, image.get_rect(midbottom=(canvas.get_width() // 2, canvas.get_height())))
    return canvas


def _c7(i):
    """07 collection frames are authored facing left; normalize to right."""
    return _sprite(f"07_kirby_collection/frame_{i:03d}.png", authored_left=True)


def _basic_frames(*indices):
    return [
        _sprite(f"03_basic_kirby/frame_{i:03d}.png")
        for i in indices
    ]


def _water_shot_frame(index):
    """Align the body in the wide water-shot frames to Kirby's collision body."""
    image = load.load_image(f"07_kirby_collection/frame_{index:03d}.png")
    canvas = pg.Surface((70, 42), pg.SRCALPHA)
    body_center_x = 10 if index != 258 else image.get_width() // 2
    x = canvas.get_width() // 2 - body_center_x
    canvas.blit(image, (x, canvas.get_height() - image.get_height()))
    return canvas


class Kirby(pg.sprite.Sprite):
    def __init__(self, x, y):
        pg.sprite.Sprite.__init__(self)
        self._load_frames()
        self._init_state(x, y)

    # ---------------------------------------------------------------- stack
    def is_empty(self):        return len(self.ability_stack) <= 0
    def push(self, element):   self.ability_stack.append(element)
    def pop(self):
        if self.is_empty(): return '스택이 비어있음'
        return self.ability_stack.pop()
    def pop_same_ability(self, element):
        if self.is_empty(): return '스택이 비어있음'
        return self.ability_stack.remove(element)
    def peek(self):
        if self.is_empty(): return '스택이 비어있음'
        return self.ability_stack[len(self.ability_stack) - 1]

    # ---------------------------------------------------------------- load
    def _load_frames(self):
        # Keep normal movement and melee in the same basic Kirby sprite set.
        self.idle_frames = _basic_frames(1)
        self.move_frames = _basic_frames(*range(15, 23))
        self.jump_up = _basic_frames(33)[0]
        self.jump_down = _basic_frames(23)[0]
        self.hover_frame = _basic_frames(11)[0]

        # Inhale, full-mouth movement, and spit/recovery.
        self.inhale_frames = [_c7(i) for i in range(98, 104)]
        self.held_idle = _c7(111)
        self.held_frames = [_c7(i) for i in range(112, 128)]
        self.held_jump_up = _c7(118)
        self.held_jump_down = _c7(119)
        self.spit_frames = [_c7(i) for i in (107, 104, 108, 109)]
        breath_horizontal = _basic_frames(3, 49, 49, 3)
        self.element_forms = {
            'water': {
                'idle': _sprite("07_kirby_collection/frame_337.png"),
                'move': [
                    _sprite(f"07_kirby_collection/frame_{i:03d}.png")
                    for i in range(331, 347)
                ],
                'jump_up': _sprite("07_kirby_collection/frame_351.png"),
                'jump_down': _sprite("07_kirby_collection/frame_357.png"),
            },
        }
        self.ability_frames = {
            'fire': {
                'horizontal': breath_horizontal,
                'vertical': [
                    _sprite(
                        f"03_basic_kirby/frame_{i:03d}.png",
                        canvas_size=(46, 46),
                        angle=32,
                    )
                    for i in (3, 49, 49, 3)
                ],
                'diagonal': [
                    _sprite(
                        f"03_basic_kirby/frame_{i:03d}.png",
                        canvas_size=(44, 40),
                        angle=-18,
                    )
                    for i in (3, 49, 49, 3)
                ],
            },
            'water': {
                'horizontal': [
                    _water_shot_frame(i)
                    for i in (258, 254, 255, 256, 257, 256, 255, 254)
                ],
            },
            'electric': {
                'horizontal': [
                    _sprite(
                        f"07_kirby_collection/frame_{i:03d}.png",
                        canvas_size=(42, 52),
                    )
                    for i in range(202, 214)
                ],
            },
            'earth': {'horizontal': breath_horizontal},
        }

        # Same-key follow-ups form independent three-stage punch/kick combos.
        self.attack_combos = {
            'punch': [
                {
                    'name': '잽',
                    'frames': _basic_frames(1, 64, 68, 66, 1),
                    'frame_ms': 36,
                    'hit_frames': frozenset((2, 3)),
                    'hitbox': (28, 2, 22),
                    'motion': {2: 1},
                },
                {
                    'name': '크로스',
                    'frames': _basic_frames(1, 69, 72, 76, 77, 1),
                    'frame_ms': 38,
                    'hit_frames': frozenset((2, 3, 4)),
                    'hitbox': (34, 0, 25),
                    'motion': {2: 2, 3: 1},
                },
                {
                    'name': '브레이크 피니시',
                    'frames': _basic_frames(1, 55, 58, 68, 76, 77, 1),
                    'frame_ms': 40,
                    'hit_frames': frozenset((3, 4, 5)),
                    'hitbox': (40, -4, 32),
                    'motion': {2: 2, 3: 3, 4: 2},
                },
            ],
            'kick': [
                {
                    'name': '단발 킥',
                    'frames': _basic_frames(1, 100, 101, 104, 1),
                    'frame_ms': 42,
                    'hit_frames': frozenset((1, 2, 3)),
                    'hitbox': (32, -8, 34),
                    'motion': {1: 1, 2: 1},
                },
                {
                    'name': '에어리얼 체인',
                    'frames': _basic_frames(1, 90, 91, 94, 96, 99, 1),
                    'frame_ms': 40,
                    'hit_frames': frozenset((1, 3, 4, 5)),
                    'hitbox': (38, -8, 38),
                    'motion': {2: 2, 3: 2, 4: 2},
                },
                {
                    'name': '소머솔트 피니시',
                    'frames': _basic_frames(1, 94, 96, 100, 101, 104, 1),
                    'frame_ms': 42,
                    'hit_frames': frozenset((1, 2, 4, 5, 6)),
                    'hitbox': (42, -12, 40),
                    'motion': {2: 2, 3: 2, 4: 3, 5: 2},
                },
            ],
        }

    # ---------------------------------------------------------------- init
    def _init_state(self, x, y):
        self.image = self.idle_frames[0]
        self.rect = pg.Rect(x, y, *_BODY_SIZE)
        self.y_float = float(y)

        # 이동
        self.speed       = 5
        self.velocity_y  = 0.0
        self.gravity     = 0.6
        self.is_jumping  = False
        self.air_jumps   = 0
        self.facing_right = True
        self.frame_w     = 0
        self.anim_timer  = 0
        self.anim_speed  = 80     # ms / walk frame

        # 입력 엣지 감지
        self._prev_jump_held = False
        self._prev_d_held    = False
        self._prev_f_held    = False

        # 흡입 / 호버
        self.inhaling    = False
        self.inhale_anim_idx = 0
        self.inhale_anim_t = pg.time.get_ticks()
        self.inhale_anim_ms = 75
        self.hovering    = False
        self.jump_held   = False
        self.hover_held  = False
        self.inhale_range = 180

        # 물기 / 능력
        self.held_element:  str | None   = None
        self.ability_stack: list[str]    = []
        self.held_anim_idx  = 0
        self.held_anim_t    = 0
        self.held_anim_ms   = 85
        self.ability_anim_idx = 0
        self.ability_anim_t = 0
        self.ability_anim_ms = 70
        self.ability_anim_key = None

        # 뱉기 애니메이션 (원샷)
        self.spit_anim_idx  = -1
        self.spit_anim_t    = 0
        self.spit_anim_ms   = 60

        # 근접 콤보
        self.attack_kind: str | None = None
        self.attack_stage = -1
        self.attack_frame_idx = -1
        self.attack_frame_t = 0
        self.attack_queue_count = 0
        self.attack_chain_kind = None
        self.attack_chain_stage = 0
        self.attack_chain_until = 0
        self.attack_chain_ms = 220

        # 기타
        self.pending_projectiles: list[dict]       = []
        self._beams:              dict[str, BeamEffect] = {}
        self.beam_kill_cd = 0
        self.font = load.get_korean_font(18)

    # ---------------------------------------------------------------- update
    def update(self, key, jump_pressed=False, spit_pressed=False,
               attack_pressed=False, enemies=None, gulp_pressed=False,
               punch_pressed=False, kick_pressed=False):
        # 흡입: 입에 문 상태이거나 공격 중이면 불가
        self.inhaling = (bool(key[KEYS['inhale']])
                         and self.held_element is None
                         and not self._in_attack())

        self.jump_held  = bool(key[KEYS['jump']])
        shift           = bool(key[pg.K_LSHIFT] or key[pg.K_RSHIFT])
        self.hover_held = self.jump_held and shift

        # D / F 키 엣지 감지 (근접 공격)
        d_held = bool(key[pg.K_d])
        f_held = bool(key[pg.K_f])
        just_punch = punch_pressed or (d_held and not self._prev_d_held)
        just_kick  = kick_pressed or (f_held and not self._prev_f_held)
        self._prev_d_held = d_held
        self._prev_f_held = f_held

        can_attack = (self.held_element is None
                      and self.spit_anim_idx < 0
                      and not self.inhaling)
        if just_punch and can_attack: self._on_attack('punch')
        if just_kick  and can_attack: self._on_attack('kick')

        self._handle_inhale(enemies)
        if spit_pressed and not self._in_attack(): self._on_spit()
        if gulp_pressed: self._on_gulp()
        self._update_beams(bool(key[KEYS['attack']]), key)
        moving = self._move(key)
        self._apply_gravity(self.jump_held, self.hover_held)
        self._update_image(moving)

    # ---------------------------------------------------------------- helpers
    def _in_attack(self):
        return self.attack_kind is not None

    def _current_attack(self):
        if not self._in_attack():
            return None
        return self.attack_combos[self.attack_kind][self.attack_stage]

    # ---------------------------------------------------------------- inhale
    def _get_inhale_rect(self):
        x = self.rect.right if self.facing_right else self.rect.left - self.inhale_range
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
                self.held_element  = enemy.element
                self.inhaling      = False
                self.held_anim_idx = 0
                self.held_anim_t   = pg.time.get_ticks()
                enemies.remove(enemy)

    # ---------------------------------------------------------------- actions
    def _on_spit(self):
        """X키: 입에 문 → 별 뱉기 / 능력 있음 → 능력 잃고 별 뱉기."""
        if self.held_element is not None:
            self.held_element = None
        elif not self.is_empty():
            self.pop()
        self.spit_anim_idx = 0
        self.spit_anim_t   = pg.time.get_ticks()
        self._shoot('star')

    def _on_gulp(self):
        if self.held_element is not None:
            self._push_ability(self.held_element)
            self.held_element = None

    def _on_attack(self, kind):
        if not self._in_attack():
            now = pg.time.get_ticks()
            stage = (
                self.attack_chain_stage
                if kind == self.attack_chain_kind and now <= self.attack_chain_until
                else 0
            )
            self._start_attack(kind, stage)
            return
        if self.attack_kind != kind:
            return
        remaining_stages = len(self.attack_combos[kind]) - self.attack_stage - 1
        if self.attack_queue_count < remaining_stages:
            self.attack_queue_count += 1

    def _start_attack(self, kind, stage, queue_count=0):
        self.attack_kind = kind
        self.attack_stage = stage
        self.attack_frame_idx = 0
        self.attack_frame_t = pg.time.get_ticks()
        self.attack_queue_count = queue_count
        self.attack_chain_kind = None
        self.attack_chain_stage = 0
        self.attack_chain_until = 0
        self._apply_attack_motion(0)

    def _finish_attack(self):
        kind = self.attack_kind
        next_stage = self.attack_stage + 1
        self.attack_kind = None
        self.attack_stage = -1
        self.attack_frame_idx = -1
        self.attack_queue_count = 0
        if kind is not None and next_stage < len(self.attack_combos[kind]):
            self.attack_chain_kind = kind
            self.attack_chain_stage = next_stage
            self.attack_chain_until = pg.time.get_ticks() + self.attack_chain_ms
        else:
            self.attack_chain_kind = None
            self.attack_chain_stage = 0
            self.attack_chain_until = 0

    # ---------------------------------------------------------------- beam
    def _get_beam(self, element):
        if element not in self._beams:
            self._beams[element] = FireBeam() if element == 'fire' else BeamEffect(element)
        return self._beams[element]

    def _get_fire_direction(self, key):
        if key[pg.K_UP]:    return 'vertical'
        if key[pg.K_DOWN] and self.is_jumping: return 'diagonal'
        return 'horizontal'

    def _update_beams(self, attack_held, key=None):
        if self.is_empty() or self.held_element is not None or self._in_attack():
            for beam in self._beams.values():
                beam.deactivate()
        else:
            current = self.peek()
            if current in BEAM_ELEMENTS:
                beam = self._get_beam(current)
                if attack_held:
                    if current == 'fire' and key is not None:
                        beam.try_activate(self._get_fire_direction(key))
                    else:
                        beam.try_activate()
                else:
                    beam.deactivate()

        for el, beam in self._beams.items():
            direction = getattr(beam, 'direction', 'horizontal')
            mouth_x, mouth_y = self._beam_mouth_position(direction)
            if el == 'fire':
                beam.update(mouth_x, mouth_y, self.facing_right, kirby_rect=self.rect)
            else:
                beam.update(mouth_x, mouth_y, self.facing_right)

        if self.beam_kill_cd > 0:
            self.beam_kill_cd -= 1

    def _active_beam_state(self):
        if self.is_empty() or self.held_element is not None:
            return None
        current = self.peek()
        beam = self._beams.get(current)
        if current not in self.ability_frames or beam is None or not beam.active:
            return None
        return current, getattr(beam, 'direction', 'horizontal')

    def _equipped_form(self):
        if self.is_empty() or self.held_element is not None:
            return None
        current = self.peek()
        return current if current in self.element_forms else None

    def _beam_mouth_position(self, direction):
        if direction == 'vertical':
            x_offset = 6 if self.facing_right else -6
            return self.rect.centerx + x_offset, self.rect.top - 10
        if direction == 'diagonal':
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
        kr = self.rect
        fr = self.facing_right
        direction = getattr(beam, 'direction', 'horizontal')
        mouth_x, mouth_y = self._beam_mouth_position(direction)
        if direction == 'vertical':
            return pg.Rect(mouth_x - 20, mouth_y - 80, 40, 80)
        if direction == 'diagonal':
            x = mouth_x if fr else mouth_x - 72
            return pg.Rect(x, mouth_y, 72, 52)
        x = mouth_x if fr else mouth_x - 84
        return pg.Rect(x, mouth_y - 24, 84, 48)

    @property
    def melee_hit_rect(self):
        """Current combo stage hitbox, active only on impact frames."""
        attack = self._current_attack()
        if attack is None or self.attack_frame_idx not in attack['hit_frames']:
            return None

        kr = self.rect
        reach, top_offset, height = attack['hitbox']
        x = kr.right - 4 if self.facing_right else kr.left - reach + 4
        return pg.Rect(x, kr.top + top_offset, reach, height)

    # ---------------------------------------------------------------- ability
    def _push_ability(self, element):
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

    # ---------------------------------------------------------------- animation ticks
    def _tick_inhale_anim(self):
        now = pg.time.get_ticks()
        if now - self.inhale_anim_t >= self.inhale_anim_ms:
            self.inhale_anim_t = now
            self.inhale_anim_idx = (self.inhale_anim_idx + 1) % len(self.inhale_frames)
        return self.inhale_frames[self.inhale_anim_idx]

    def _tick_held_anim(self, moving):
        if not moving:
            return self.held_idle
        now = pg.time.get_ticks()
        if now - self.held_anim_t >= self.held_anim_ms:
            self.held_anim_t   = now
            self.held_anim_idx = (self.held_anim_idx + 1) % len(self.held_frames)
        return self.held_frames[self.held_anim_idx]

    def _tick_ability_anim(self, element, direction):
        frame_sets = self.ability_frames[element]
        direction = direction if direction in frame_sets else 'horizontal'
        anim_key = (element, direction)
        if self.ability_anim_key != anim_key:
            self.ability_anim_key = anim_key
            self.ability_anim_idx = 0
            self.ability_anim_t = pg.time.get_ticks()

        frames = frame_sets[direction]
        now = pg.time.get_ticks()
        if now - self.ability_anim_t >= self.ability_anim_ms:
            self.ability_anim_t = now
            self.ability_anim_idx = (self.ability_anim_idx + 1) % len(frames)
        return frames[self.ability_anim_idx]

    def _tick_spit_anim(self):
        if self.spit_anim_idx < 0:
            return
        now = pg.time.get_ticks()
        if now - self.spit_anim_t >= self.spit_anim_ms:
            self.spit_anim_t    = now
            self.spit_anim_idx += 1
            if self.spit_anim_idx >= len(self.spit_frames):
                self.spit_anim_idx = -1

    def _tick_attack_anim(self):
        attack = self._current_attack()
        if attack is None:
            return

        now = pg.time.get_ticks()
        if now - self.attack_frame_t < attack['frame_ms']:
            return

        self.attack_frame_t = now
        self.attack_frame_idx += 1
        if self.attack_frame_idx < len(attack['frames']):
            self._apply_attack_motion(self.attack_frame_idx)
            return

        if (self.attack_queue_count > 0
                and self.attack_stage < len(self.attack_combos[self.attack_kind]) - 1):
            kind = self.attack_kind
            self._start_attack(
                kind,
                self.attack_stage + 1,
                queue_count=self.attack_queue_count - 1,
            )
        else:
            self._finish_attack()

    def _apply_attack_motion(self, frame_idx):
        attack = self._current_attack()
        if attack is None:
            return
        distance = attack['motion'].get(frame_idx, 0)
        if distance == 0:
            return
        direction = 1 if self.facing_right else -1
        self.rect.x = max(
            0,
            min(SCREEN_WIDTH - self.rect.width, self.rect.x + distance * direction),
        )

    # ---------------------------------------------------------------- movement
    def _move(self, key):
        if self._in_attack():
            return False

        moving = False
        if key[pg.K_LEFT]:
            self.rect.x = max(0, self.rect.x - self.speed)
            self.facing_right = False
            moving = True
        if key[pg.K_RIGHT]:
            self.rect.x = min(SCREEN_WIDTH - self.rect.width, self.rect.x + self.speed)
            self.facing_right = True
            moving = True
        return moving

    def _update_image(self, moving):
        self._tick_spit_anim()
        self._tick_attack_anim()

        attack = self._current_attack()
        if attack is not None:
            frame = attack['frames'][self.attack_frame_idx]
        elif self.spit_anim_idx >= 0:
            frame = self.spit_frames[self.spit_anim_idx]
        elif self.inhaling:
            frame = self._tick_inhale_anim()
        elif self.held_element is not None:
            if self.is_jumping:
                frame = self.held_jump_up if self.velocity_y < 0 else self.held_jump_down
            else:
                frame = self._tick_held_anim(moving)
        elif (ability_state := self._active_beam_state()) is not None:
            frame = self._tick_ability_anim(*ability_state)
        elif (form_element := self._equipped_form()) is not None:
            form = self.element_forms[form_element]
            if self.is_jumping:
                frame = form['jump_up'] if self.velocity_y < 0 else form['jump_down']
            elif moving:
                frame = self._anim_frame(moving, form['move'])
            else:
                frame = form['idle']
        elif self.hovering and self.hover_held:
            frame = self.hover_frame
        elif not self.is_jumping:
            frame = self._anim_frame(moving)
        else:
            frame = self.jump_up if self.velocity_y < 0 else self.jump_down

        if not self.inhaling:
            self.inhale_anim_idx = 0
            self.inhale_anim_t = pg.time.get_ticks()
        if self._active_beam_state() is None:
            self.ability_anim_idx = 0
            self.ability_anim_t = pg.time.get_ticks()
            self.ability_anim_key = None
        self.image = frame if self.facing_right else pg.transform.flip(frame, True, False)

    def _anim_frame(self, moving, frames=None):
        frames = self.move_frames if frames is None else frames
        if not moving:
            return self.idle_frames[0]
        now = pg.time.get_ticks()
        if now - self.anim_timer >= self.anim_speed:
            self.anim_timer = now
            self.frame_w = (self.frame_w + 1) % len(frames)
        return frames[self.frame_w % len(frames)]

    # ---------------------------------------------------------------- gravity
    def _apply_gravity(self, jump_held, hover_held=False):
        just_pressed         = jump_held and not self._prev_jump_held
        self._prev_jump_held = jump_held

        if just_pressed:
            if not self.is_jumping:
                self.velocity_y = -10.0
                self.is_jumping = True
                self.hovering   = False
            else:
                self.velocity_y = -6.0
                self.air_jumps += 1
                self.hovering   = True

        if self.is_jumping:
            if self.hovering and hover_held and self.velocity_y >= 0:
                self.velocity_y = min(self.velocity_y + 0.08, 1.2)
            else:
                self.velocity_y += self.gravity
            self.y_float += self.velocity_y
            self.rect.y   = int(self.y_float)

        ground = SCREEN_HEIGHT - 50 - self.rect.height
        if self.rect.y >= ground:
            self.rect.y     = ground
            self.y_float    = float(ground)
            self.velocity_y = 0.0
            self.is_jumping = False
            self.air_jumps  = 0
            self.hovering   = False
        if self.rect.y < 10:
            self.rect.y     = 10
            self.y_float    = 10.0
            self.velocity_y = 0.0

    # ---------------------------------------------------------------- beam draw
    def draw_beams(self, surface):
        for beam in self._beams.values():
            beam.draw(surface)
        self._draw_beam_energy(surface)

    def _draw_beam_energy(self, surface):
        if self.is_empty():
            return
        current = self.peek()
        if current not in BEAM_ELEMENTS or current not in self._beams:
            return
        beam  = self._beams[current]
        color = ELEMENTS[current]['color']
        bar_w, bar_h = 60, 8
        bx = self.rect.centerx - bar_w // 2
        by = self.rect.bottom + 5
        pg.draw.rect(surface, (40, 40, 40),    (bx - 1, by - 1, bar_w + 2, bar_h + 2))
        filled = int(bar_w * beam.energy_ratio)
        if filled > 0:
            pg.draw.rect(surface, color, (bx, by, filled, bar_h))
        pg.draw.rect(surface, (200, 200, 200), (bx, by, bar_w, bar_h), 1)

    # ---------------------------------------------------------------- draw
    def draw(self, surface):
        image_rect = self.image.get_rect(midbottom=self.rect.midbottom)
        surface.blit(self.image, image_rect)
        # 입에 문 원소 표시 (뱉기/공격 중에는 숨김)
        if (self.held_element is not None
                and self.spit_anim_idx < 0
                and not self._in_attack()):
            color = ELEMENTS[self.held_element]['color']
            bx = self.rect.right + 4 if self.facing_right else self.rect.left - 4
            r  = 10 + int(3 * abs(math.sin(pg.time.get_ticks() / 150)))
            pg.draw.circle(surface, color,           (bx, self.rect.centery), r)
            pg.draw.circle(surface, (255, 255, 255), (bx, self.rect.centery), r, 2)

    def draw_inhale_effect(self, surface):
        if not self.inhaling:
            return
        now     = pg.time.get_ticks()
        mouth_x = self.rect.right if self.facing_right else self.rect.left
        mouth_y = self.rect.centery
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

        if key is not None:
            z_on  = key[KEYS['inhale']]
            color = (0, 180, 0) if z_on else (180, 0, 0)
            dbg   = font.render(
                f"Z키: {'ON' if z_on else 'OFF'}  inhaling: {self.inhaling}", True, color)
            surface.blit(dbg, (SCREEN_WIDTH - 220, 10))

        if self.held_element is not None:
            el    = ELEMENTS[self.held_element]
            guide = font.render(
                f"[{el['label']} 입에 문 중]  X: 뱉기   ↓: 삼키기   SPACE: 점프",
                True, el['color'])
        else:
            guide = font.render(
                "Z:흡입  X:뱉기  D연타:펀치 3단  F연타:킥 3단  V:빔  SPACE:점프",
                True, (80, 80, 80))
        surface.blit(guide, (10, SCREEN_HEIGHT - 30))

        attack = self._current_attack()
        if attack is not None:
            queued = (
                f"  NEXT x{self.attack_queue_count}"
                if self.attack_queue_count else ""
            )
            combo = font.render(
                f"{attack['name']}  {self.attack_stage + 1}/3{queued}",
                True, (190, 40, 40),
            )
            surface.blit(combo, (10, 40))

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
            lbl = font.render(el['label'], True, (255, 255, 255))
            surface.blit(lbl, lbl.get_rect(center=(cx, cy)))
