# 게임 화면 그리기

from src.game_ui import draw_end_overlay, draw_status_hud


def render_game(surface, state, font, large_font):
    # 한 프레임 그리기
    transitioning = state.stage.transitioning
    # 배경 먼저
    state.stage.draw_environment(
        surface,
        state.camera_x,
        state.enemies,
        font,
        state.player.rect,
    )
    for enemy in state.enemies:
        enemy.draw(surface, state.camera_x)
    # 적 발사체
    _draw_sprite_group(surface, state.enemy_projectiles, state.camera_x)
    if transitioning:
        pass
    else:
        # 흡입 효과 먼저
        state.player.draw_inhale_effect(surface, state.camera_x)
        state.player.draw(surface, state.camera_x)
    _draw_sprite_group(surface, state.projectiles, state.camera_x)
    if not transitioning:
        # 빔 그리기
        state.player.draw_beams(surface, state.camera_x)
    for number in state.damage_numbers:
        number.draw(surface, state.camera_x)

    state.player.draw_UI(surface)
    draw_status_hud(surface, state, font, large_font)
    if state.player.game_over:
        # 게임오버 화면
        draw_end_overlay(
            surface,
            "GAME OVER",
            "R: restart    Q: exit",
            large_font,
            font,
        )
    elif state.stage.completed:
        draw_end_overlay(
            surface,
            "ALL STAGES CLEAR!",
            "R: play again",
            large_font,
            font,
        )


def _draw_sprite_group(surface, sprites, camera_x):
    # 카메라 보정
    offset = round(camera_x)
    for sprite in sprites:
        surface.blit(sprite.image, sprite.rect.move(-offset, 0))
