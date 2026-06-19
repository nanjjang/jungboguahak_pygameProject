"""체력바, 스테이지 이름, 게임오버 화면 같은 UI를 그리는 파일."""

import pygame as pg

from src.constants import DIFFICULTY_SETTINGS, SCREEN_HEIGHT, SCREEN_WIDTH


def draw_status_hud(surface, state, font, large_font):
    """플레이 중 항상 보이는 HP, 목숨, 스테이지 정보를 그린다."""
    player = state.player
    stage = state.stage
    x, y, width, height = 10, 67, 220, 18
    # HP 바는 배경 사각형, 채워진 체력, 테두리 순서로 그린다.
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
    # 오른쪽 위에는 현재 스테이지와 난이도를 함께 표시한다.
    stage_text = font.render(
        f"STAGE {stage.label}   {difficulty_label}",
        True,
        (255, 255, 255),
    )
    stage_shadow = font.render(
        f"STAGE {stage.label}   {difficulty_label}",
        True,
        (25, 20, 35),
    )
    rect = stage_text.get_rect(topright=(SCREEN_WIDTH - 12, 12))
    surface.blit(stage_shadow, rect.move(2, 2))
    surface.blit(stage_text, rect)
    _draw_boss_hud(surface, state, font)
    _draw_stage_title(surface, stage, large_font)


def draw_end_overlay(surface, title, subtitle, large_font, font):
    """게임오버 또는 전체 클리어 때 화면 중앙에 안내 문구를 덮어 그린다."""
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


def draw_quit_confirm_popup(surface, font, selected_yes):
    """게임오버 화면에서 종료 여부를 묻는 확인 팝업을 그린다."""
    shade = pg.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pg.SRCALPHA)
    shade.fill((0, 0, 0, 95))
    surface.blit(shade, (0, 0))

    popup_rect = pg.Rect(0, 0, 430, 190)
    popup_rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
    pg.draw.rect(surface, (255, 248, 238), popup_rect, border_radius=18)
    pg.draw.rect(surface, (210, 70, 95), popup_rect, 4, border_radius=18)

    title = font.render("진짜 게임을 종료할까요?", True, (45, 35, 45))
    surface.blit(title, title.get_rect(center=(popup_rect.centerx, popup_rect.y + 58)))

    guide = font.render("← → 선택    ENTER 결정", True, (95, 80, 90))
    surface.blit(guide, guide.get_rect(center=(popup_rect.centerx, popup_rect.y + 92)))

    yes_rect = pg.Rect(popup_rect.x + 82, popup_rect.y + 120, 112, 42)
    no_rect = pg.Rect(popup_rect.right - 194, popup_rect.y + 120, 112, 42)
    _draw_confirm_button(surface, font, yes_rect, "네", selected_yes)
    _draw_confirm_button(surface, font, no_rect, "아니요", not selected_yes)


def _draw_confirm_button(surface, font, rect, text, selected):
    fill = (255, 220, 95) if selected else (245, 232, 222)
    border = (175, 55, 80) if selected else (165, 145, 145)
    text_color = (45, 35, 45)
    pg.draw.rect(surface, fill, rect, border_radius=10)
    pg.draw.rect(surface, border, rect, 3, border_radius=10)
    label = font.render(text, True, text_color)
    surface.blit(label, label.get_rect(center=rect.center))


def _draw_boss_hud(surface, state, font):
    """보스가 있는 스테이지에서만 보스 체력바를 그린다."""
    boss = None
    for enemy in state.enemies:
        if enemy.is_boss:
            boss = enemy
            break

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
    """스테이지 시작 직후나 클리어 중에 중앙 큰 제목을 잠깐 보여준다."""
    now = pg.time.get_ticks()
    if stage.clear_started_at is not None:
        label = "STAGE CLEAR"
        color = (255, 225, 70)
    elif now - stage.stage_started_at < 1100:
        label = f"BOSS {stage.label}" if stage.is_boss_stage else f"STAGE {stage.label}"
        color = (255, 245, 180)
    else:
        return
    shadow = large_font.render(label, True, (55, 28, 70))
    title = large_font.render(label, True, color)
    rect = title.get_rect(center=(SCREEN_WIDTH // 2, 150))
    surface.blit(shadow, rect.move(3, 3))
    surface.blit(title, rect)
