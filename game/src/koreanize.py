import pygame
import time

class HangulInputBox(pygame.sprite.Sprite):
    '''
    pygame 내부에 사용되는 비쥬얼 컴포넌트로
    한글을 입력할 수 있는 박스이다.
    한글/영문 전환 토클키는 Left-Shift + Space 이다.
    한글 모드에서는 굵은 사각형 커서가 나타나고
    영문 모드에서는 가는 사각형 커서가 보인다.
    '''
    # 자음-초성/종성
    cons = {'r': 'ㄱ', 'R': 'ㄲ', 's': 'ㄴ', 'e': 'ㄷ', 'E': 'ㄸ', 'f': 'ㄹ', 'a': 'ㅁ', 'q': 'ㅂ', 'Q': 'ㅃ', 't': 'ㅅ',
            'T': 'ㅆ',
            'd': 'ㅇ', 'w': 'ㅈ', 'W': 'ㅉ', 'c': 'ㅊ', 'z': 'ㅋ', 'x': 'ㅌ', 'v': 'ㅍ', 'g': 'ㅎ'}
    # 모음-중성
    vowels = {'k': 'ㅏ', 'o': 'ㅐ', 'i': 'ㅑ', 'O': 'ㅒ', 'j': 'ㅓ', 'p': 'ㅔ', 'u': 'ㅕ', 'P': 'ㅖ', 'h': 'ㅗ', 'hk': 'ㅘ',
              'ho': 'ㅙ', 'hl': 'ㅚ',
              'y': 'ㅛ', 'n': 'ㅜ', 'nj': 'ㅝ', 'np': 'ㅞ', 'nl': 'ㅟ', 'b': 'ㅠ', 'm': 'ㅡ', 'ml': 'ㅢ', 'l': 'ㅣ'}
    # 자음-종성
    cons_double = {'rt': 'ㄳ', 'sw': 'ㄵ', 'sg': 'ㄶ', 'fr': 'ㄺ', 'fa': 'ㄻ', 'fq': 'ㄼ', 'ft': 'ㄽ', 'fx': 'ㄾ', 'fv': 'ㄿ',
                   'fg': 'ㅀ', 'qt': 'ㅄ'}

    def __init__(self, font:str, fontSize:int, width:int, fColor:str, bColor:str):
        pygame.sprite.Sprite.__init__(self)
        self.font = pygame.font.Font(font, fontSize)
        self.fontSize:int = fontSize
        self.width = width * self.fontSize
        self.height = fontSize
        self.fColor = pygame.Color(fColor)
        self.bColor = pygame.Color(bColor)

        self.image = pygame.Surface([self.width, self.height])
        self.rect = self.image.get_rect()

        self.text = '첫 글자'
        self.textImage = self.font.render(self.text, True, self.fColor)
        self.textRect = self.textImage.get_rect()
        self.hanText = ''
        self.hanMode = False

        self.cursor = pygame.Rect(self.textRect.topright, (3, self.fontSize))

        pygame.key.set_repeat(500, 50)

        self.enterEvent = pygame.event.Event(pygame.USEREVENT, {'name':'enterEvent', 'text':''})

    def update(self, event) -> None:
        if event == None: event = pygame.event.Event(pygame.USEREVENT,{})
        if event.type == pygame.KEYDOWN:  # 키다운 이벤트라면, key, mod, ucicode, scancode 속성을 가진다.
            if event.key == pygame.K_RETURN or event.key == pygame.K_CARET:
                text2 = self.text + HangulInputBox.engkor(self.hanText)
                self.enterEvent.text = text2
                pygame.event.post(self.enterEvent)
                self.text = ''
                self.hanText = ''
            elif event.key == pygame.K_BACKSPACE:
                if self.hanMode and len(self.hanText) > 0:
                    self.hanText = self.hanText[:-1]
                elif len(self.text) > 0:
                    self.text = self.text[:-1]
            elif event.mod & pygame.KMOD_LSHIFT and event.key == pygame.K_SPACE:  # 한영 변환 인식 Left Shift + space
                if self.hanMode:  # 영문모드로 토글
                    self.text += HangulInputBox.engkor(self.hanText)
                    self.cursor = pygame.Rect(self.textRect.topright, (3, self.fontSize))
                    self.hanMode = False
                else:  # 한글모드로 토클
                    self.cursor = pygame.Rect(self.textRect.topright, (16, self.fontSize))
                    self.hanMode = True
                self.hanText = ''
            else:
                if self.hanMode:
                    self.hanText += event.unicode
                else:
                    self.text += event.unicode
            #----------
            text2 = self.text + HangulInputBox.engkor(self.hanText)
            self.textImage = self.font.render(text2, True, 'white')
            self.textRect = self.textImage.get_rect()
            if self.textRect.width > self.rect.width:
                self.textRect.topright = (self.rect.width - self.fontSize, 0)
            else:
                self.textRect.topleft = (0,0)
            self.cursor.topleft = self.textRect.topright

        self.image.fill(self.bColor)
        self.image.blit(self.textImage, self.textRect)
        if time.time() % 1 > 0.5:
            pygame.draw.rect(self.image, 'red', self.cursor)

    @classmethod
    def engkor(cls, text):
        result = ''  # 영 > 한 변환 결과

        # 1. 해당 글자가 자음인지 모음인지 확인
        vc = ''
        for t in text:
            if t in cls.cons:
                vc += 'c'
            elif t in cls.vowels:
                vc += 'v'
            else:
                vc += '!'

        # cvv → fVV / cv → fv / cc → dd
        vc = vc.replace('cvv', 'fVV').replace('cv', 'fv').replace('cc', 'dd')

        # 2. 자음 / 모음 / 두글자 자음 에서 검색
        i = 0
        while i < len(text):
            v = vc[i]
            t = text[i]

            j = 1
            # 한글일 경우
            try:
                if v == 'f' or v == 'c':  # 초성(f) & 자음(c) = 자음
                    result += cls.cons[t]

                elif v == 'V':  # 더블 모음
                    result += cls.vowels[text[i:i + 2]]
                    j += 1

                elif v == 'v':  # 모음
                    result += cls.vowels[t]

                elif v == 'd':  # 더블 자음
                    result += cls.cons_double[text[i:i + 2]]
                    j += 1
                else:
                    result += t

            # 한글이 아닐 경우
            except:
                if v in cls.cons:
                    result += cls.cons[t]
                elif v in cls.vowels:
                    result += cls.vowels[t]
                else:
                    result += t

            i += j

        return join_jamos(result)

    # https://joyfulgenie.tistory.com/entry/pygame%EC%97%90%EC%84%9C-%ED%95%9C%EA%B8%80%EC%9E%85%EB%A0%A5-%EC%BB%B4%ED%8F%AC%EB%84%8C%ED%8A%B8-%EB%A7%8C%EB%93%A4%EA%B8%B0


# 한글 unicode → pygame 키 상수 역매핑 (cons/vowels 단일 영문자 기준)
KOREAN_TO_KEY = {}
for _eng, _kor in HangulInputBox.cons.items():
    if len(_eng) == 1 and hasattr(pygame, f'K_{_eng}'):
        KOREAN_TO_KEY[_kor] = getattr(pygame, f'K_{_eng}')
for _eng, _kor in HangulInputBox.vowels.items():
    if len(_eng) == 1 and hasattr(pygame, f'K_{_eng}'):
        KOREAN_TO_KEY[_kor] = getattr(pygame, f'K_{_eng}')