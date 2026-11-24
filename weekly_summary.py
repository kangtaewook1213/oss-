"""주간 리포트: 집계(weekly_summary)와 화면(build_weekly)."""
import csv
import os
import tkinter as tk
from datetime import date, datetime, timedelta

import ui
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
# 화면: main.App 안에서 그려진다. app.selected / app.select / app.reload /
#       app.toast를 쓴다. (색, 글꼴, 공통 위젯은 ui.py)
# ---------------------------------------------------------------
def build_weekly(app, parent):
    day = app.selected
    summary = weekly_summary(load_calorie_records(), load_todo_records(), day)
    cal, todo, daily = summary["calorie"], summary["todo"], summary["daily"]
    ui.page_header(app, parent, "주간 리포트", "한 주의 칼로리와 할 일을 한눈에 돌아보세요.", step=7,
                   week_range=get_week_range)

    active = [d for d in daily if d["intake"] or d["burn"]]
    average = round(cal["intake"] / len(active)) if active else 0
    ui.tile_row(parent, [
        dict(title="주간 섭취", value=f"{cal['intake']:,}", unit="kcal", color=ui.COLOR_INTAKE,
             note=f"기록한 날 평균 {average:,} kcal"),
        dict(title="주간 소모", value=f"{cal['burn']:,}", unit="kcal", color=ui.COLOR_BURN,
             note=f"{sum(1 for d in daily if d['burn'])}일 운동"),
        dict(title="순 칼로리", value=f"{cal['net']:+,}", unit="kcal", color=ui.COLOR_PRIMARY,
             note="섭취 − 소모"),
        dict(title="할 일 완료율", value=f"{todo['rate']}", unit="%", color=ui.COLOR_TODO,
             note=f"{todo['total']}개 중 {todo['done']}개 완료"),
    ]).pack(fill="x", pady=(0, 14))

    main = ui.frame(parent)
    main.pack(fill="both", expand=True)
    side = ui.frame(main, width=ui.px(330))
    side.pack(side="right", fill="y", padx=(14, 0))
    side.pack_propagate(False)

    outer, body = ui.card(main, "요일별 칼로리")
    outer.pack(side="left", fill="both", expand=True)
    if not active:
        ui.empty_state(body, "이 주에는 칼로리 기록이 없습니다",
                       "칼로리 화면에서 식단이나 운동을 기록해 보세요.").pack(expand=True)
    else:
        best = max(daily, key=lambda d: d["intake"])
        insight = (f"가장 많이 섭취한 날은 {ui.WEEKDAYS[best['date'].weekday()]}요일"
                   f"({best['intake']:,} kcal)입니다.")
        ui.label(body, insight, "small").pack(anchor="w", pady=(0, 6))
        labels = [f"{ui.WEEKDAYS[d['date'].weekday()]} {d['date'].day}" for d in daily]
        today = date.today()
        highlight = next((i for i, d in enumerate(daily) if d["date"] == today), None)
        ui.BarChart(body, labels, [("섭취", ui.COLOR_INTAKE, [d["intake"] for d in daily]),
                                   ("소모", ui.COLOR_BURN, [d["burn"] for d in daily])],
                    highlight=highlight).pack(fill="both", expand=True)

    outer, body = ui.card(side, "할 일")
    outer.pack(fill="both", expand=True)
    if not todo["total"]:
        ui.empty_state(body, "이 주에 등록된 할 일이 없습니다").pack(expand=True)
        return
    top = ui.frame(body)
    top.pack(fill="x")
    ui.ring(top, todo["rate"], size=76, width=8, color=ui.COLOR_TODO).pack(side="left")
    text = ui.frame(top)
    text.pack(side="left", padx=14)
    ui.label(text, f"{todo['done']} / {todo['total']} 완료", "title").pack(anchor="w")
    left = len(todo["incomplete"])
    ui.label(text, f"미완료 {left}개" if left else "모두 완료했어요!", "muted",
             color=ui.COLOR_MUTED if left else ui.COLOR_TODO).pack(anchor="w")

    ui.divider(body).pack(fill="x", pady=12)
    ui.label(body, "미완료 할 일", "h2").pack(anchor="w", pady=(0, 6))
    if not left:
        ui.label(body, "남은 할 일이 없습니다.", "small").pack(anchor="w")
        return
    scroll = ui.ScrollFrame(body)
    scroll.pack(fill="both", expand=True)
    for item in sorted(todo["incomplete"], key=lambda t: t["date"]):
        row = ui.frame(scroll.body)
        row.pack(fill="x", pady=3)
        tk.Label(row, text=f"{item['date'].month}/{item['date'].day}", font=ui.FONTS["small"],
                 bg=ui.COLOR_TRACK, fg=ui.COLOR_MUTED, width=5).pack(side="left")
        link = ui.label(row, item["title"], "body", anchor="w", cursor="hand2")
        link.pack(side="left", fill="x", expand=True, padx=8)
        link.bind("<Button-1>", lambda event, d=item["date"]: app.select(d, page="todo"))
