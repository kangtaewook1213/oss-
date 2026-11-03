# Health Log

날짜별로 식단·운동 칼로리, 인바디 수치, 할 일을 기록하고 주간 리포트로 돌아볼 수 있는 Python 데스크톱 건강 기록 프로그램입니다.
달력에서 날짜를 선택하면 그날의 기록 화면을 열 수 있습니다.


## 주요 기능

| 기능 | 설명 | 상태 |
|------|------|------|
| 달력 | 월 단위 달력, ◀ ▶ 로 월 이동, 오늘 날짜 강조 | 완료 |
| 칼로리 기록 | 식단(섭취)/운동(소모) 입력, 조회·수정·삭제, 일일 합계 계산 | 완료 |
| 할 일 | 날짜별 할 일 입력 및 완료 관리 | 완료 <!-- 확인: 실제 구현 범위에 맞게 수정 --> |
| 인바디 트래커 | 키, 체중, 골격근량, 체지방률 입력 및 저장 | 완료 (저장만 지원) |
| 주간 리포트 | 주간 칼로리 요약, 요일별 표, 할 일 완료율, 미완료 목록 | 완료 |

### 칼로리 기록
- 구분(식단/운동), 기록 이름, 칼로리(kcal)를 입력해 저장합니다.
- 선택한 날짜의 기록을 표로 조회하고, 선택해서 수정하거나 삭제할 수 있습니다.
- 하루 총 섭취, 총 소모, 순 칼로리(섭취 - 소모)를 계산합니다.

### 할 일
- 선택한 날짜에 할 일을 등록하고 완료 여부를 관리합니다. 
- 저장된 할 일은 주간 리포트의 완료율과 미완료 목록에 반영됩니다.

### 인바디 트래커
- 입력값 검사 범위: 키 50~250 cm, 체중 10~500 kg, 체지방률 0~100 %
- 골격근량은 0 이상이며 체중보다 클 수 없습니다.

### 주간 리포트
- 선택한 날짜가 속한 주(일요일~토요일)를 집계합니다.
- 주간 섭취/소모/순 칼로리와 요일별 내역을 보여줍니다.
- 할 일 완료율과 미완료 항목을 보여줍니다.
- 한 주의 시작 요일은 `weekly_summary.py`의 `WEEK_START`로 바꿀 수 있습니다. (`"SUN"` 또는 `"MON"`)

## 실행 방법

### 요구 사항
- Python 3.8 이상 권장
- 별도 패키지 설치 없음 (표준 라이브러리 `tkinter`, `csv`, `datetime`만 사용)

> Linux에서 `tkinter`가 없다면 `sudo apt install python3-tk`로 설치하세요.

### 실행
```bash
git clone https://github.com/<조직또는아이디>/<저장소>.git
cd <저장소>
python main.py
```

1. 달력이 열리면 원하는 날짜를 클릭합니다.
2. 상세 화면에서 `칼로리 입력`, `할 일 입력`, `인바디 트래커`, `주간 리포트` 중 원하는 기능을 선택합니다.

첫 실행 시 `data/` 폴더와 CSV 파일이 헤더와 함께 자동으로 생성됩니다.

## 프로젝트 구조

```
.
├── main.py              # 실행 진입점, 달력 화면, 날짜 상세 화면
├── config.py            # 데이터 경로, CSV 헤더, 데이터 파일 초기화
├── calorie_diary.py     # 칼로리 기록 (입력, 조회, 수정, 삭제, 일일 계산)
├── daily_todo.py        # 날짜별 할 일 기록
├── body_tracker.py      # 인바디 수치 입력 및 저장
├── weekly_summary.py    # 주간 집계 및 리포트 화면
└── data/                # 실행 시 자동 생성되는 사용자 데이터
    ├── calories.csv
    ├── body_tracker.csv
    └── todo.csv
```

## 데이터 저장 형식

모든 기록은 `data/` 폴더의 CSV 파일에 저장됩니다. 경로와 헤더는 `config.py`에서 한곳으로 관리합니다.

| 파일 | 컬럼 |
|------|------|
| `calories.csv` | `id, date, type, name, kcal` (`type`: `intake` / `burn`) |
| `todo.csv` | `id, date, title, done` (`done`: `true` / `false`) |
| `body_tracker.csv` | `id, date, height_cm, weight_kg, skeletal_muscle_mass_kg, body_fat_percentage` |

날짜 형식은 `YYYY-MM-DD`입니다.

## 개발 가이드

- 데이터 경로나 CSV 헤더가 필요한 모듈은 새로 만들지 말고 `config.py`에서 import합니다.
  ```python
  from config import CALORIE_CSV, TODO_CSV
  ```
- 각 기능 화면은 `show_xxx(parent, selected_date)` 형태의 함수로 제공하고, `main.py`에서 연결합니다.
- 화면 코드와 CSV 처리·계산 코드는 가능한 한 함수로 분리해 테스트하기 쉽게 유지합니다.

## 기여하기

기여를 환영합니다! 처음이라면 [`good first issue`](https://github.com/kangtaewook1213/oss-/issues/64), (https://github.com/kangtaewook1213/oss-/issues/65) 라벨이 붙은 이슈부터 시작해 보세요.

1. 저장소를 Fork합니다.
2. 브랜치를 만듭니다. 
3. 변경 사항을 커밋합니다.
4. Push 후 Pull Request를 엽니다.

PR에는 관련 이슈 번호와 변경 전/후 스크린샷(UI 변경 시)을 함께 적어 주세요.

## 로드맵

- [ ] 인바디 기록 조회·수정·삭제 및 변화 추이 표시
- [ ] 주간 리포트에 인바디 변화 추가
- [ ] 단위 테스트 추가

## 라이선스
MIT License 
