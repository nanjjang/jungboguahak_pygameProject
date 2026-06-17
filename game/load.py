"""이미지와 폰트처럼 여러 파일에서 함께 쓰는 리소스를 불러오는 도우미."""

from pathlib import Path

import pygame

# load.py는 game 폴더 안에 있으므로, 여기서 src/assets/images까지의 경로를 만든다.
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
        # 설치된 폰트 중 이름이 일치하는 것이 있으면 그 폰트를 사용한다.
        if pygame.font.match_font(name):
            return pygame.font.SysFont(name, size)
    # 한글 폰트를 못 찾으면 pygame 기본 폰트로라도 게임이 멈추지 않게 한다.
    return pygame.font.Font(None, size)


def load_image(name):
    """assets/images 폴더에서 이미지 파일 하나를 읽어 pygame Surface로 반환한다."""
    return pygame.image.load(IMAGE_ROOT / name)
