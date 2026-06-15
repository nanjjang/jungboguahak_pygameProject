from src.constants import DIFFICULTY_SETTINGS


def select_active_enemies(enemies, player, difficulty):
    active_enemies = set()
    candidates = []

    for index, enemy in enumerate(enemies):
        if enemy.is_boss:
            active_enemies.add(enemy)
            continue
        if enemy.defeated:
            continue
        if not enemy.can_recognize(player.rect):
            continue

        distance = abs(enemy.rect.centerx - player.rect.centerx)
        candidates.append((distance, index, enemy))

    candidates.sort()
    limit = DIFFICULTY_SETTINGS[difficulty]["max_active_enemies"]
    for _, _, enemy in candidates[:limit]:
        active_enemies.add(enemy)
    return active_enemies


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
