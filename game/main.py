import pygame as pg
import sys

from src.constants import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, WHITE, GRAY
from src.kirby import Kirby


def main():
    pg.init()
    screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pg.display.set_caption("지연쌤팬클럽")
    clock = pg.time.Clock()

    player = Kirby(x=100, y=400)

    running = True
    while running:
        clock.tick(FPS)

        jump_pressed = False
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
            if event.type == pg.KEYDOWN and event.key == pg.K_SPACE:
                jump_pressed = True

        key = pg.key.get_pressed()

        screen.fill(WHITE)
        pg.draw.line(screen, GRAY, (0, SCREEN_HEIGHT - 50), (SCREEN_WIDTH, SCREEN_HEIGHT - 50), 5)
        player.update(screen, key, jump_pressed)

        pg.display.flip()

    pg.quit()
    sys.exit()


if __name__ == "__main__":
    main()
