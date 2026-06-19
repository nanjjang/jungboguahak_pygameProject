# 적 업데이트

from src.constants import DIFFICULTY_SETTINGS


def select_active_enemies(enemies, player, difficulty):
    # 움직일 적 고르기
    active_enemies = set()
    candidates = []

    for index, enemy in enumerate(enemies):
        if enemy.is_boss:
            # 보스는 항상 움직임
            active_enemies.add(enemy)
            continue
        if enemy.defeated:
            continue
        if not enemy.can_recognize(player.rect):
            continue

        distance = abs(enemy.rect.centerx - player.rect.centerx)
        candidates.append((distance, index, enemy))

    candidates.sort()
    # 난이도별 수 제한
    limit = DIFFICULTY_SETTINGS[difficulty]["max_active_enemies"]
    for _, _, enemy in candidates[:limit]:
        active_enemies.add(enemy)
    return active_enemies


def update_enemies(state):
    # 적 전체 처리
    active_enemies = select_active_enemies(
        state.enemies,
        state.player,
        state.difficulty,
    )
    for enemy in list(state.enemies):
        enemy_ground_y = state.stage.floor_at_x(
            enemy.rect.centerx,
            preferred_y=enemy.rect.bottom,
        )
        enemy.update(
            kirby=state.player,
            ground_y=enemy_ground_y,
            engage=enemy in active_enemies,
        )
        if getattr(enemy, "ai_type", None) != "swooper" and not enemy.defeated:
            enemy.rect.bottom = state.stage.floor_at_x(
                enemy.rect.centerx,
                preferred_y=enemy.rect.bottom,
        )
        for shot in enemy.pending_projectiles:
            # 발사체 넘기기
            state.enemy_projectiles.add(shot)
        enemy.pending_projectiles.clear()
