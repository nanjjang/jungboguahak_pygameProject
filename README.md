# Pygame 프로젝트<br>팀명 : 지연쌤팬클럽 

Pygame으로 만든 Kirby 스타일 액션 게임입니다.

## 개발 환경
- OS: macOS & Window

## 실행 환경

- Python 3.14.3에서 실행 확인
- pygame-ce 2.5.7 사용

## 설치 및 실행 방법

프로젝트 루트에서 아래 명령어를 순서대로 실행합니다.

```bash 
# macOS
cd .../"프로젝트 폴더 이름"

python3 -m venv .venv
source .venv/bin/activate

python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt

python3 game/main.py
```
```bash 
# Windows
cd .../"프로젝트 폴더 이름"

python -m venv .venv
venv\Scripts\activate.bat

python -m pip install --upgrade pip
python -m pip install -r requirements.txt

python game/main.py
```

가상환경이 켜지면 터미널 앞에 `(.venv)`가 표시됩니다.

게임을 종료한 뒤 가상환경을 끄려면 아래 명령어를 실행합니다.

```bash
deactivate
```

## 조작 방법

| 키 | 동작 |
| --- | --- |
| `↑` / `↓` | 메뉴 선택 |
| `ENTER` | 메뉴 결정 |
| `ESC` | 설정 |
| `Q` | 종료 |
| `←` / `→` | 이동 |
| `SPACE` | 점프 |
| `SHIFT` + `SPACE` | 공중 유지 |
| `Z` | 흡입 |
| `X` | 발사 |
| `↓` | 삼키기 |
| `D` / `F` | 펀치 / 킥 |
| `V` | 능력 공격 |
| 문 앞에서 `↑` | 다음 스테이지 이동 |
| `R` | 게임오버/클리어 후 다시 시작 |

## 참고

- 의존성은 `requirements.txt` 확인부탁드립니다.