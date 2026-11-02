
import csv
import os
from datetime import date, datetime, timedelta

from config import CALORIE_CSV, TODO_CSV

# 한 주의 시작 요일: "MON" = 월~일, "SUN" = 일~토
WEEK_START = "SUN"

WEEKDAY_KR = ["월", "화", "수", "목", "금", "토", "일"]  # date.weekday() 순서
TRUE_VALUES = ("1", "true", "y", "yes", "완료")


# ---------------------------------------------------------------
# 날짜 / 주 범위
# ---------------------------------------------------------------
def to_date(value):
    """'YYYY-MM-DD' 문자열 또는 date를 date로 변환"""
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    return datetime.strptime(str(value).strip(), "%Y-%m-%d").date()


def get_week_range(ref_date):
    """ref_date가 속한 주의 (시작일, 종료일) 반환. 기준은 WEEK_START."""
    ref_date = to_date(ref_date)
    if WEEK_START == "SUN":
        offset = (ref_date.weekday() + 1) % 7   # 일요일=0 ... 토요일=6
    else:
        offset = ref_date.weekday()             # 월요일=0 ... 일요일=6
    start = ref_date - timedelta(days=offset)
    return start, start + timedelta(days=6)


# ---------------------------------------------------------------
# CSV 읽기 (파일이 없으면 빈 리스트)
# ---------------------------------------------------------------
def load_calorie_records(path=CALORIE_CSV):
    if not os.path.exists(path):
        return []
    records = []
    with open(path, newline="", encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            try:
                records.append({
                    "date": to_date(row["date"]),
                    "type": row["type"].strip().lower(),
                    "name": row["name"],
                    "kcal": int(float(row["kcal"])),
                })
            except (ValueError, KeyError, TypeError, AttributeError):
                print(f"[건너뜀] 칼로리 행 오류: {row}")
    return records


def load_todo_records(path=TODO_CSV):
    if not os.path.exists(path):
        return []
    records = []
    with open(path, newline="", encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            try:
                records.append({
                    "date": to_date(row["date"]),
                    "title": row["title"],
                    "done": row["done"].strip().lower() in TRUE_VALUES,
                })
            except (ValueError, KeyError, TypeError, AttributeError):
                print(f"[건너뜀] 할 일 행 오류: {row}")
    return records