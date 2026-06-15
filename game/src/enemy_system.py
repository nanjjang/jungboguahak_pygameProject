from src.constants import DIFFICULTY_SETTINGS


def select_active_enemies(enemies, player, difficulty):
    bosses = {enemy for enemy in enemies if enemy.is_boss}
    candidates = [
        enemy
        for enemy in enemies
        if not enemy.is_boss and not enemy.defeated and enemy.can_recognize(player.rect)
    ]
    candidates.sort(
        key=lambda enemy: (
            abs(enemy.rect.centerx - player.rect.centerx) - (70 if enemy.engaged else 0)
        )
    )
    limit = DIFFICULTY_SETTINGS[difficulty]["max_active_enemies"]
    return bosses | set(candidates[:limit])


def update_enemies(state):
    active_enemies = select_active_enemies(
        state.enemies,
        state.player,
        state.difficulty,
    )
    for enemy in list(state.enemies):
        enemy.update(
            kirby=state.player,
            ground_y=state.ground_y,
            engage=enemy in active_enemies,
        )
        for shot in enemy.pending_projectiles:
            state.enemy_projectiles.add(shot)
        enemy.pending_projectiles.clear()
