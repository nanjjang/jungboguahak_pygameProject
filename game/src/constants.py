# 공통 설정

# 화면 기본값
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 600
FPS = 60

# 속성 설정
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

# 난이도 설정
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


def make_frame_names(prefix, start, end):
    frames = []
    for index in range(start, end + 1):
        frames.append(f"{prefix}{index}.png")
    return frames


# 적 설정
ENEMY_DATA = {
    "fire": {
        "frames": make_frame_names("flame", 1, 12),
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
        "frames": make_frame_names("waddleDoo", 1, 7),
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
        "frames": make_frame_names("bird", 1, 5),
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
        "frames": make_frame_names("pikey", 1, 2),
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
