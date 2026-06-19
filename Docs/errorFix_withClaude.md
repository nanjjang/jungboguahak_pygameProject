# 에러 해결 일지.


> 6월 11일
## 문제점

`python3 main.py` 실행 시 다음 에러로 실행이 안됏음 ㅜㅜ:

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

- 목요일(6/11)까지는 잘 작동했는데..?? 갑자기 이랬음
- 코드는 전혀 바뀌지 않았는데 갑자기 PNG 로드에서 실패.

## 원인

코드나 이미지 파일의 문제가 아니었던것.....

진짜 원인은 설치된 pygame에 SDL_image 지원이 빠져 있었더라는 거!!!!!

```python
pygame.image.get_extended()   # → False
```

- `pygame.image.get_extended()`가 `False`면 pygame은 BMP 파일만 읽을 수 있음.
그래서? PNG를 넘기면 "File is not a Windows BMP file"라는 에러가 발생.

### SDL / SDL_image 란? -> 인터넷 검색.

- **SDL (Simple DirectMedia Layer)**: pygame이 내부적으로 쓰는 저수준 라이브러리. 창 띄우기, 키보드/마우스 입력, 소리, 화면 그리기 등을 담당. pygame은 이 SDL을 파이썬에서 쉽게 쓰도록 감싼 래퍼.
- **SDL_image**: PNG·JPG 같은 다양한 이미지 포맷을 읽게 해주는 확장 라이브러리. 이게 없으면 SDL은 BMP만 읽을 수 있음.
- `get_extended() == True` 라는 건 SDL_image가 함께 설치돼 있다는 뜻임.

## 해결한 방법은?

`pygame`을 `pygame-ce`(커뮤니티 에디션)로 교체. `import pygame` API가 동일함 -> pygame-ce라고 안해도 되는게 신기방기.

---

# 한글 폰트 깨짐 & 한국어 키보드 입력 불가 해결 기록

> 작성일: 2026-06-13

---

## 문제 1: 한글 폰트 깨짐

### 증상

`pygame.font.SysFont(None, size)`로 폰트를 생성하면 한글이 깨져서 표시됨 (□□□ 또는 물음표).

### 원인

`SysFont(None, size)`는 pygame 기본 폰트를 사용하는데, 이 폰트는 한글을 지원하지 않음.

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


### codex가 이상하게 해결함. 그니까 잘못 해결함
  ```markdown
  ![내 사진](./gpt's_wrong.png)
  ```

---

```html
<img src="./gpt's_wrong.png" width="400">
```

### + 윤준서의 실수
하드코딩을 박아서 
