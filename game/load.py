import os, pygame

# 한글 지원 폰트 우선순위 (macOS → Windows → Linux 순)
_KOREAN_FONT_CANDIDATES = ["applegothic", "malgun gothic", "nanumgothic", "gulim", "dotum"]

def get_korean_font(size):
    """시스템에서 한글 폰트를 찾아 반환. 없으면 기본 폰트 사용."""
    for name in _KOREAN_FONT_CANDIDATES:
        if pygame.font.match_font(name):   # 실제 존재 여부 확인
            return pygame.font.SysFont(name, size)
    return pygame.font.Font(None, size)    # 한글 깨질 수 있음

def load_image(name):
    path = os.path.join('src','assets','images',name)
    image = pygame.image.load(path)
    return image

def load_scene(name):
    path = os.path.join('..','data','scenery',name)
    scenery = pygame.image.load(path)
    return scenery

def load_font(name,size):
    path = os.path.join('..','data','fonts',name)
    font = pygame.font.Font(path,size)
    return font

def load_sound(name):
    path = os.path.join('..','data','sounds',name)
    sound = pygame.mixer.Sound(path)
    return sound

def load_music(name):
    path = os.path.join('..','data','music',name)
    music = pygame.mixer.Sound(path)
    return music