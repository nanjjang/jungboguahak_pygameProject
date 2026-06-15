import pygame as pg

from src.constants import DIFFICULTY_SETTINGS, SCREEN_HEIGHT, SCREEN_WIDTH


def draw_status_hud(surface, state, font, large_font):
    player = state.player
    stage = state.stage
    x, y, width, height = 10, 67, 220, 18
    pg.draw.rect(surface, (42, 28, 36), (x - 2, y - 2, width + 4, height + 4))
    filled = round(width * player.hp / player.max_hp)
    if filled:
        pg.draw.rect(surface, (235, 65, 90), (x, y, filled, height))
    pg.draw.rect(surface, (255, 255, 255), (x, y, width, height), 2)
    hp_text = font.render(
        f"HP {player.hp}/{player.max_hp}    LIFE x{player.lives}",
        True,
        (255, 255, 255),
    )
    surface.blit(
        hp_text,
        hp_text.get_rect(center=(x + width // 2, y + height // 2)),
    )

    difficulty_label = DIFFICULTY_SETTINGS[state.difficulty]["label"]
    stage_text = font.render(
        f"STAGE {stage.label}   {difficulty_label}",
        True,
        (40, 40, 55),
    )
    surface.blit(
        stage_text,
        stage_text.get_rect(topright=(SCREEN_WIDTH - 12, 12)),
    )
    _draw_boss_hud(surface, state, font)
    _draw_stage_title(surface, stage, large_font)


def draw_end_overlay(surface, title, subtitle, large_font, font):
    shade = pg.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pg.SRCALPHA)
    shade.fill((15, 15, 25, 185))
    surface.blit(shade, (0, 0))
    main_text = large_font.render(title, True, (255, 225, 100))
    sub_text = font.render(subtitle, True, (255, 255, 255))
    surface.blit(
        main_text,
        main_text.get_rect(center=(SCREEN_WIDTH // 2, 250)),
    )
    surface.blit(
        sub_text,
        sub_text.get_rect(center=(SCREEN_WIDTH // 2, 300)),
    )


def _draw_boss_hud(surface, state, font):
    boss = next((enemy for enemy in state.enemies if enemy.is_boss), None)
    if boss is None:
        return

    boss_width = 350
    x = SCREEN_WIDTH // 2 - boss_width // 2
    y = 92
    pg.draw.rect(surface, (50, 25, 30), (x, y, boss_width, 14))
    boss_fill = round(boss_width * boss.hp / boss.max_hp)
    pg.draw.rect(surface, (185, 35, 55), (x, y, boss_fill, 14))
    pg.draw.rect(surface, (255, 255, 255), (x, y, boss_width, 14), 1)
    text = font.render(
        f"BOSS {boss.hp}/{boss.max_hp}",
        True,
        (255, 255, 255),
    )
    surface.blit(text, text.get_rect(center=(SCREEN_WIDTH // 2, y + 7)))


def _draw_stage_title(surface, stage, large_font):
    now = pg.time.get_ticks()
    if stage.clear_started_at is not None:
        title = large_font.render("STAGE CLEAR", True, (255, 195, 40))
    elif now - stage.stage_started_at < 1100:
        label = f"BOSS {stage.label}" if stage.is_boss_stage else f"STAGE {stage.label}"
        title = large_font.render(label, True, (65, 80, 150))
    else:
        return
    surface.blit(title, title.get_rect(center=(SCREEN_WIDTH // 2, 150)))
