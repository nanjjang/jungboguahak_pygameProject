# PNG 로드 에러 해결 기록 (with Claude)

> 작성일: 2026-06-13

## 증상

`python3 main.py` 실행 시 다음 에러로 크래시:

```
Traceback (most recent call last):
  File ".../game/main.py", line 14, in main
    player = Kirby(x=100, y=600)
  File ".../game/src/kirby.py", line 28, in loadMove
    self.kirby1 = load.load_image("Kirby1.png")
  File ".../game/load.py", line 5, in load_image
    image = pygame.image.load(path)
pygame.error: File is not a Windows BMP file
```

- 목요일(6/11)까지는 잘 작동했음.
- 코드는 전혀 바뀌지 않았는데 갑자기 PNG 로드에서 실패.

## 원인

크래시는 **코드나 이미지 파일의 문제가 아니었음.** `Kirby1.png`는 정상적인 PNG 파일(26×26 RGBA).

진짜 원인은 설치된 **pygame에 SDL_image 지원이 빠져 있던 것**:

```python
pygame.image.get_extended()   # → False
```

- `pygame.image.get_extended()`가 `False`면 pygame은 **BMP 파일만** 읽을 수 있음.
- 그래서 PNG를 넘기면 "File is not a Windows BMP file"라는 (오해를 부르는) 에러가 발생.

### SDL / SDL_image 란?

- **SDL (Simple DirectMedia Layer)**: pygame이 내부적으로 쓰는 저수준 라이브러리. 창 띄우기, 키보드/마우스 입력, 소리, 화면 그리기 등을 담당. pygame은 이 SDL을 파이썬에서 쉽게 쓰도록 감싼 래퍼.
- **SDL_image**: PNG·JPG 같은 다양한 이미지 포맷을 읽게 해주는 **확장** 라이브러리. 이게 없으면 SDL 본체는 BMP만 읽음.
- `get_extended() == True` 라는 건 SDL_image가 함께 설치돼 있다는 뜻.

### 왜 목요일엔 됐고 지금은 안 됐나

- `game/venv` 가상환경이 **오늘(6/13) 13:53에 새로 생성**됨. pygame 2.6.1도 13:54에 설치됨.
- 목요일엔 다른 환경(이전 venv 또는 프레임워크 Python)에서 실행했고, 거기엔 SDL_image가 정상적으로 포함돼 있었음.
- 오늘 새 venv를 만들면서 `pip install pygame`으로 설치한 **Python 3.14용 pygame 2.6.1 휠에 SDL_image가 빠져 있었음** (venv 안에 SDL_image dylib 파일 자체가 없음).
- 결론: 코드는 그대로고, **환경만 새로 깔리면서 깨진 것**. Python 3.14가 매우 최신 버전이라 패키징 문제가 있었음.

## 해결

`pygame`을 `pygame-ce`(커뮤니티 에디션)로 교체. `import pygame` API가 동일한 드롭인 교체본이며, Python 3.14용 휠에 SDL_image가 제대로 포함돼 있음.

```bash
# venv 활성화 상태에서
pip uninstall pygame
pip install pygame-ce
```

확인:

```python
import pygame
print(pygame.ver)                  # pygame-ce 2.5.7
print(pygame.image.get_extended()) # True
```

`extended: True`가 되면 PNG 로드 정상 작동.

## 정리 / 예방

- 앞으로 `pip install pygame` 대신 **`pip install pygame-ce`** 를 사용하면 같은 문제를 피할 수 있음.
- pygame 관련 에러가 PNG/JPG 로드에서 날 때는 먼저 `pygame.image.get_extended()` 를 확인할 것. `False`면 SDL_image 문제.
- 실행 환경(venv)과 패키지를 설치하는 환경이 같은지 항상 확인. (이번엔 프레임워크 Python과 venv 두 군데 모두 교체함.)

---

# 한글 폰트 깨짐 & 한국어 키보드 입력 불가 해결 기록 (with Claude)

> 작성일: 2026-06-13

---

## 문제 1: 한글 폰트 깨짐

### 증상

`pygame.font.SysFont(None, size)`로 폰트를 생성하면 한글이 깨져서 표시됨 (□□□ 또는 물음표).

### 원인

`SysFont(None, size)`는 pygame 기본 폰트를 사용하는데, 이 폰트는 한글을 지원하지 않음.

### 잘못된 해결 시도

```python
font_list = ["malgun gothic", "AppleGothic", "NanumGothic", "Gulim"]
font_found = False

for font_name in font_list:
    try:
        my_font = pygame.font.SysFont(font_name, 40)
        font_found = True
        break
    except:
        continue
```

`SysFont()`는 존재하지 않는 폰트 이름을 넘겨도 **예외를 발생시키지 않고** 기본 폰트를 반환함.
따라서 `try/except`로는 폰트 존재 여부를 판별할 수 없어 `font_found`가 항상 `True`가 됨.

### 올바른 해결

`pygame.font.match_font(name)`으로 시스템에 폰트가 존재하는지 먼저 확인.

```python
# load.py
_KOREAN_FONT_CANDIDATES = ["applegothic", "malgun gothic", "nanumgothic", "gulim", "dotum"]

def get_korean_font(size):
    for name in _KOREAN_FONT_CANDIDATES:
        if pygame.font.match_font(name):   # 실제 존재 여부 확인
            return pygame.font.SysFont(name, size)
    return pygame.font.Font(None, size)    # 없으면 기본 폰트
```

추가로, 폰트 객체를 `draw_hud()` 같은 매 프레임 호출 함수 안에서 생성하면 성능이 낭비됨.
초기화 시 한 번만 만들어 `self.font`에 캐시해서 재사용.

```python
# kirby.py __init__
self.font = load.get_korean_font(18)  # 초기화 시 1회 생성
```

### 우선순위 목록

| 폰트 이름 | 지원 OS |
|---|---|
| applegothic | macOS |
| malgun gothic | Windows |
| nanumgothic | Linux / 나눔폰트 설치 시 |
| gulim / dotum | Windows (구버전) |

---

_## 문제 2: 한국어 키보드 입력 시 게임 키 입력 불가

### 증상

macOS에서 키보드 입력 방식을 한국어로 설정해두면 Z, X, C, Space 등 게임 키가 전혀 반응하지 않음.

### 원인

macOS의 한국어 IME(입력기)가 활성화된 상태에서는 키 입력이 IME에 먼저 전달되어 한글 문자 조합에 사용됨.
이 과정에서 키 입력이 `KEYDOWN` 이벤트나 `get_pressed()` 대신 `TEXTINPUT` 이벤트로 변환되어 pygame에 전달되지 않음.

### 해결

게임 시작 시 `pg.key.stop_text_input()`을 한 번 호출해서 IME가 키를 가로채지 못하게 함.

```python
# main.py
def main():
    pg.init()
    pg.key.stop_text_input()  # 한국어 IME가 키 입력을 가로채지 않도록
    ...
```

게임 중에는 텍스트 입력이 필요 없으므로 부작용 없음.

### 주의

`pg.init()` **이후**에 호출해야 함. 초기화 전에 호출하면 효과 없음._
