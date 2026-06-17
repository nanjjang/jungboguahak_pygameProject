"""pygame 이벤트를 게임에서 쓰기 쉬운 입력 상태로 바꾸는 파일."""

from dataclasses import dataclass

import pygame as pg


# 게임 안에서 쓰는 행동 이름과 실제 키보드 키를 연결한다.
KEY_BINDINGS = {
    "jump": pg.K_SPACE,
    "inhale": pg.K_z,
    "spit": pg.K_x,
    "attack": pg.K_v,
    "gulp": pg.K_DOWN,
    "settings": pg.K_ESCAPE,
    "quit_title": pg.K_q,
    "restart": pg.K_r,
    "punch": pg.K_d,
    "kick": pg.K_f,
    "stage_enter": pg.K_UP,
}

KOREAN_TO_KEY = {
    "ㄱ": pg.K_r,
    "ㄴ": pg.K_s,
    "ㄷ": pg.K_e,
    "ㄹ": pg.K_f,
    "ㅁ": pg.K_a,
    "ㅂ": pg.K_q,
    "ㅅ": pg.K_t,
    "ㅇ": pg.K_d,
    "ㅈ": pg.K_w,
    "ㅊ": pg.K_c,
    "ㅋ": pg.K_z,
    "ㅌ": pg.K_x,
    "ㅍ": pg.K_v,
    "ㅎ": pg.K_g,
    "ㅏ": pg.K_k,
    "ㅐ": pg.K_o,
    "ㅑ": pg.K_i,
    "ㅓ": pg.K_j,
    "ㅔ": pg.K_p,
    "ㅕ": pg.K_u,
    "ㅗ": pg.K_h,
    "ㅛ": pg.K_y,
    "ㅜ": pg.K_n,
    "ㅠ": pg.K_b,
    "ㅡ": pg.K_m,
    "ㅣ": pg.K_l,
}

# 메뉴 이동과 게임 이동에서 같이 쓰는 방향키 묶음이다.
NAV_UP_KEYS = (pg.K_UP, pg.K_w)
NAV_DOWN_KEYS = (pg.K_DOWN, pg.K_s)
NAV_LEFT_KEYS = (pg.K_LEFT, pg.K_a)
NAV_RIGHT_KEYS = (pg.K_RIGHT, pg.K_d)
CONFIRM_KEYS = (pg.K_RETURN, pg.K_KP_ENTER, pg.K_SPACE)
HOVER_KEYS = (pg.K_LSHIFT, pg.K_RSHIFT)


@dataclass
class FrameInput:
    """한 프레임 동안 눌린 키와 계속 누르고 있는 키를 모아 둔 입력 결과."""

    # 창 닫기처럼 게임 전체 흐름을 끝내는 입력이다.
    quit_requested: bool = False

    # pressed는 이번 프레임에 한 번 눌린 입력이다.
    up_pressed: bool = False
    down_pressed: bool = False
    left_pressed: bool = False
    right_pressed: bool = False
    confirm_pressed: bool = False
    settings_pressed: bool = False
    title_quit_pressed: bool = False
    restart_requested: bool = False

    # 공격/상호작용처럼 한 번 누르는 순간이 중요한 입력이다.
    spit_pressed: bool = False
    gulp_pressed: bool = False
    punch_pressed: bool = False
    kick_pressed: bool = False
    enter_pressed: bool = False

    # held는 키를 누르고 있는 동안 매 프레임 True가 되는 입력이다.
    up_held: bool = False
    down_held: bool = False
    left_held: bool = False
    right_held: bool = False
    jump_held: bool = False
    hover_modifier_held: bool = False
    inhale_held: bool = False
    beam_held: bool = False
    punch_held: bool = False
    kick_held: bool = False


def read_frame_input():
    """pygame 이벤트 큐와 현재 키 상태를 읽어 FrameInput으로 반환한다."""
    actions = FrameInput()
    for event in pg.event.get():
        if event.type == pg.QUIT:
            actions.quit_requested = True
            continue
        if event.type != pg.KEYDOWN:
            continue

        key_const = _normalized_key(event)
        # KEYDOWN 이벤트는 "방금 눌렀다"는 의미의 pressed 입력으로 저장한다.
        actions.up_pressed |= key_const in NAV_UP_KEYS
        actions.down_pressed |= key_const in NAV_DOWN_KEYS
        actions.left_pressed |= key_const in NAV_LEFT_KEYS
        actions.right_pressed |= key_const in NAV_RIGHT_KEYS
        actions.confirm_pressed |= key_const in CONFIRM_KEYS
        actions.settings_pressed |= key_const == KEY_BINDINGS["settings"]
        actions.title_quit_pressed |= key_const == KEY_BINDINGS["quit_title"]
        actions.restart_requested |= key_const == KEY_BINDINGS["restart"]

        actions.spit_pressed |= key_const == KEY_BINDINGS["spit"]
        actions.gulp_pressed |= key_const == KEY_BINDINGS["gulp"]
        actions.punch_pressed |= key_const == KEY_BINDINGS["punch"]
        actions.kick_pressed |= key_const == KEY_BINDINGS["kick"]
        actions.enter_pressed |= key_const == KEY_BINDINGS["stage_enter"]

    held = pg.key.get_pressed()
    # get_pressed()는 현재 누르고 있는 키를 알려 주므로 이동/점프 유지에 쓴다.
    actions.up_held = _held_any(held, NAV_UP_KEYS)
    actions.down_held = _held_any(held, NAV_DOWN_KEYS)
    actions.left_held = _held_any(held, NAV_LEFT_KEYS)
    actions.right_held = _held_any(held, NAV_RIGHT_KEYS)
    actions.jump_held = bool(held[KEY_BINDINGS["jump"]])
    actions.hover_modifier_held = _held_any(held, HOVER_KEYS)
    actions.inhale_held = bool(held[KEY_BINDINGS["inhale"]])
    actions.beam_held = bool(held[KEY_BINDINGS["attack"]])
    actions.punch_held = bool(held[KEY_BINDINGS["punch"]])
    actions.kick_held = bool(held[KEY_BINDINGS["kick"]])
    return actions


def _normalized_key(event):
    """한글 입력 상태에서도 같은 키가 눌린 것처럼 처리한다."""
    return KOREAN_TO_KEY.get(getattr(event, "unicode", ""), event.key)


def _held_any(held, keys):
    """여러 키 후보 중 하나라도 눌려 있으면 True를 반환한다."""
    return any(held[key] for key in keys)
