"""주간 리포트: 집계(weekly_summary) + Tkinter 화면(show_weekly_report).

main.py 연결:
    from weekly_summary import show_weekly_report
    show_weekly_report(parent, selected_date)   # selected_date: date 또는 'YYYY-MM-DD'
"""
import csv
import os
import tkinter as tk
from datetime import date, datetime, timedelta
from tkinter import ttk

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


# ---------------------------------------------------------------
# 집계
# ---------------------------------------------------------------
def weekly_summary(calorie_records, todo_records, ref_date):
    """주간 리포트 요약을 만든다.

    입력: 칼로리 기록, 할 일 기록(None이면 빈 리스트로 처리), 기준 날짜
    출력: {
        "start", "end", "has_data",
        "calorie": {"intake", "burn", "net", "records"},
        "daily":   [{"date", "intake", "burn", "net"} x 7],
        "todo":    {"total", "done", "rate", "items", "incomplete"},
    }
    """
    calorie_records = calorie_records or []
    todo_records = todo_records or []
    start, end = get_week_range(ref_date)

    week_cal = [r for r in calorie_records if start <= r["date"] <= end]
    intake = sum(r["kcal"] for r in week_cal if r["type"] == "intake")
    burn = sum(r["kcal"] for r in week_cal if r["type"] == "burn")

    daily = []
    for i in range(7):
        d = start + timedelta(days=i)
        d_in = sum(r["kcal"] for r in week_cal if r["date"] == d and r["type"] == "intake")
        d_burn = sum(r["kcal"] for r in week_cal if r["date"] == d and r["type"] == "burn")
        daily.append({"date": d, "intake": d_in, "burn": d_burn, "net": d_in - d_burn})

    week_todo = [t for t in todo_records if start <= t["date"] <= end]
    done = sum(1 for t in week_todo if t["done"])
    total = len(week_todo)

    return {
        "start": start,
        "end": end,
        "has_data": bool(week_cal or week_todo),
        "calorie": {"intake": intake, "burn": burn,
                    "net": intake - burn, "records": week_cal},
        "daily": daily,
        "todo": {
            "total": total,
            "done": done,
            "rate": round(done / total * 100) if total else 0,
            "items": week_todo,
            "incomplete": [t for t in week_todo if not t["done"]],
        },
    }


# ---------------------------------------------------------------
# 화면
# ---------------------------------------------------------------
def show_weekly_report(parent, selected_date):
    """선택한 날짜가 속한 주의 리포트 창을 연다. 닫으면 parent(상세 화면)로 돌아간다."""
    summary = weekly_summary(load_calorie_records(), load_todo_records(), selected_date)
    start, end = summary["start"], summary["end"]

    win = tk.Toplevel(parent)
    win.title("주간 리포트")
    win.geometry("440x560")
    win.transient(parent)          # 상세 화면 위에 표시 (입력 기능은 막지 않음)

    tk.Label(win, text="주간 리포트", font=("맑은 고딕", 15, "bold")).pack(pady=(14, 2))
    tk.Label(win, text=f"{start.strftime('%Y-%m-%d')} ~ {end.strftime('%Y-%m-%d')}",
             fg="gray").pack()

    if not summary["has_data"]:
        tk.Label(win, text="이 주에는 기록된 데이터가 없습니다.\n칼로리나 할 일을 입력하면 여기에 요약돼요.",
                 font=("맑은 고딕", 11), pady=60, justify="center").pack(expand=True)
        tk.Button(win, text="닫기", width=12, command=win.destroy).pack(pady=15)
        return win

    # --- 칼로리 요약 ---
    cal = summary["calorie"]
    cal_frame = ttk.LabelFrame(win, text="주간 칼로리")
    cal_frame.pack(fill="x", padx=15, pady=(12, 6))
    for label, value in (("섭취", cal["intake"]), ("소모", cal["burn"]), ("순 칼로리", cal["net"])):
        row = tk.Frame(cal_frame)
        row.pack(fill="x", padx=10, pady=2)
        tk.Label(row, text=label, width=10, anchor="w").pack(side="left")
        text = f"{value:+,} kcal" if label == "순 칼로리" else f"{value:,} kcal"
        tk.Label(row, text=text, anchor="e").pack(side="right")

    # 요일별 표
    table = ttk.Treeview(cal_frame, columns=("day", "intake", "burn", "net"),
                         show="headings", height=7)
    for col, head, w in (("day", "요일", 90), ("intake", "섭취", 80),
                         ("burn", "소모", 80), ("net", "순", 80)):
        table.heading(col, text=head)
        table.column(col, width=w, anchor="center")
    for d in summary["daily"]:
        table.insert("", "end", values=(
            f"{d['date'].strftime('%m/%d')} ({WEEKDAY_KR[d['date'].weekday()]})",
            f"{d['intake']:,}", f"{d['burn']:,}", f"{d['net']:+,}"))
    table.pack(fill="x", padx=10, pady=(4, 8))

    # --- 할 일 요약 ---
    todo = summary["todo"]
    todo_frame = ttk.LabelFrame(win, text="할 일 완료율")
    todo_frame.pack(fill="both", expand=True, padx=15, pady=6)

    if todo["total"] == 0:
        tk.Label(todo_frame, text="이 주에 등록된 할 일이 없습니다.", fg="gray").pack(pady=15)
    else:
        tk.Label(todo_frame,
                 text=f"{todo['rate']}%  ({todo['done']} / {todo['total']} 완료)",
                 font=("맑은 고딕", 11, "bold")).pack(pady=(8, 2))
        ttk.Progressbar(todo_frame, maximum=100, value=todo["rate"]).pack(fill="x", padx=10)

        tk.Label(todo_frame, text="미완료 할 일", anchor="w").pack(fill="x", padx=10, pady=(8, 0))
        if todo["incomplete"]:
            box = tk.Frame(todo_frame)
            box.pack(fill="both", expand=True, padx=10, pady=(2, 8))
            scroll = tk.Scrollbar(box)
            scroll.pack(side="right", fill="y")
            lb = tk.Listbox(box, height=5, yscrollcommand=scroll.set)
            for t in sorted(todo["incomplete"], key=lambda x: x["date"]):
                lb.insert("end", f"{t['date'].strftime('%m/%d')}  {t['title']}")
            lb.pack(side="left", fill="both", expand=True)
            scroll.config(command=lb.yview)
        else:
            tk.Label(todo_frame, text="모두 완료했어요!", fg="green").pack(pady=10)

    tk.Button(win, text="닫기", width=12, command=win.destroy).pack(pady=12)
    return win

