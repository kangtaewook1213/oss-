"""프로젝트 공용 설정: 데이터 경로와 CSV 헤더를 정의한다.

모든 모듈은 BASE_DIR 등을 새로 만들지 말고 이 파일에서 import해서 사용한다.
    from config import CALORIE_CSV, TODO_CSV
"""
import csv
import os

# config.py가 있는 폴더(프로젝트 루트) 기준 -> 어디서 실행해도 같은 경로
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
SAMPLE_DIR = os.path.join(DATA_DIR, "sample")

CALORIE_CSV = os.path.join(DATA_DIR, "calories.csv")
TODO_CSV = os.path.join(DATA_DIR, "todo.csv")

CALORIE_HEADER = ["id", "date", "type", "name", "kcal"]   # type: intake / burn
TODO_HEADER = ["id", "date", "title", "done"]             # done: true / false


def ensure_data_files():
    """data/ 폴더와 CSV 파일이 없으면 헤더 포함해서 생성한다.

    프로그램 시작 시(main) 한 번만 호출하면 된다.
    """
    os.makedirs(DATA_DIR, exist_ok=True)
    for path, header in ((CALORIE_CSV, CALORIE_HEADER), (TODO_CSV, TODO_HEADER)):
        if not os.path.exists(path):
            with open(path, "w", newline="", encoding="utf-8") as f:
                csv.writer(f).writerow(header)