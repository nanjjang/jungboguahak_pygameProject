from src.combat import DamageNumber


def spawn_damage_number(numbers, amount, rect):
    if amount > 0:
        numbers.append(DamageNumber(amount, rect))


def damage_enemy(enemy, amount, source_x, state):
    dealt = enemy.take_damage(amount, source_x=source_x)
    spawn_damage_number(state.damage_numbers, dealt, enemy.rect)
    if enemy.defeated and enemy in state.enemies:
        state.enemies.remove(enemy)
    return dealt


def resolve_combat(state):
    _resolve_projectile_hits(state)
    _resolve_beam_hits(state)
    _resolve_melee_hits(state)
    _resolve_enemy_hits(state)


def _resolve_projectile_hits(state):
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
    player = state.player
    beam_rect = player.active_beam_rect
    if beam_rect is None or player.beam_kill_cd > 0:
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
            enemy.last_melee_serial = player.attack_serial
            damage_enemy(
                enemy,
                player.melee_damage,
                player.rect.centerx,
                state,
            )


def _resolve_enemy_hits(state):
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
                enemy.attack_damage
                if enemy.state in attack_states
                else enemy.contact_damage
            )
            dealt = player.take_damage(
                damage,
                source_x=enemy.rect.centerx,
            )
            spawn_damage_number(state.damage_numbers, dealt, hit_rect)
