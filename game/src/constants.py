import pygame as pg

SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 600
FPS = 60

# 속성별 데이터 단일 출처 — 색/라벨/발사체/적 설정 모두 여기서
ELEMENTS = {
    "fire": {
        "color": (255, 80, 0),
        "label": "불",
        "proj_speed": 10,
        "proj_size": 22,
        "proj_dy": 0.0,
        "proj_gravity": 0.0,
        "damage": 24,
    },
    "electric": {
        "color": (255, 220, 0),
        "label": "전기",
        "proj_speed": 18,
        "proj_size": 18,
        "proj_dy": 0.0,
        "proj_gravity": 0.0,
        "damage": 20,
    },
    "water": {
        "color": (0, 150, 255),
        "label": "물",
        "proj_speed": 8,
        "proj_size": 20,
        "proj_dy": -1.5,
        "proj_gravity": 0.2,
        "damage": 18,
    },
    "earth": {
        "color": (139, 90, 43),
        "label": "땅",
        "proj_speed": 6,
        "proj_size": 24,
        "proj_dy": 0.0,
        "proj_gravity": 0.2,
        "damage": 28,
    },
    "star": {
        "color": (255, 220, 50),
        "label": "★",
        "proj_speed": 12,
        "proj_size": 18,
        "proj_dy": 0.0,
        "proj_gravity": 0.0,
        "damage": 35,
    },
}

# 난이도별 AI 반응성, 능력치, 생성 수 조절
DIFFICULTY_SETTINGS = {
    "easy": {
        "label": "EASY",
        "speed_mult": 0.78,
        "hp_mult": 0.82,
        "damage_mult": 0.72,
        "detect_mult": 0.75,
        "cooldown_mult": 1.35,
        "reaction_ms": 780,
        "aim_error": 34,
        "spawn_bonus": -1,
        "max_active_enemies": 1,
    },
    "normal": {
        "label": "NORMAL",
        "speed_mult": 1.0,
        "hp_mult": 1.0,
        "damage_mult": 1.0,
        "detect_mult": 1.0,
        "cooldown_mult": 1.0,
        "reaction_ms": 460,
        "aim_error": 18,
        "spawn_bonus": 0,
        "max_active_enemies": 1,
    },
    "hard": {
        "label": "HARD",
        "speed_mult": 1.28,
        "hp_mult": 1.3,
        "damage_mult": 1.38,
        "detect_mult": 1.35,
        "cooldown_mult": 0.7,
        "reaction_ms": 240,
        "aim_error": 5,
        "spawn_bonus": 1,
        "max_active_enemies": 2,
    },
}

# 적 종류별 스프라이트·AI·전투 설정
ENEMY_DATA = {
    "fire": {
        "frames": [f"flame{i}.png" for i in range(1, 13)],
        "ai": "chaser",
        "speed": 1.6,
        "patrol": 100,
        "hp": 42,
        "contact_damage": 12,
        "attack_damage": 16,
        "detect_x": 165,
        "detect_y": 100,
        "cooldown": 1100,
    },
    "electric": {
        "frames": [f"waddleDoo{i}.png" for i in range(1, 8)],
        "ai": "shooter",
        "speed": 1.5,
        "patrol": 150,
        "hp": 52,
        "contact_damage": 10,
        "attack_damage": 18,
        "detect_x": 215,
        "detect_y": 110,
        "cooldown": 1450,
    },
    "water": {
        "frames": [f"bird{i}.png" for i in range(1, 6)],
        "ai": "swooper",
        "speed": 2.3,
        "patrol": 200,
        "hp": 36,
        "contact_damage": 11,
        "attack_damage": 15,
        "detect_x": 190,
        "detect_y": 180,
        "cooldown": 1250,
    },
    "earth": {
        "frames": [f"pikey{i}.png" for i in range(1, 3)],
        "ai": "charger",
        "speed": 1.2,
        "patrol": 80,
        "hp": 68,
        "contact_damage": 14,
        "attack_damage": 22,
        "detect_x": 175,
        "detect_y": 95,
        "cooldown": 1750,
    },
}

# 키 바인딩 단일 출처 — 여기만 바꾸면 전체 반영
KEYS = {
    "jump": pg.K_SPACE,
    "inhale": pg.K_z,
    "spit": pg.K_x,
    "attack": pg.K_v,
    "gulp": pg.K_DOWN,
}
