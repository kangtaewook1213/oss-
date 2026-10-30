# 데이터 저장 규약

> 논의 이슈: #(이슈 번호)
> 최종 수정: 2026-10-30

## 1. 저장 위치
- 프로젝트 `data/` 폴더 (코드 파일 기준 상대 경로)
- 경로는 `config.py`에서만 정의하고, 모든 모듈은 import해서 사용한다.
  (각 모듈에서 BASE_DIR을 새로 만들지 않는다)

## 2. 파일 구성

| 파일 | 용도 | 컬럼 |
|------|------|------|
| `data/calories.csv` | 칼로리 기록 | `id,date,type,name,kcal` |
| `data/todo.csv` | 할 일 기록 | `id,date,title,done` |

## 3. 컬럼 규칙

| 컬럼 | 형식 | 비고 |
|------|------|------|
| id | 정수 | 생성 방식은 아래 "미정 항목" 참고 |
| date | `YYYY-MM-DD` | 예: 2026-10-11 |
| type | `intake` / `burn` | 칼로리 파일만 |
| kcal | 정수 | |
| done | `true` / `false` | 할 일 파일만 |

## 4. 공통 규칙
- 구분자: 쉼표(`,`), 인코딩: UTF-8
- `data/` 폴더와 파일이 없으면 헤더 포함 자동 생성
- 읽을 때 파일이 없으면 빈 리스트 반환 (에러 내지 않음)

## 5. Git 처리
- 실제 데이터 `data/*.csv`는 `.gitignore`
- 샘플 `data/sample/`만 커밋

## 6. 예시

​```csv
id,date,type,name,kcal
1,2026-10-11,burn,전주 일요일 운동,200
​```

​```csv
id,date,title,done
1,2026-10-11,스트레칭,true
​```

