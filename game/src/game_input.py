"""키보드 입력을 게임에서 쓰기 쉬운 값으로 정리하는 파일."""

import pygame as pg

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

NAV_UP_KEYS = (pg.K_UP)
NAV_DOWN_KEYS = (pg.K_DOWN)
NAV_LEFT_KEYS = (pg.K_LEFT)
NAV_RIGHT_KEYS = (pg.K_RIGHT)
CONFIRM_KEYS = (pg.K_RETURN, pg.K_KP_ENTER, pg.K_SPACE)
HOVER_KEYS = (pg.K_LSHIFT)


class FrameInput:
    """한 프레임 동안의 입력 상태."""

    def __init__(self):
        self.quit_requested = False

        self.up_pressed = False
        self.down_pressed = False
        self.left_pressed = False
        self.right_pressed = False
        self.confirm_pressed = False
        self.settings_pressed = False
        self.title_quit_pressed = False
        self.restart_requested = False

        self.spit_pressed = False
        self.gulp_pressed = False
        self.punch_pressed = False
        self.kick_pressed = False
        self.enter_pressed = False

        self.up_held = False
        self.down_held = False
        self.left_held = False
        self.right_held = False
        self.jump_held = False
        self.hover_modifier_held = False
        self.inhale_held = False
        self.beam_held = False
        self.punch_held = False
        self.kick_held = False


def read_frame_input():
    """pygame 이벤트와 현재 키 상태를 읽어서 FrameInput으로 반환한다."""
    actions = FrameInput()
    for event in pg.event.get():
        if event.type == pg.QUIT:
            actions.quit_requested = True
            continue
        if event.type != pg.KEYDOWN:
            continue

        key_const = _normalized_key(event)
        _check_pressed_key(actions, key_const)

    held = pg.key.get_pressed()
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


def _check_pressed_key(actions, key):
    if key in NAV_UP_KEYS:
        actions.up_pressed = True
    if key in NAV_DOWN_KEYS:
        actions.down_pressed = True
    if key in NAV_LEFT_KEYS:
        actions.left_pressed = True
    if key in NAV_RIGHT_KEYS:
        actions.right_pressed = True
    if key in CONFIRM_KEYS:
        actions.confirm_pressed = True

    if key == KEY_BINDINGS["settings"]:
        actions.settings_pressed = True
    elif key == KEY_BINDINGS["quit_title"]:
        actions.title_quit_pressed = True
    elif key == KEY_BINDINGS["restart"]:
        actions.restart_requested = True
    elif key == KEY_BINDINGS["spit"]:
        actions.spit_pressed = True
    elif key == KEY_BINDINGS["gulp"]:
        actions.gulp_pressed = True
    elif key == KEY_BINDINGS["punch"]:
        actions.punch_pressed = True
    elif key == KEY_BINDINGS["kick"]:
        actions.kick_pressed = True
    elif key == KEY_BINDINGS["stage_enter"]:
        actions.enter_pressed = True


def _normalized_key(event):
    """한글 입력 상태에서도 같은 키가 눌린 것처럼 처리한다."""
    if hasattr(event, "unicode") and event.unicode in KOREAN_TO_KEY:
        return KOREAN_TO_KEY[event.unicode]
    return event.key


def _held_any(held, keys):
    """여러 키 후보 중 하나라도 눌려 있으면 True를 반환한다."""
    for key in keys:
        if held[key]:
            return True
    return False