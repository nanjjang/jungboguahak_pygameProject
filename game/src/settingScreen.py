# 게임 중 ESC로 들어가는 설정 메뉴와 캐릭터 설정 메뉴.

import pygame as pg
import load
from src.constants import (
    FPS,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
)
from src.warningMessage import show_popup
from src import sfx

screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pg.time.Clock()



WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
PINK = (255, 182, 193)
GRAY = (100, 100, 100)
YELLOW = (255, 215, 0)
DARK_GRAY = (40, 40, 40)
BLUE = (100, 149, 237)
GREEN = (60, 179, 113)


font = load.get_korean_font(22)
title_font = load.get_korean_font(36)

volume = 100
difficulties = ["Easy", "Normal", "Hard"]
DIFFICULTY_VALUES = ["easy", "normal", "hard"]
diff_index = 1
temp_diff_index = 1  

nickname = "Kirby_Fan"
screen_sizes = [(1000, 600), (1024, 768), (1280, 720)]
size_index = 0
is_fullscreen = False


char_colors = ["Pink", "Yellow", "Blue", "Green"]
color_map = {"Pink": PINK, "Yellow": YELLOW, "Blue": BLUE, "Green": GREEN}
costumes = ["None", "Sword", "Fire", "Beam"]

current_color_idx = 0
current_costume_idx = 0


typing_mode = False
confirm_mode = False      
pending_direction = None  


volume_dragging = False
VOLUME_BAR_RECT = pg.Rect(650, 110, 200, 15)


key_hold_time = 0       
last_tick_time = 0      
pressed_direction = None


def draw_text(text, font, color, surface, x, y):
    text_obj = font.render(text, True, color)
    text_rect = text_obj.get_rect()
    text_rect.topleft = (x, y)
    surface.blit(text_obj, text_rect)


def previous_menu_index(selected_index, menu_items):
    nickname_index = len(menu_items)
    if selected_index == nickname_index:
        return len(menu_items) - 1
    if selected_index == 0:
        return nickname_index
    return selected_index - 1


def next_menu_index(selected_index, menu_items):
    nickname_index = len(menu_items)
    if selected_index == nickname_index:
        return 0
    if selected_index == len(menu_items) - 1:
        return nickname_index
    return selected_index + 1


def move_pending_direction(selected_index, menu_items, pending_direction):
    if pending_direction == "UP":
        return previous_menu_index(selected_index, menu_items)
    if pending_direction == "DOWN":
        return next_menu_index(selected_index, menu_items)
    return selected_index


def apply_screen_mode():
    global screen

    flags = 0
    if is_fullscreen:
        flags = pg.FULLSCREEN
    screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), flags)


def set_current_difficulty(difficulty):
    global diff_index, temp_diff_index
    if difficulty in DIFFICULTY_VALUES:
        diff_index = DIFFICULTY_VALUES.index(difficulty)
        temp_diff_index = diff_index


def current_difficulty():
    return DIFFICULTY_VALUES[diff_index]


def change_volume(amount):
    global volume
    volume = max(0, min(100, volume + amount))


def change_temp_difficulty(amount):
    global temp_diff_index
    temp_diff_index = (temp_diff_index + amount) % len(difficulties)


def change_screen_size(amount):
    global size_index, SCREEN_WIDTH, SCREEN_HEIGHT
    size_index = (size_index + amount) % len(screen_sizes)
    SCREEN_WIDTH, SCREEN_HEIGHT = screen_sizes[size_index]
    apply_screen_mode()


def toggle_screen_type():
    global is_fullscreen
    is_fullscreen = not is_fullscreen
    apply_screen_mode()


def show_character_setting_menu():
    return show_popup(screen, "현재 개발 중에 있는 기능입니다! \n v2.0 업데이트를 기달려주세요!")


# ====================================================
# 설정 메뉴
# ====================================================
def show_settings_menu(current_game_difficulty=None):
    # 설정 화면 전체
    global volume, diff_index, temp_diff_index, nickname
    global typing_mode, confirm_mode, volume_dragging, pending_direction
    global key_hold_time, last_tick_time, pressed_direction

    if current_game_difficulty is not None:
        set_current_difficulty(current_game_difficulty)

    typing_mode = False
    confirm_mode = False
    pending_direction = None
    volume_dragging = False
    pressed_direction = None
    key_hold_time = 0
    last_tick_time = 0

    result = {
        "difficulty": None,
        "restart_requested": False,
        "quit_requested": False,
    }

    menu_items = [
        "볼륨 바 (Volume)",
        "난이도 (Difficulty)",
        "캐릭터 세팅 (Character Settings)",
        "화면 크기 (Screen Size)",
        "화면 타입 (Screen Type)",
        "재시작 (Restart)",
        "게임 종료 (Exit)"
    ]
    nickname_index = len(menu_items)
    selected_index = 1

    temp_diff_index = diff_index

    menu_running = True
    while menu_running:
        dt = clock.tick(30)
        sfx.set_user_volume(volume)
        screen.fill(BLACK)

        # 타이틀
        draw_text("SETTINGS MENU (ESC to Return)", title_font, PINK, screen, 50, 30)

        # 왼쪽 미리보기
        box_x, box_y, box_w, box_h = 80, 220, 160, 160
        kirby_color = color_map[char_colors[current_color_idx]]
        pg.draw.rect(screen, kirby_color, (box_x, box_y, box_w, box_h))
        pg.draw.rect(screen, WHITE, (box_x, box_y, box_w, box_h), 3) 
        draw_text(f"[{costumes[current_costume_idx]}]", font, BLACK, screen, box_x + 35, box_y + 65)

        if selected_index == nickname_index:
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

        # 오른쪽 메뉴
        for i, item in enumerate(menu_items):
            # 현재 줄 표시
            color = YELLOW if i == selected_index else WHITE

            val_text = ""
            if i == 0:
                val_text = f"{volume}%"
            elif i == 1:
                val_text = f"< {difficulties[temp_diff_index]} >"
            elif i in (2, 5, 6):
                val_text = "(Press Enter)"
            elif i == 3:
                val_text = f"< {screen_sizes[size_index][0]}x{screen_sizes[size_index][1]} >"
            elif i == 4:
                if is_fullscreen:
                    val_text = "< Fullscreen >"
                else:
                    val_text = "< Windowed >"

            draw_text(item, font, color, screen, 320, 100 + i * 55)

            if i != 0:
                draw_text(val_text, font, color, screen, 800, 100 + i * 55)

        # ==========================================
        # 볼륨 슬라이더
        # ==========================================
        pg.draw.rect(screen, GRAY, VOLUME_BAR_RECT) 
        filled_width = int(VOLUME_BAR_RECT.width * (volume / 100))
        pg.draw.rect(screen, PINK, (VOLUME_BAR_RECT.x, VOLUME_BAR_RECT.y, filled_width, VOLUME_BAR_RECT.height))
        handle_x = VOLUME_BAR_RECT.x + filled_width
        handle_y = VOLUME_BAR_RECT.y + VOLUME_BAR_RECT.height // 2
        if selected_index == 0:
            handle_color = YELLOW
        else:
            handle_color = WHITE
        pg.draw.circle(screen, handle_color, (handle_x, handle_y), 8)

        draw_text(
            f"{volume}%",
            font,
            handle_color,
            screen,
            VOLUME_BAR_RECT.x + VOLUME_BAR_RECT.width + 15,
            VOLUME_BAR_RECT.y - 5,
        )

        # 난이도 확인창
        if confirm_mode:
            popup_rect = pg.Rect(
                SCREEN_WIDTH // 2 - 210,
                SCREEN_HEIGHT // 2 - 80,
                500,
                150,
            )
            pg.draw.rect(screen, DARK_GRAY, popup_rect)
            pg.draw.rect(screen, PINK, popup_rect, 3)
            draw_text(
                "난이도 변경 사항을 적용하시겠습니까?",
                font,
                WHITE,
                screen,
                SCREEN_WIDTH // 2 - 160,
                SCREEN_HEIGHT // 2 - 40,
            )
            draw_text(
                "[Enter] 동의(적용)  /  [ESC] 거절(취소)",
                font,
                YELLOW,
                screen,
                SCREEN_WIDTH // 2 - 160,
                SCREEN_HEIGHT // 2 + 10,
            )

        pg.display.flip()

        if selected_index == 0 and pressed_direction is not None and not typing_mode:
            # 꾹 누르면 계속 조절
            key_hold_time += dt
            if key_hold_time >= 600:
                current_time = pg.time.get_ticks()
                if current_time - last_tick_time >= 100:
                    if pressed_direction == "LEFT":
                        change_volume(-5)
                    elif pressed_direction == "RIGHT":
                        change_volume(5)
                    last_tick_time = current_time
        else:
            key_hold_time = 0

        mouse_pos = pg.mouse.get_pos()
        for event in pg.event.get():
            if event.type == pg.QUIT:
                result["quit_requested"] = True
                return result

            if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                # 볼륨 드래그
                drag_rect = pg.Rect(
                    VOLUME_BAR_RECT.x,
                    VOLUME_BAR_RECT.y - 5,
                    VOLUME_BAR_RECT.width + 10,
                    VOLUME_BAR_RECT.height + 10,
                )
                if VOLUME_BAR_RECT.collidepoint(mouse_pos) or drag_rect.collidepoint(mouse_pos):
                    volume_dragging = True
                    selected_index = 0

            if event.type == pg.MOUSEBUTTONUP and event.button == 1:
                volume_dragging = False

            if event.type == pg.KEYUP:
                if event.key == pg.K_LEFT and pressed_direction == "LEFT":
                    pressed_direction = None
                elif event.key == pg.K_RIGHT and pressed_direction == "RIGHT":
                    pressed_direction = None

            if event.type == pg.KEYDOWN:
                if confirm_mode:
                    # 확인창
                    if event.key == pg.K_RETURN:
                        # 적용
                        diff_index = temp_diff_index
                        result["difficulty"] = current_difficulty()
                        confirm_mode = False
                    elif event.key == pg.K_ESCAPE:
                        # 취소
                        temp_diff_index = diff_index
                        confirm_mode = False
                    else:
                        continue
                    selected_index = move_pending_direction(selected_index, menu_items, pending_direction)
                    pending_direction = None
                    continue

                if typing_mode:
                    # 닉네임 입력
                    if event.key == pg.K_RETURN:
                        typing_mode = False
                    elif event.key == pg.K_BACKSPACE:
                        nickname = nickname[:-1]
                    elif len(nickname) < 15 and event.unicode.isalnum():
                        nickname += event.unicode
                    continue

                if event.key == pg.K_ESCAPE:
                    menu_running = False

                # 난이도 확인
                elif event.key == pg.K_UP:
                    if selected_index == 1 and diff_index != temp_diff_index:
                        confirm_mode = True
                        pending_direction = "UP"
                    else:
                        selected_index = previous_menu_index(selected_index, menu_items)

                elif event.key == pg.K_DOWN:
                    if selected_index == 1 and diff_index != temp_diff_index:
                        confirm_mode = True
                        pending_direction = "DOWN"
                    else:
                        selected_index = next_menu_index(selected_index, menu_items)

                elif event.key == pg.K_LEFT:
                    if selected_index == 0:
                        change_volume(-5)
                        pressed_direction = "LEFT"
                        key_hold_time = 0
                        last_tick_time = pg.time.get_ticks()
                    elif selected_index == 1:
                        change_temp_difficulty(-1)
                    elif selected_index == 3:
                        change_screen_size(-1)
                    elif selected_index == 4:
                        toggle_screen_type()

                elif event.key == pg.K_RIGHT:
                    # 오른쪽 키
                    if selected_index == 0:
                        change_volume(5)
                        pressed_direction = "RIGHT"
                        key_hold_time = 0
                        last_tick_time = pg.time.get_ticks()
                    elif selected_index == 1:
                        change_temp_difficulty(1)
                    elif selected_index == 3:
                        change_screen_size(1)
                    elif selected_index == 4:
                        toggle_screen_type()

                elif event.key == pg.K_RETURN:
                    if selected_index == nickname_index:
                        typing_mode = True
                    elif selected_index == 1:
                        diff_index = temp_diff_index
                        result["difficulty"] = current_difficulty()
                    elif selected_index == 2:
                        if not show_character_setting_menu():
                            result["quit_requested"] = True
                            menu_running = False
                    elif selected_index == 5:
                        result["restart_requested"] = True
                        menu_running = False
                    elif selected_index == 6:
                        result["quit_requested"] = True
                        menu_running = False

        if volume_dragging:
            # 드래그한 위치로 볼륨 맞춤
            relative_x = mouse_pos[0] - VOLUME_BAR_RECT.x
            relative_x = max(0, min(relative_x, VOLUME_BAR_RECT.width))
            volume = int((relative_x / VOLUME_BAR_RECT.width) * 100)

    return result


# --- 테스트용 인게임 루프 ---
running = True
def _settings_menu(clock, difficulty):
    # 예전 테스트용 루프
    global running
    while running:
        current_game_color = color_map[char_colors[current_color_idx]]
        screen.fill(current_game_color)

        draw_text("KIRBY GAME PLAYING...", font, BLACK, screen, 50, 50)
        draw_text("Press 'ESC' for Advanced Settings Menu", font, GRAY, screen, 50, 100)
        draw_text(f"Kirby Name: {nickname}", font, BLACK, screen, 50, 300)
        draw_text(f"Costume Equipped: {costumes[current_costume_idx]}", font, BLACK, screen, 50, 350)
        draw_text(f"System Volume: {volume}% | Difficulty: {difficulties[diff_index]}", font, BLACK, screen, 50, 400)

        pg.display.flip()
        clock.tick(FPS)
