"""플레이어, 적, 발사체 사이의 충돌과 데미지를 처리하는 파일."""

from src.combat import DamageNumber


def spawn_damage_number(numbers, amount, rect):
    """실제로 데미지가 들어갔을 때만 화면 표시용 숫자를 추가한다."""
    if amount > 0:
        numbers.append(DamageNumber(amount, rect))


def damage_enemy(enemy, amount, source_x, state):
    """적에게 피해를 주고, 쓰러졌으면 현재 스테이지 적 목록에서 제거한다."""
    dealt = enemy.take_damage(amount, source_x=source_x)
    spawn_damage_number(state.damage_numbers, dealt, enemy.rect)
    if enemy.defeated and enemy in state.enemies:
        state.enemies.remove(enemy)
    return dealt


def resolve_combat(state):
    """한 프레임 동안 가능한 모든 전투 충돌을 순서대로 처리한다."""
    _resolve_projectile_hits(state)
    _resolve_beam_hits(state)
    _resolve_melee_hits(state)
    _resolve_enemy_hits(state)


def _resolve_projectile_hits(state):
    """Kirby가 뱉은 별/속성 발사체가 적에게 맞았는지 확인한다."""
    for projectile in list(state.projectiles):
        for enemy in list(state.enemies):
            if projectile.rect.colliderect(enemy.rect) and not enemy.being_inhaled:
                damage_enemy(
                    enemy,
                    projectile.damage,
                    projectile.rect.centerx,
                    state,
                )
                projectile.kill()
                break


def _resolve_beam_hits(state):
    """지속형 빔 공격이 적에게 닿았는지 확인한다."""
    player = state.player
    beam_rect = player.active_beam_rect
    if beam_rect is None or player.beam_kill_cd > 0:
        # 빔은 매 프레임 계속 닿기 때문에 짧은 쿨타임으로 중복 피해를 막는다.
        return

    for enemy in list(state.enemies):
        if beam_rect.colliderect(enemy.rect) and not enemy.being_inhaled:
            damage_enemy(
                enemy,
                player.beam_damage,
                player.rect.centerx,
                state,
            )
            player.beam_kill_cd = 8
            break


def _resolve_melee_hits(state):
    """펀치/킥 콤보의 활성 히트박스가 적에게 닿았는지 확인한다."""
    player = state.player
    melee_rect = player.melee_hit_rect
    if melee_rect is None:
        return

    for enemy in list(state.enemies):
        if (
            melee_rect.colliderect(enemy.rect)
            and not enemy.being_inhaled
            and enemy.last_melee_serial != player.attack_serial
        ):
            # 같은 공격 동작 하나가 같은 적을 여러 번 때리지 않도록 serial을 기록한다.
            enemy.last_melee_serial = player.attack_serial
            damage_enemy(
                enemy,
                player.melee_damage,
                player.rect.centerx,
                state,
            )


def _resolve_enemy_hits(state):
    """적 발사체와 적 몸통 공격이 플레이어에게 닿았는지 확인한다."""
    player = state.player
    for shot in list(state.enemy_projectiles):
        if shot.rect.colliderect(player.rect):
            hit_rect = player.rect.copy()
            dealt = player.take_damage(
                shot.damage,
                source_x=shot.rect.centerx,
            )
            spawn_damage_number(state.damage_numbers, dealt, hit_rect)
            shot.kill()

    attack_states = ("lunge", "charge", "swoop", "boss_dash")
    for enemy in state.enemies:
        if enemy.being_inhaled or enemy.defeated:
            continue
        if enemy.rect.colliderect(player.rect):
            hit_rect = player.rect.copy()
            damage = (
                # 공격 상태일 때는 더 강한 공격 데미지, 단순 접촉이면 접촉 데미지를 쓴다.
                enemy.attack_damage
                if enemy.state in attack_states
                else enemy.contact_damage
            )
            dealt = player.take_damage(
                damage,
                source_x=enemy.rect.centerx,
            )
            spawn_damage_number(state.damage_numbers, dealt, hit_rect)
