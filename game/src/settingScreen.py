"""게임 중 ESC로 들어가는 설정 메뉴와 캐릭터 설정 메뉴."""

import pygame
import sys
import load
from src.constants import (
    FPS,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
)
# 화면 설정 관련 변수
# 이 파일은 자체 설정 화면을 그리기 위해 별도의 screen/clock 참조를 가진다.
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("커비 게임 - 고급 설정 메뉴")
clock = pygame.time.Clock()


# 색상 정의
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
PINK = (255, 182, 193)
DARK_PINK = (230, 140, 160)
GRAY = (100, 100, 100)
LIGHT_GRAY = (180, 180, 180)
YELLOW = (255, 215, 0)
DARK_GRAY = (40, 40, 40)
BLUE = (100, 149, 237)
GREEN = (60, 179, 113)

# 폰트 설정
font = load.get_korean_font(22)
title_font = load.get_korean_font(36)

# --- 실제 적용 데이터 ---
# 실제 적용 데이터는 메뉴를 닫은 뒤에도 유지되는 설정값이다.
volume = 50
difficulties = ["Easy", "Normal", "Hard"]
diff_index = 1
temp_diff_index = 1  # 난이도 임시 조작용 인덱스

nickname = "Kirby_Fan"
screen_sizes = [(1000, 600), (1024, 768), (1280, 720)]
size_index = 0
is_fullscreen = False

# 캐릭터 세팅 관련 변수
char_colors = ["Pink", "Yellow", "Blue", "Green"]
color_map = {"Pink": PINK, "Yellow": YELLOW, "Blue": BLUE, "Green": GREEN}
costumes = ["None", "Sword", "Fire", "Beam"]

# [진짜 적용 값]
current_color_idx = 0
current_costume_idx = 0
# [세팅 메뉴 내 임시 값]
# 임시 값은 사용자가 ENTER로 적용하기 전까지 실제 캐릭터 값에 반영하지 않는다.
temp_color_idx = 0
temp_costume_idx = 0

# --- 상태 플래그 ---
typing_mode = False
confirm_mode = False       # 난이도 변경 후 다른 메뉴 이동 시 팝업 플래그
pending_direction = None   # 팝업 승낙 시 이동할 위/아래 방향 저장용 변수

# 볼륨 바 마우스 드래그 상태
volume_dragging = False

# 볼륨 바 위치 및 크기 정의 (x, y, width, height)
VOLUME_BAR_RECT = pygame.Rect(650, 110, 200, 15)

# --- 방향키 연속 조작용 시간 측정 변수 ---
key_hold_time = 0        # 키가 유지된 시간 (밀리초)
last_tick_time = 0       # 마지막으로 주기 기능이 실행된 타이밍 (밀리초)
pressed_direction = None # 현재 누르고 있는 방향 ("LEFT" 또는 "RIGHT")


def draw_text(text, font, color, surface, x, y):
    """텍스트를 지정한 위치에 그리는 작은 반복 작업용 함수."""
    text_obj = font.render(text, True, color)
    text_rect = text_obj.get_rect()
    text_rect.topleft = (x, y)
    surface.blit(text_obj, text_rect)


def previous_menu_index(selected_index, menu_items):
    if selected_index == 7:
        return len(menu_items) - 1
    if selected_index == 0:
        return 7
    return selected_index - 1


def next_menu_index(selected_index, menu_items):
    if selected_index == 7:
        return 0
    if selected_index == len(menu_items) - 1:
        return 7
    return selected_index + 1


def apply_screen_mode():
    global screen

    flags = 0
    if is_fullscreen:
        flags = pygame.FULLSCREEN
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), flags)


# ====================================================
# 순서 관계없이 자유롭게 선택하는 캐릭터 세팅 화면
# ====================================================
def show_character_setting_menu():
    """캐릭터 색상과 코스튬을 고르는 하위 설정 화면."""
    global current_color_idx, current_costume_idx, temp_color_idx, temp_costume_idx

    # 하위 메뉴에 들어올 때 현재 적용값을 임시값으로 복사한다.
    temp_color_idx = current_color_idx
    temp_costume_idx = current_costume_idx
    selected_row = 0 

    char_menu_running = True
    while char_menu_running:
        clock.tick(30)
        screen.fill(BLACK)  

        # 왼쪽에는 현재 임시 선택 상태의 캐릭터 미리보기를 그린다.
        draw_text("★ 캐릭터 세팅 ★", title_font, PINK, screen, 50, 40)
        draw_text("방향키 [위/아래] 줄이동, [좌/우] 변경 | [ENTER] 승낙(적용), [ESC] 거절(취소)", font, LIGHT_GRAY, screen, 50, 95)

        box_w, box_h = 220, 220
        box_x = 80
        box_y = (SCREEN_HEIGHT // 2) - (box_h // 2)
        
        kirby_color = color_map[char_colors[temp_color_idx]]
        pygame.draw.rect(screen, kirby_color, (box_x, box_y, box_w, box_h))
        pygame.draw.rect(screen, WHITE, (box_x, box_y, box_w, box_h), 4)
        
        draw_text(f"[{costumes[temp_costume_idx]}]", font, BLACK, screen, box_x + 60, box_y + 95)
        draw_text("< 현재 캐릭터 상태 >", font, WHITE, screen, box_x + 15, box_y - 35)

        start_x = 420
        obj_w, obj_h = 110, 60
        gap = 25

        step1_color = YELLOW if selected_row == 0 else WHITE
        draw_text("1. 캐릭터 색상 선택", font, step1_color, screen, start_x, 180)
        
        for idx, name in enumerate(char_colors):
            # 선택 가능한 색상을 가로로 나열하고 현재 선택값에 테두리를 준다.
            item_x = start_x + idx * (obj_w + gap)
            item_y = 220
            pygame.draw.rect(screen, color_map[name], (item_x, item_y, obj_w, obj_h))
            if selected_row == 0 and temp_color_idx == idx:
                border_color = YELLOW
                border_size = 4
            else:
                border_color = WHITE if temp_color_idx == idx else GRAY
                border_size = 2
            pygame.draw.rect(screen, border_color, (item_x, item_y, obj_w, obj_h), border_size)
            draw_text(name, font, BLACK, screen, item_x + 15, item_y + 15)

        step2_color = YELLOW if selected_row == 1 else WHITE
        draw_text("2. 캐릭터 코스튬 선택", font, step2_color, screen, start_x, 340)
        
        for idx, name in enumerate(costumes):
            # 코스튬도 색상과 같은 방식으로 선택 테두리를 표시한다.
            item_x = start_x + idx * (obj_w + gap)
            item_y = 380
            pygame.draw.rect(screen, DARK_GRAY, (item_x, item_y, obj_w, obj_h))
            if selected_row == 1 and temp_costume_idx == idx:
                border_color = YELLOW
                border_size = 4
            else:
                border_color = WHITE if temp_costume_idx == idx else GRAY
                border_size = 2
            pygame.draw.rect(screen, border_color, (item_x, item_y, obj_w, obj_h), border_size)
            draw_text(name, font, WHITE, screen, item_x + 15, item_y + 15)

        pygame.draw.rect(screen, DARK_GRAY, (0, 530, SCREEN_WIDTH, 70))
        if selected_row == 0:
            draw_text("▶ 방향키 [위/아래]로 코스튬 메뉴 이동 가능 | [좌/우]로 색상 변경", font, YELLOW, screen, 50, 550)
        else:
            draw_text("▶ 방향키 [위/아래]로 색상 메뉴 이동 가능 | [좌/우]로 코스튬 변경", font, GREEN, screen, 50, 550)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    # ESC는 임시 선택을 버리고 이전 메뉴로 돌아간다.
                    char_menu_running = False
                elif event.key == pygame.K_RETURN:
                    # ENTER는 임시 선택을 실제 적용값으로 복사한다.
                    current_color_idx = temp_color_idx
                    current_costume_idx = temp_costume_idx
                    char_menu_running = False
                elif event.key == pygame.K_UP or event.key == pygame.K_DOWN:
                    selected_row = 1 - selected_row
                elif event.key == pygame.K_LEFT:
                    if selected_row == 0:
                        temp_color_idx = (temp_color_idx - 1) % len(char_colors)
                    else:
                        temp_costume_idx = (temp_costume_idx - 1) % len(costumes)
                elif event.key == pygame.K_RIGHT:
                    if selected_row == 0:
                        temp_color_idx = (temp_color_idx + 1) % len(char_colors)
                    else:
                        temp_costume_idx = (temp_costume_idx + 1) % len(costumes)


# ====================================================
# 메인 설정 메뉴 화면 함수
# ====================================================
def show_settings_menu():
    """볼륨, 난이도, 캐릭터, 화면 크기 등 전체 설정 메뉴를 보여준다."""
    global volume, diff_index, temp_diff_index, nickname, size_index, is_fullscreen, screen, SCREEN_WIDTH, SCREEN_HEIGHT
    global current_color_idx, current_costume_idx
    global typing_mode, confirm_mode, volume_dragging, pending_direction
    global key_hold_time, last_tick_time, pressed_direction

    menu_items = [
        "볼륨 바 (Volume)",
        "난이도 (Difficulty)",
        "캐릭터 세팅 (Character Settings)",
        "화면 크기 (Screen Size)",
        "화면 타입 (Screen Type)",
        "재시작 (Restart)",
        "게임 종료 (Exit)"
    ]
    selected_index = 1  # 난이도 테스트를 편하게 하기 위해 1로 설정 유지

    # 난이도는 바로 적용하지 않고, 메뉴 이동 시 확인 팝업을 띄우기 위해 임시값을 쓴다.
    temp_diff_index = diff_index

    menu_running = True
    while menu_running:
        dt = clock.tick(30)
        screen.fill(BLACK)

        # 타이틀
        draw_text("SETTINGS MENU (ESC to Return)", title_font, PINK, screen, 50, 30)

        # 왼쪽 UI: 실제 적용 값 렌더링
        box_x, box_y, box_w, box_h = 80, 220, 160, 160
        kirby_color = color_map[char_colors[current_color_idx]]
        pygame.draw.rect(screen, kirby_color, (box_x, box_y, box_w, box_h))
        pygame.draw.rect(screen, WHITE, (box_x, box_y, box_w, box_h), 3) 
        draw_text(f"[{costumes[current_costume_idx]}]", font, BLACK, screen, box_x + 35, box_y + 65)

        if selected_index == 7:
            name_color = YELLOW
        else:
            name_color = WHITE
        if typing_mode:
            name_color = PINK

        if typing_mode:
            name_text = f"[ {nickname}_ ]"
        else:
            name_text = f"[ {nickname} ]"
        draw_text(name_text, font, name_color, screen, box_x + 10, box_y + box_h + 20)

        # 오른쪽 UI: 메인 설정 항목
        for i, item in enumerate(menu_items):
            # 현재 선택한 메뉴 줄만 노란색으로 강조한다.
            color = YELLOW if (i == selected_index and selected_index != 7) else WHITE

            val_text = ""
            if i == 0:
                val_text = f"{volume}%"
            elif i == 1:
                val_text = f"< {difficulties[temp_diff_index]} >"
            elif i == 2:
                val_text = "(Press Enter)"
            elif i == 3:
                val_text = f"< {screen_sizes[size_index][0]}x{screen_sizes[size_index][1]} >"
            elif i == 4:
                if is_fullscreen:
                    val_text = "< Fullscreen >"
                else:
                    val_text = "< Windowed >"
            elif i == 5:
                val_text = "(Press Enter)"
            elif i == 6:
                val_text = "(Press Enter)"

            draw_text(item, font, color, screen, 320, 100 + i * 55)
            # 볼륨 바가 위치한 i == 0 항목이 아닐 때만 일반 텍스트 수치값 출력
            if i != 0:
                draw_text(val_text, font, color, screen, 800, 100 + i * 55)

        # ----------------------------------------------------
        # 볼륨 슬라이더 및 우측 수치 텍스트 복구
        # ----------------------------------------------------
        pygame.draw.rect(screen, GRAY, VOLUME_BAR_RECT) 
        filled_width = int(VOLUME_BAR_RECT.width * (volume / 100))
        pygame.draw.rect(screen, PINK, (VOLUME_BAR_RECT.x, VOLUME_BAR_RECT.y, filled_width, VOLUME_BAR_RECT.height))
        handle_x = VOLUME_BAR_RECT.x + filled_width
        handle_y = VOLUME_BAR_RECT.y + VOLUME_BAR_RECT.height // 2
        if selected_index == 0:
            handle_color = YELLOW
        else:
            handle_color = WHITE
        pygame.draw.circle(screen, handle_color, (handle_x, handle_y), 8)

        # 볼륨 바 오른쪽에 % 수치를 선명하게 다시 그려줍니다.
        draw_text(
            f"{volume}%",
            font,
            handle_color,
            screen,
            VOLUME_BAR_RECT.x + VOLUME_BAR_RECT.width + 15,
            VOLUME_BAR_RECT.y - 5,
        )

        # 난이도 이탈 시 발생하는 승낙/거절 팝업창
        if confirm_mode:
            popup_rect = pygame.Rect(
                SCREEN_WIDTH // 2 - 200,
                SCREEN_HEIGHT // 2 - 80,
                400,
                160,
            )
            pygame.draw.rect(screen, DARK_GRAY, popup_rect)
            pygame.draw.rect(screen, PINK, popup_rect, 3)
            draw_text(
                "난이도 변경 사항을 적용하시겠습니까?",
                font,
                WHITE,
                screen,
                SCREEN_WIDTH // 2 - 160,
                SCREEN_HEIGHT // 2 - 40,
            )
            draw_text(
                "[Enter] 승낙(적용)  /  [ESC] 거절(취소)",
                font,
                YELLOW,
                screen,
                SCREEN_WIDTH // 2 - 160,
                SCREEN_HEIGHT // 2 + 10,
            )

        pygame.display.flip()

        # 볼륨 홀딩 처리
        if selected_index == 0 and pressed_direction is not None and not typing_mode:
            # 좌/우 키를 오래 누르면 볼륨이 일정 간격으로 계속 변하게 한다.
            key_hold_time += dt
            if key_hold_time >= 600:
                current_time = pygame.time.get_ticks()
                if current_time - last_tick_time >= 100:
                    if pressed_direction == "LEFT":
                        volume = max(0, volume - 5)
                    elif pressed_direction == "RIGHT":
                        volume = min(100, volume + 5)
                    last_tick_time = current_time
        else:
            key_hold_time = 0

        mouse_pos = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # 볼륨 바 근처를 클릭하면 드래그로 볼륨을 조절할 수 있다.
                drag_rect = pygame.Rect(
                    VOLUME_BAR_RECT.x,
                    VOLUME_BAR_RECT.y - 5,
                    VOLUME_BAR_RECT.width + 10,
                    VOLUME_BAR_RECT.height + 10,
                )
                if VOLUME_BAR_RECT.collidepoint(mouse_pos) or drag_rect.collidepoint(mouse_pos):
                    volume_dragging = True
                    selected_index = 0

            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                volume_dragging = False

            if event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT and pressed_direction == "LEFT":
                    pressed_direction = None
                elif event.key == pygame.K_RIGHT and pressed_direction == "RIGHT":
                    pressed_direction = None

            if event.type == pygame.KEYDOWN:
                if confirm_mode:
                    # 난이도 변경 후 다른 줄로 이동하려 할 때 적용/취소를 먼저 묻는다.
                    if event.key == pygame.K_RETURN:
                        # 승낙
                        diff_index = temp_diff_index
                        confirm_mode = False
                        if pending_direction == "UP":
                            selected_index = previous_menu_index(selected_index, menu_items)
                        elif pending_direction == "DOWN":
                            selected_index = next_menu_index(selected_index, menu_items)
                    elif event.key == pygame.K_ESCAPE:
                        # 거절
                        temp_diff_index = diff_index
                        confirm_mode = False
                        if pending_direction == "UP":
                            selected_index = previous_menu_index(selected_index, menu_items)
                        elif pending_direction == "DOWN":
                            selected_index = next_menu_index(selected_index, menu_items)
                    continue

                if typing_mode:
                    # 닉네임 입력 모드에서는 이동키 대신 문자 입력을 우선 처리한다.
                    if event.key == pygame.K_RETURN:
                        typing_mode = False
                    elif event.key == pygame.K_BACKSPACE:
                        nickname = nickname[:-1]
                    elif len(nickname) < 15 and event.unicode.isalnum():
                        nickname += event.unicode
                    continue

                if event.key == pygame.K_ESCAPE:
                    menu_running = False

                # 위/아래 이동 시, 난이도 변경사항이 있으면 다른 옵션 가기 전에 팝업 발생
                elif event.key == pygame.K_UP:
                    if selected_index == 1 and diff_index != temp_diff_index:
                        confirm_mode = True
                        pending_direction = "UP"
                    else:
                        selected_index = previous_menu_index(selected_index, menu_items)

                elif event.key == pygame.K_DOWN:
                    if selected_index == 1 and diff_index != temp_diff_index:
                        confirm_mode = True
                        pending_direction = "DOWN"
                    else:
                        selected_index = next_menu_index(selected_index, menu_items)

                elif event.key == pygame.K_LEFT:
                    # 왼쪽 키는 현재 선택된 항목의 값을 줄이거나 이전 선택지로 이동한다.
                    if selected_index == 0:
                        volume = max(0, volume - 5)
                        pressed_direction = "LEFT"
                        key_hold_time = 0
                        last_tick_time = pygame.time.get_ticks()
                    elif selected_index == 1:
                        temp_diff_index = (temp_diff_index - 1) % len(difficulties)
                    elif selected_index == 3:
                        size_index = (size_index - 1) % len(screen_sizes)
                        SCREEN_WIDTH, SCREEN_HEIGHT = screen_sizes[size_index]
                        apply_screen_mode()
                    elif selected_index == 4:
                        is_fullscreen = not is_fullscreen
                        apply_screen_mode()

                elif event.key == pygame.K_RIGHT:
                    # 오른쪽 키는 현재 선택된 항목의 값을 늘리거나 다음 선택지로 이동한다.
                    if selected_index == 0:
                        volume = min(100, volume + 5)
                        pressed_direction = "RIGHT"
                        key_hold_time = 0
                        last_tick_time = pygame.time.get_ticks()
                    elif selected_index == 1:
                        temp_diff_index = (temp_diff_index + 1) % len(difficulties)
                    elif selected_index == 3:
                        size_index = (size_index + 1) % len(screen_sizes)
                        SCREEN_WIDTH, SCREEN_HEIGHT = screen_sizes[size_index]
                        apply_screen_mode()
                    elif selected_index == 4:
                        is_fullscreen = not is_fullscreen
                        apply_screen_mode()

                elif event.key == pygame.K_RETURN:
                    # ENTER는 하위 메뉴 진입, 재시작, 종료처럼 명령형 항목을 실행한다.
                    if selected_index == 7:
                        typing_mode = True
                    elif selected_index == 2:
                        show_character_setting_menu()
                    elif selected_index == 5:
                        menu_running = False
                    elif selected_index == 6:
                        pygame.quit()
                        sys.exit()

        if volume_dragging:
            # 마우스 x좌표를 볼륨 바 길이에 맞춰 0~100 사이 볼륨으로 변환한다.
            relative_x = mouse_pos[0] - VOLUME_BAR_RECT.x
            relative_x = max(0, min(relative_x, VOLUME_BAR_RECT.width))
            volume = int((relative_x / VOLUME_BAR_RECT.width) * 100)


# --- 메인 게임 인게임 루프 ---
running = True
def _settings_menu(clock, difficulty):
    """예전 테스트용 인게임 설정 루프. 현재 실제 게임 루프에서는 거의 쓰지 않는다."""
    global running
    while running:
        current_game_color = color_map[char_colors[current_color_idx]]
        screen.fill(current_game_color)

        draw_text("KIRBY GAME PLAYING...", font, BLACK, screen, 50, 50)
        draw_text("Press 'ESC' for Advanced Settings Menu", font, GRAY, screen, 50, 100)
        draw_text(f"Kirby Name: {nickname}", font, BLACK, screen, 50, 300)
        draw_text(f"Costume Equipped: {costumes[current_costume_idx]}", font, BLACK, screen, 50, 350)
        draw_text(f"System Volume: {volume}% | Difficulty: {difficulties[diff_index]}", font, BLACK, screen, 50, 400)

        pygame.display.flip()
        clock.tick(FPS)
