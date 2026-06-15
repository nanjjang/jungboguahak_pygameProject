from pathlib import Path

import pygame

IMAGE_ROOT = Path(__file__).resolve().parent / "src" / "assets" / "images"

# 한글 지원 폰트 우선순위 (macOS → Windows → Linux 순)
_KOREAN_FONT_CANDIDATES = (
    "applegothic",
    "malgun gothic",
    "nanumgothic",
    "gulim",
    "dotum",
)


def get_korean_font(size):
    """시스템에서 한글 폰트를 찾아 반환. 없으면 기본 폰트 사용."""
    for name in _KOREAN_FONT_CANDIDATES:
        if pygame.font.match_font(name):
            return pygame.font.SysFont(name, size)
    return pygame.font.Font(None, size)


def load_image(name):
    return pygame.image.load(IMAGE_ROOT / name)
