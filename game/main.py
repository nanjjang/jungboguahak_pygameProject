import pygame
import sys

from src.constants import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, WHITE, GRAY
from components.player import Player


def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("파이게임 점프 & 중력 예제")
    clock = pygame.time.Clock()

    player = Player(x=100, y=400, size=50)

    running = True
    while running:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        player.move()
        player.update_physics()

        screen.fill(WHITE)
        pygame.draw.line(screen, GRAY, (0, SCREEN_HEIGHT - 50), (SCREEN_WIDTH, SCREEN_HEIGHT - 50), 5)
        player.draw(screen)

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
