"""현재 프레임에 실제로 움직일 적을 고르고 업데이트한다."""

from src.constants import DIFFICULTY_SETTINGS


def select_active_enemies(enemies, player, difficulty):
    """플레이어와 가까운 적 중 난이도 제한만큼만 적극적으로 행동하게 고른다."""
    active_enemies = set()
    candidates = []

    for index, enemy in enumerate(enemies):
        if enemy.is_boss:
            # 보스는 항상 활성화해서 플레이어와 계속 싸우게 한다.
            active_enemies.add(enemy)
            continue
        if enemy.defeated:
            continue
        if not enemy.can_recognize(player.rect):
            continue

        distance = abs(enemy.rect.centerx - player.rect.centerx)
        candidates.append((distance, index, enemy))

    candidates.sort()
    # 쉬움/보통/어려움마다 동시에 달려드는 적 수를 다르게 제한한다.
    limit = DIFFICULTY_SETTINGS[difficulty]["max_active_enemies"]
    for _, _, enemy in candidates[:limit]:
        active_enemies.add(enemy)
    return active_enemies


def update_enemies(state):
    """모든 적을 업데이트하고, 적이 만든 발사체를 전역 발사체 그룹에 넣는다."""
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
            # Enemy 객체 내부에 임시 저장된 발사체를 실제 게임 상태로 옮긴다.
            state.enemy_projectiles.add(shot)
        enemy.pending_projectiles.clear()
