import pygame as pg

SCREEN_WIDTH  = 800
SCREEN_HEIGHT = 600
FPS = 60

WHITE = (255, 255, 255)
BLUE  = (0, 102, 204)
GRAY  = (200, 200, 200)

# 속성별 데이터 단일 출처 — 색/라벨/발사체/적 설정 모두 여기서
ELEMENTS = {
    'fire':     {'color': (255,  80,   0), 'label': '불',
                 'proj_speed': 10, 'proj_size': 22, 'proj_dy': 0.0,  'proj_gravity': 0.0},
    'electric': {'color': (255, 220,   0), 'label': '전기',
                 'proj_speed': 18, 'proj_size': 18, 'proj_dy': 0.0,  'proj_gravity': 0.0},
    'water':    {'color': (  0, 150, 255), 'label': '물',
                 'proj_speed':  8, 'proj_size': 20, 'proj_dy': -1.5, 'proj_gravity': 0.2},
    'earth':    {'color': (139,  90,  43), 'label': '땅',
                 'proj_speed':  6, 'proj_size': 24, 'proj_dy': 0.0,  'proj_gravity': 0.2},
    'star':     {'color': (255, 220,  50), 'label': '★',
                 'proj_speed': 12, 'proj_size': 18, 'proj_dy': 0.0,  'proj_gravity': 0.0},
}

# 적 종류별 스프라이트·이동 설정
ENEMY_DATA = {
    'fire':     {'frames': [f'flame{i}.png'      for i in range(1, 13)], 'speed': 1, 'patrol': 100},
    'electric': {'frames': [f'waddleDoo{i}.png'  for i in range(1, 8)],  'speed': 2, 'patrol': 150},
    'water':    {'frames': [f'bird{i}.png'        for i in range(1, 6)],  'speed': 3, 'patrol': 200},
    'earth':    {'frames': [f'pikey{i}.png'       for i in range(1, 3)],  'speed': 1, 'patrol':  80},
}

# 키 바인딩 단일 출처 — 여기만 바꾸면 전체 반영
KEYS = {
    'jump':   pg.K_SPACE,
    'inhale': pg.K_z,
    'spit':   pg.K_x,
    'attack': pg.K_c,
}
