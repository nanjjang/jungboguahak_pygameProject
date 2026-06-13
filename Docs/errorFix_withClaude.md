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
