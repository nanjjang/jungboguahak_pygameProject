import pygame as pg
import load

font = load.get_korean_font(15)


def show_popup(screen, message):
    # 팝업창 크기 설정
    popup_width, popup_height = 300, 150
    screen_width, screen_height = screen.get_size()
    popup_x = (screen_width - popup_width) // 2
    popup_y = (screen_height - popup_height) // 2
    popup_rect = pg.Rect(popup_x, popup_y, popup_width, popup_height)

    waiting = True
    while waiting:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return False
            if event.type == pg.KEYDOWN:
                # 아무 키나 누르면 팝업 닫기
                waiting = False

        # 팝업창 배경 그리기 (흰색 박스 + 검은색 테두리)
        pg.draw.rect(screen, (255, 255, 255), popup_rect)
        pg.draw.rect(screen, (0, 0, 0), popup_rect, 3)

        # 텍스트 렌더링
        text_surface = font.render(message, True, (0, 0, 0))
        text_rect = text_surface.get_rect(center=popup_rect.center)

        # 화면에 텍스트 그리기
        screen.blit(text_surface, text_rect)

        pg.display.flip()
    return True
