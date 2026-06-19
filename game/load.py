# 이미지랑 폰트 불러오기

from pathlib import Path

import pygame


IMAGE_ROOT = Path(__file__).resolve().parent / "src" / "assets" / "images"


_KOREAN_FONT_CANDIDATES = (
    "applegothic",
    "malgun gothic",
    "nanumgothic",
    "gulim",
    "dotum",
)


def get_korean_font(size):
    # 한글 폰트 찾기
    for name in _KOREAN_FONT_CANDIDATES:
        # 있으면 그걸로
        if pygame.font.match_font(name):
            return pygame.font.SysFont(name, size)
    # 없으면 기본 폰트
    return pygame.font.Font(None, size)


def load_image(name):
    # 이미지 읽기
    return pygame.image.load(IMAGE_ROOT / name)
