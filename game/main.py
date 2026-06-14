import pygame as pg
import sys

from src.constants import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, WHITE, GRAY, KEYS
from src.koreanize import KOREAN_TO_KEY
from src.kirby import Kirby
from src.enemy import create_enemy
from src.projectile import Projectile


def make_enemies(ground_y):
    spawn = [
        ('fire',     300, 0),
        ('fire',     500, 0),
        ('electric', 450, 0),
        ('water',    550, 90),   # 새라서 공중에 (fly_offset=90)
        ('earth',    650, 0),
    ]
    enemies = []
    for element, x, fly_offset in spawn:
        e = create_enemy(element, x, 0)
        e.rect.bottom = ground_y - fly_offset
        e.start_x     = e.rect.x
        enemies.append(e)
    return enemies


def main():
    pg.init()
    screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pg.display.set_caption("지연쌤팬클럽")
    clock = pg.time.Clock()

    ground_y    = SCREEN_HEIGHT - 50
    player      = Kirby(x=100, y=600)
    enemies     = make_enemies(ground_y)
    projectiles = pg.sprite.Group()

    running = True
    while running:
        clock.tick(FPS)

        jump_pressed = spit_pressed = attack_pressed = gulp_pressed = False
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
            if event.type == pg.KEYDOWN:
                key_const = KOREAN_TO_KEY.get(event.unicode, event.key)
                if key_const == KEYS['jump']:   jump_pressed   = True
                if key_const == KEYS['spit']:   spit_pressed   = True
                if key_const == KEYS['attack']: attack_pressed = True
                if key_const == KEYS['gulp']:   gulp_pressed   = True

        key = pg.key.get_pressed()
        player.update(key, jump_pressed, spit_pressed, attack_pressed, enemies, gulp_pressed)

        for proj_data in player.pending_projectiles:
            projectiles.add(Projectile(**proj_data))
        player.pending_projectiles.clear()

        for enemy in enemies:
            enemy.update(kirby_rect=player.rect)

        projectiles.update()

        # 발사체가 적에 닿으면 적 제거
        for proj in list(projectiles):
            for enemy in list(enemies):
                if proj.rect.colliderect(enemy.rect) and not enemy.being_inhaled:
                    enemies.remove(enemy)
                    proj.kill()
                    break

        # Draw
        screen.fill(WHITE)
        pg.draw.line(screen, GRAY, (0, ground_y), (SCREEN_WIDTH, ground_y), 2)
        for enemy in enemies:
            enemy.draw(screen)
        player.draw_inhale_effect(screen)
        player.draw(screen)
        projectiles.draw(screen)
        player.draw_hud(screen, key)

        pg.display.flip()

    pg.quit()
    sys.exit()


if __name__ == "__main__":
    main()
