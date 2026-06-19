# 게임 업데이트

from src.combat_system import resolve_combat
from src.constants import SCREEN_WIDTH
from src.enemy_system import update_enemies
from src.projectile import Projectile


def update_gameplay(state, actions):
    lives_before = state.player.lives
    if not state.player.game_over and not state.stage.completed:
        if not state.stage.transitioning:
            _update_active_stage(state, actions)
        _update_stage_transition(state, actions)

    state.update_camera(reset=state.player.lives < lives_before)
    state.update_damage_numbers()


def _update_active_stage(state, actions):
    player = state.player
    player.update(
        actions,
        state.enemies,
        terrain_rects=state.stage.terrain_rects,
        ground_y=state.stage.floor_y,
        spit_pressed=actions.spit_pressed,
        gulp_pressed=actions.gulp_pressed,
        punch_pressed=actions.punch_pressed,
        kick_pressed=actions.kick_pressed,
    )

    for projectile_data in player.pending_projectiles:
        state.projectiles.add(
            Projectile(
                projectile_data["x"],
                projectile_data["y"],
                projectile_data["facing_right"],
                element=projectile_data["element"],
                world_width=state.stage.world_width,
            )
        )
    player.pending_projectiles.clear()

    update_enemies(state)
    state.projectiles.update()
    state.enemy_projectiles.update()
    for shot in list(state.enemy_projectiles):
        if abs(shot.rect.centerx - player.rect.centerx) > SCREEN_WIDTH * 2:
            shot.kill()

    resolve_combat(state)
    if not state.enemies:
        state.enemy_projectiles.empty()


def _update_stage_transition(state, actions):
    if actions.enter_pressed and not state.stage.transitioning:
        room_enemies = state.stage.try_enter_local_door(state.player)
        if room_enemies is not None:
            state.enter_room(room_enemies)
            return

        # 출구 문 시도

    replacement = state.stage.update(
        state.enemies,
        player_rect=state.player.rect,
        enter_pressed=actions.enter_pressed,
    )
    if replacement is not None:
        state.enter_stage(replacement)
