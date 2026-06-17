"""한 프레임 동안 실제 게임 상태를 업데이트하는 파일."""

from src.combat_system import resolve_combat
from src.constants import SCREEN_WIDTH
from src.enemy_system import update_enemies
from src.projectile import Projectile


def update_gameplay(state, actions):
    """플레이어, 적, 발사체, 스테이지 전환을 한 프레임 진행한다."""
    lives_before = state.player.lives
    if not state.player.game_over and not state.stage.completed:
        if not state.stage.transitioning:
            # 일반 플레이 중일 때만 캐릭터와 전투를 업데이트한다.
            _update_active_stage(state, actions)
        # 스테이지 클리어 연출 중이어도 전환 타이머는 계속 확인한다.
        _update_stage_transition(state, actions)

    # 목숨을 잃으면 카메라를 시작 위치 쪽으로 되돌린다.
    state.update_camera(reset=state.player.lives < lives_before)
    state.update_damage_numbers()


def _update_active_stage(state, actions):
    """스테이지가 진행 중일 때 움직임, 공격, 적 AI, 충돌을 처리한다."""
    player = state.player
    player.update(
        actions,
        state.enemies,
        spit_pressed=actions.spit_pressed,
        gulp_pressed=actions.gulp_pressed,
        punch_pressed=actions.punch_pressed,
        kick_pressed=actions.kick_pressed,
    )

    for projectile_data in player.pending_projectiles:
        # Kirby가 만든 발사체 정보는 여기서 실제 Sprite 객체로 바꾼다.
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
        # 플레이어와 너무 멀어진 적 발사체는 메모리와 충돌 계산을 줄이기 위해 제거한다.
        if abs(shot.rect.centerx - player.rect.centerx) > SCREEN_WIDTH * 2:
            shot.kill()

    resolve_combat(state)
    if not state.enemies:
        # 적이 전부 사라졌으면 남은 적 발사체도 같이 정리한다.
        state.enemy_projectiles.empty()


def _update_stage_transition(state, actions):
    """문 앞에서 입장 키를 눌렀을 때 다음 스테이지로 넘어간다."""
    replacement = state.stage.update(
        state.enemies,
        player_rect=state.player.rect,
        enter_pressed=actions.enter_pressed,
    )
    if replacement is not None:
        state.enter_stage(replacement)
