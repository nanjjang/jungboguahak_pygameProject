from functools import lru_cache
from pathlib import Path

import pygame as pg


SOUNDS_ROOT = Path(__file__).resolve().parent / "assets" / "sounds"

MASTER_VOLUME = 0.78
MUSIC_VOLUME = 0.44

MUSIC = {
    "menu": "05_-_Menu.mp3",
    "stage": "playing.mp3",
    "boss": "kirby-gourmet-race.mp3",
    "stage_clear": "09_stagecomplete.mp3",
    "game_over": "59_gameover.mp3",
}

SFX = {
    "menu_move": ("punch.wav", 0.18),
    "menu_confirm": ("fallingdown.wav", 0.34),
    "jump": ("fallingdown.wav", 0.34),
    "inhale": ("inhaling1(countinueWithInhaling2).wav", 0.38),
    "spit": ("fallingdown.wav", 0.38),
    "copy": ("kirby-copy-ability.mp3", 0.72),
    "melee": ("punch.wav", 0.50),
    "beam": ("electronicbeam.wav", 0.30),
    "beam_fire": ("fireflame.wav", 0.32),
    "beam_water": ("waterFlame.wav", 0.32),
    "beam_earth": ("earthFlame.wav", 0.32),
    "enemy_hit": ("punch.wav", 0.36),
    "player_hit": ("kirby-scream.mp3", 0.68),
    "player_down": ("kirby-death-sound.mp3", 0.68),
    "quit": ("byebye.mp3", 0.32),
}

_enabled = True
_current_music = None
_last_played_at = {}
_loop_channels = {}


def init():
    global _enabled
    if pg.mixer.get_init():
        return True
    try:
        pg.mixer.init(frequency=48000, size=-16, channels=2, buffer=512)
        pg.mixer.set_num_channels(24)
        return True
    except pg.error:
        _enabled = False
        return False


def play_sfx(name, cooldown_ms=0):
    if not _enabled or not init() or name not in SFX:
        return

    now = pg.time.get_ticks()
    last_played = _last_played_at.get(name, -cooldown_ms)
    if cooldown_ms and now - last_played < cooldown_ms:
        return
    _last_played_at[name] = now

    sound = _load_sound(name)
    if sound is None:
        return
    _, volume = SFX[name]
    sound.set_volume(volume * MASTER_VOLUME)
    sound.play()


def wait_to_quit(name):
    # 종료음 기다리기
    if not _enabled or not init() or name not in SFX:
        return

    sound = _load_sound(name)
    if sound is None:
        return
    _, volume = SFX[name]
    sound.set_volume(volume * MASTER_VOLUME)
    channel = sound.play()
    if channel is None:
        return

    clock = pg.time.Clock()
    while channel.get_busy():
        pg.event.pump()
        clock.tick(60)


def loop(name):
    # 반복 재생
    if not _enabled or not init() or name not in SFX:
        return
    channel = _loop_channels.get(name)
    if channel is not None and channel.get_busy():
        return

    sound = _load_sound(name)
    if sound is None:
        return
    _, volume = SFX[name]
    sound.set_volume(volume * MASTER_VOLUME)
    channel = sound.play(loops=-1)
    if channel is not None:
        _loop_channels[name] = channel


def stop(name, fade_ms=70):
    # 소리 멈춤
    channel = _loop_channels.pop(name, None)
    if channel is None:
        return
    if fade_ms:
        channel.fadeout(fade_ms)
    else:
        channel.stop()


def stop_all(fade_ms=70):
    # 반복음 전부 멈춤
    channels = list(_loop_channels.values())
    _loop_channels.clear()

    for channel in channels:
        if fade_ms:
            channel.fadeout(fade_ms)
        else:
            channel.stop()


def play_bgm(name, loops=-1, fade_ms=450, restart=False):
    # 배경음 변경
    global _current_music
    if not _enabled or not init() or name not in MUSIC:
        return
    if not restart and _current_music == name:
        return

    path = SOUNDS_ROOT / MUSIC[name]
    if not path.exists():
        return
    try:
        pg.mixer.music.fadeout(120)
        pg.mixer.music.load(str(path))
        pg.mixer.music.set_volume(MUSIC_VOLUME)
        pg.mixer.music.play(loops=loops, fade_ms=fade_ms)
        _current_music = name
    except pg.error:
        _current_music = None


def sync_bgm(state):
    # 상태별 배경음
    if state.player.game_over:
        play_bgm("game_over", loops=0)
        return
    if state.stage.transitioning or state.stage.completed:
        play_bgm("stage_clear", loops=0)
        return
    if state.stage.is_boss_stage:
        play_bgm("boss")
        return
    play_bgm("stage")


def stop_music(fade_ms=250):
    # 배경음 멈춤
    global _current_music
    if not pg.mixer.get_init():
        return
    pg.mixer.music.fadeout(fade_ms)
    _current_music = None


@lru_cache(maxsize=None)
def _load_sound(name):
    filename, _ = SFX[name]
    path = SOUNDS_ROOT / filename
    if not path.exists():
        return None
    try:
        return pg.mixer.Sound(str(path))
    except pg.error:
        return None
