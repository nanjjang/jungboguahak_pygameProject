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

KEY_SCANCODES = {
    "jump": pg.KSCAN_SPACE,
    "inhale": pg.KSCAN_Z,
    "spit": pg.KSCAN_X,
    "attack": pg.KSCAN_V,
    "gulp": pg.KSCAN_DOWN,
    "settings": pg.KSCAN_ESCAPE,
    "quit_title": pg.KSCAN_Q,
    "restart": pg.KSCAN_R,
    "punch": pg.KSCAN_D,
    "kick": pg.KSCAN_F,
    "stage_enter": pg.KSCAN_UP,
}

# 저의 처절한 하드코딩 시도를 기억해주세요 ㅜㅜ
# KOREAN_TO_KEY = {
#     "ㄱ": pg.K_r,
#     "ㄴ": pg.K_s,
#     "ㄷ": pg.K_e,
#     "ㄹ": pg.K_f,
#     "ㅁ": pg.K_a,
#     "ㅂ": pg.K_q,
#     "ㅅ": pg.K_t,
#     "ㅇ": pg.K_d,
#     "ㅈ": pg.K_w,
#     "ㅊ": pg.K_c,
#     "ㅋ": pg.K_z,
#     "ㅌ": pg.K_x,
#     "ㅍ": pg.K_v,
#     "ㅎ": pg.K_g,
#     "ㅏ": pg.K_k,
#     "ㅐ": pg.K_o,
#     "ㅑ": pg.K_i,
#     "ㅓ": pg.K_j,
#     "ㅔ": pg.K_p,
#     "ㅕ": pg.K_u,
#     "ㅗ": pg.K_h,
#     "ㅛ": pg.K_y,
#     "ㅜ": pg.K_n,
#     "ㅠ": pg.K_b,
#     "ㅡ": pg.K_m,
#     "ㅣ": pg.K_l,
# }

NAV_UP_KEYS = (pg.K_UP,)
NAV_DOWN_KEYS = (pg.K_DOWN,)
NAV_LEFT_KEYS = (pg.K_LEFT,)
NAV_RIGHT_KEYS = (pg.K_RIGHT,)
CONFIRM_KEYS = (pg.K_RETURN, pg.K_KP_ENTER, pg.K_SPACE)
HOVER_KEYS = (pg.K_LSHIFT,)

NAV_UP_SCANCODES = (pg.KSCAN_UP,)
NAV_DOWN_SCANCODES = (pg.KSCAN_DOWN,)
NAV_LEFT_SCANCODES = (pg.KSCAN_LEFT,)
NAV_RIGHT_SCANCODES = (pg.KSCAN_RIGHT,)
HOVER_SCANCODES = (pg.KSCAN_LSHIFT,)

SCANCODE_TO_KEY = {
    pg.KSCAN_UP: pg.K_UP,
    pg.KSCAN_DOWN: pg.K_DOWN,
    pg.KSCAN_LEFT: pg.K_LEFT,
    pg.KSCAN_RIGHT: pg.K_RIGHT,
    pg.KSCAN_RETURN: pg.K_RETURN,
    pg.KSCAN_KP_ENTER: pg.K_KP_ENTER,
    pg.KSCAN_SPACE: pg.K_SPACE,
    pg.KSCAN_LSHIFT: pg.K_LSHIFT,
    pg.KSCAN_ESCAPE: pg.K_ESCAPE,
    pg.KSCAN_Q: pg.K_q,
    pg.KSCAN_R: pg.K_r,
    pg.KSCAN_Z: pg.K_z,
    pg.KSCAN_X: pg.K_x,
    pg.KSCAN_V: pg.K_v,
    pg.KSCAN_D: pg.K_d,
    pg.KSCAN_F: pg.K_f,
}

_HELD_KEYS = set()
_HELD_SCANCODES = set()


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
            _clear_held_keys()
            continue
        if event.type == pg.WINDOWFOCUSLOST:
            _clear_held_keys()
            continue
        if event.type == pg.KEYUP:
            _forget_held_key(event, _normalized_key(event))
            continue
        if event.type == pg.KEYDOWN:
            key_const = _normalized_key(event)
            _remember_held_key(event, key_const)
            _check_pressed_key(actions, key_const)
            continue

    held = pg.key.get_pressed()
    actions.up_held = _held_any(held, NAV_UP_KEYS, NAV_UP_SCANCODES)
    actions.down_held = _held_any(held, NAV_DOWN_KEYS, NAV_DOWN_SCANCODES)
    actions.left_held = _held_any(held, NAV_LEFT_KEYS, NAV_LEFT_SCANCODES)
    actions.right_held = _held_any(held, NAV_RIGHT_KEYS, NAV_RIGHT_SCANCODES)
    actions.jump_held = _held_action(held, "jump")
    actions.hover_modifier_held = _held_any(held, HOVER_KEYS, HOVER_SCANCODES)
    actions.inhale_held = _held_action(held, "inhale")
    actions.beam_held = _held_action(held, "attack")
    actions.punch_held = _held_action(held, "punch")
    actions.kick_held = _held_action(held, "kick")
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
    scancode = getattr(event, "scancode", None)
    if scancode in SCANCODE_TO_KEY:
        return SCANCODE_TO_KEY[scancode]
    return event.key


def _remember_held_key(event, normalized_key):
    _HELD_KEYS.add(normalized_key)
    if hasattr(event, "key"):
        _HELD_KEYS.add(event.key)
    scancode = getattr(event, "scancode", None)
    if scancode is not None and scancode != pg.KSCAN_UNKNOWN:
        _HELD_SCANCODES.add(scancode)


def _forget_held_key(event, normalized_key):
    _HELD_KEYS.discard(normalized_key)
    if hasattr(event, "key"):
        _HELD_KEYS.discard(event.key)
    scancode = getattr(event, "scancode", None)
    if scancode is not None:
        _HELD_SCANCODES.discard(scancode)


def _clear_held_keys():
    _HELD_KEYS.clear()
    _HELD_SCANCODES.clear()


def _held_action(held, action):
    return _held_any(held, (KEY_BINDINGS[action],), (KEY_SCANCODES[action],))


def _held_any(held, keys, scancodes=()):
    """여러 키 후보 중 하나라도 눌려 있으면 True를 반환한다."""
    for key in keys:
        if key in _HELD_KEYS or _pressed_key(held, key):
            return True
    for scancode in scancodes:
        if scancode in _HELD_SCANCODES:
            return True
    return False


def _pressed_key(held, key):
    try:
        return bool(held[key])
    except (IndexError, KeyError):
        return False
