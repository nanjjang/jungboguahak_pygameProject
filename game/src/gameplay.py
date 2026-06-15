from src.combat_system import resolve_combat
from src.constants import SCREEN_WIDTH
from src.enemy_system import update_enemies
from src.projectile import Projectile


def update_gameplay(state, actions, keys):
    lives_before = state.player.lives
    if not state.player.game_over and not state.stage.completed:
        if not state.stage.transitioning:
            _update_active_stage(state, actions, keys)
        _update_stage_transition(state, actions)

    state.update_camera(reset=state.player.lives < lives_before)
    state.update_damage_numbers()


def _update_active_stage(state, actions, keys):
    player = state.player
    player.update(
        keys,
        state.enemies,
        spit_pressed=actions.spit_pressed,
        gulp_pressed=actions.gulp_pressed,
        punch_pressed=actions.punch_pressed,
        kick_pressed=actions.kick_pressed,
    )

    for projectile_data in player.pending_projectiles:
        state.projectiles.add(
            Projectile(
                **projectile_data,
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
    replacement = state.stage.update(
        state.enemies,
        player_rect=state.player.rect,
        enter_pressed=actions.enter_pressed,
    )
    if replacement is not None:
        state.enter_stage(replacement)
