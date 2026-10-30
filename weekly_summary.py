import csv
import os
from datetime import datetime, timedelta, date

BASE_DIR = os.path.dirname(__file__)
CALORIE_CSV = os.path.join(BASE_DIR,"data", "sample", "calories.csv")  # TODO: 실제 파일명으로 변경
TODO_CSV = os.path.join(BASE_DIR, "data", "sample", "todo.csv")       # TODO: 실제 파일명/컬럼 확인


def to_date(value):
    """'YYYY-MM-DD' 문자열 또는 date를 date로 변환 (selected_date 연동 대비)"""
    if isinstance(value, date):
        return value
    return datetime.strptime(value, "%Y-%m-%d").date()


def get_week_range(ref_date):
    """ref_date가 속한 주(일~토)의 (시작일, 종료일) 반환"""
    ref_date = to_date(ref_date)
    offset = (ref_date.weekday() + 1) % 7   # 일요일=0, 토요일=6
    start = ref_date - timedelta(days=offset)
    return start, start + timedelta(days=6)


def load_calorie_records(path=CALORIE_CSV):
    records = []
    with open(path, newline="", encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            try:
                records.append({
                    "date": to_date(row["date"]),
                    "type": row["type"],
                    "name": row["name"],
                    "kcal": int(row["kcal"]),
                })
            except (ValueError, KeyError):
                print(f"[건너뜀] 칼로리 행 오류: {row}")
    return records


def load_todo_records(path=TODO_CSV):
    """파일이 없으면 None 반환"""
    if not os.path.exists(path):
        return None
    records = []
    with open(path, newline="", encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            try:
                records.append({
                    "date": to_date(row["date"]),
                    "title": row["title"],
                    "done": row["done"].strip().lower() in ("1", "true", "y", "yes", "완료"),
                })
            except (ValueError, KeyError):
                print(f"[건너뜀] 할 일 행 오류: {row}")
    return records


def weekly_summary(calorie_records, todo_records, ref_date):
    """주간 리포트 요약을 만든다.
    입력: 칼로리 기록, 할 일 기록, 기준 날짜(date 또는 'YYYY-MM-DD')
    출력: 칼로리 요약과 할 일 요약이 담긴 딕셔너리
          todo_records가 None이면 결과의 'todo'는 None
    """
    start, end = get_week_range(ref_date)

    week_cal = [r for r in calorie_records if start <= r["date"] <= end]
    intake = sum(r["kcal"] for r in week_cal if r["type"] == "intake")
    burn = sum(r["kcal"] for r in week_cal if r["type"] == "burn")

    todo = None
    if todo_records is not None:
        week_todo = [t for t in todo_records if start <= t["date"] <= end]
        done = sum(1 for t in week_todo if t["done"])
        total = len(week_todo)
        todo = {
            "total": total,
            "done": done,
            "rate": round(done / total * 100) if total else 0,
            "items": week_todo,
        }

    return {
        "start": start,
        "end": end,
        "calorie": {"intake": intake, "burn": burn,
                    "net": intake - burn, "records": week_cal},
        "todo": todo,
    }


def show_detail_page(parent, summary):
    """상세 페이지 화면을 구현한다.
    입력: 부모 창, 주간 요약 결과
    """
    # TODO: 달력 GUI 구현 후 연동 예정
    pass


def weekly_report_button(parent):
    """주간 리포트 버튼을 만들고 클릭 시 동작을 연결한다.
    입력: 버튼을 올릴 부모 프레임
    """
    # TODO: 달력 GUI 구현 후 연동 예정
    pass
