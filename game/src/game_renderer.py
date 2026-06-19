"""현재 게임 상태를 화면에 그리는 순서를 담당한다."""

from src.game_ui import draw_end_overlay, draw_status_hud


def render_game(surface, state, font, large_font):
    """배경부터 HUD까지 한 프레임에 필요한 모든 화면 요소를 그린다."""
    transitioning = state.stage.transitioning
    # 가장 뒤쪽에 배경/지형/문을 먼저 그린다.
    state.stage.draw_environment(
        surface,
        state.camera_x,
        state.enemies,
        font,
        state.player.rect,
    )
    for enemy in state.enemies:
        enemy.draw(surface, state.camera_x)
    # 적 발사체는 적보다 뒤나 앞에 놓여도 되지만, 플레이어보다 먼저 그린다.
    _draw_sprite_group(surface, state.enemy_projectiles, state.camera_x)
    if transitioning:
        # draw_stage_clear_animation(
        #     surface,
        #     state.stage.clear_started_at,
        #     state.player.rect,
        #     state.stage.goal_rect,
        #     state.camera_x,
        # )
        pass
    else:
        # 플레이어 흡입 효과는 Kirby 몸 앞쪽에 보이도록 본체보다 먼저 그린다.
        state.player.draw_inhale_effect(surface, state.camera_x)
        state.player.draw(surface, state.camera_x)
    _draw_sprite_group(surface, state.projectiles, state.camera_x)
    if not transitioning:
        # 빔은 플레이어 위치를 기준으로 화면 위에 길게 그려진다.
        state.player.draw_beams(surface, state.camera_x)
    for number in state.damage_numbers:
        number.draw(surface, state.camera_x)

    state.player.draw_UI(surface)
    draw_status_hud(surface, state, font, large_font)
    if state.player.game_over:
        # 게임오버나 전체 클리어 상태에서는 반투명 안내 화면을 덮어 그린다.
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
    """월드 좌표 Sprite 그룹을 카메라 위치만큼 보정해서 화면에 그린다."""
    offset = round(camera_x)
    for sprite in sprites:
        surface.blit(sprite.image, sprite.rect.move(-offset, 0))
