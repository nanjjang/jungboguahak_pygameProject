from src.game_ui import draw_end_overlay, draw_status_hud


def render_game(surface, state, font, large_font):
    state.stage.draw_environment(
        surface,
        state.camera_x,
        state.enemies,
        font,
    )
    for enemy in state.enemies:
        enemy.draw(surface, state.camera_x)
    _draw_sprite_group(surface, state.enemy_projectiles, state.camera_x)
    state.player.draw_inhale_effect(surface, state.camera_x)
    state.player.draw(surface, state.camera_x)
    _draw_sprite_group(surface, state.projectiles, state.camera_x)
    state.player.draw_beams(surface, state.camera_x)
    for number in state.damage_numbers:
        number.draw(surface, state.camera_x)

    state.player.draw_hud(surface)
    draw_status_hud(surface, state, font, large_font)
    if state.player.game_over:
        draw_end_overlay(
            surface,
            "GAME OVER",
            "R: restart",
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
    offset = round(camera_x)
    for sprite in sprites:
        surface.blit(sprite.image, sprite.rect.move(-offset, 0))
