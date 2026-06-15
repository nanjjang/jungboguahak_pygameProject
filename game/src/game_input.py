from dataclasses import dataclass

import pygame as pg

from src.constants import KEYS
from src.koreanize import KOREAN_TO_KEY


@dataclass
class FrameInput:
    quit_requested: bool = False
    spit_pressed: bool = False
    gulp_pressed: bool = False
    punch_pressed: bool = False
    kick_pressed: bool = False
    enter_pressed: bool = False
    restart_requested: bool = False


def read_frame_input():
    actions = FrameInput()
    for event in pg.event.get():
        if event.type == pg.QUIT:
            actions.quit_requested = True
            continue
        if event.type != pg.KEYDOWN:
            continue

        key_const = KOREAN_TO_KEY.get(event.unicode, event.key)
        if key_const == KEYS["spit"]:
            actions.spit_pressed = True
        if key_const == KEYS["gulp"]:
            actions.gulp_pressed = True
        if key_const == pg.K_d:
            actions.punch_pressed = True
        if key_const == pg.K_f:
            actions.kick_pressed = True
        if key_const == pg.K_UP:
            actions.enter_pressed = True
        if key_const == pg.K_r:
            actions.restart_requested = True
    return actions
