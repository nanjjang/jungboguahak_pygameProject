import os, pygame

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