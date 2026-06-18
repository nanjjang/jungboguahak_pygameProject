"""스테이지 클리어 때 다음 스테이지로 넘어갈때 딜레이 주는 파일"""

from functools import lru_cache

import pygame as pg

import load


FRAME_MS = 55
# 엔딩 프레임 이미지는 assets/images/ending 폴더에서 순서대로 읽는다.
_FRAME_DIR = load.IMAGE_ROOT / "ending"
_FRAME_PATTERN = "kirby_frame_*.jpg"


@lru_cache(maxsize=1)
def _frame_names():
    names = []
    for path in sorted(_FRAME_DIR.glob(_FRAME_PATTERN)):
        names.append(path.name)
    return names


def animation_duration_ms():
    return max(1, len(_frame_names())) * FRAME_MS