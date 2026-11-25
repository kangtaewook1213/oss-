<<<<<<< HEAD
import csv
import math
import os
import tkinter as tk
from datetime import date

import ui
from config import BODY_TRACKER_CSV, BODY_TRACKER_HEADER

SAVE_ERRORS = (ValueError, OSError, csv.Error)
BMI_SEGMENTS = [(18.5, ui.COLOR_BURN, "저체중"), (23, ui.COLOR_TODO, "정상"),
                (25, ui.COLOR_INTAKE, "과체중"), (35, ui.COLOR_DANGER, "비만")]


def read_body_records():
    """인바디 CSV를 읽어 리스트로 반환한다. 파일이 없으면 빈 리스트를 반환한다."""
    if not os.path.exists(BODY_TRACKER_CSV):
        return []

    records = []

    with open(BODY_TRACKER_CSV, "r", newline="", encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            try:
                records.append(
                    {
                        "id": int(row["id"]),
                        "date": row["date"],
                        "height_cm": float(row["height_cm"]),
                        "weight_kg": float(row["weight_kg"]),
                        "skeletal_muscle_mass_kg": float(row["skeletal_muscle_mass_kg"]),
                        "body_fat_percentage": float(row["body_fat_percentage"]),
                    }
                )
            except (KeyError, TypeError, ValueError):
                continue

    return records


def next_body_id(records=None):
    if records is None:
        records = read_body_records()
    return max((r["id"] for r in records), default=0) + 1


def save_body_record(selected_date, height, weight, muscle, body_fat):
    """Issue #2: 선택 날짜의 인바디 수치를 저장한다."""
    try:
        height = float(str(height).strip())
        weight = float(str(weight).strip())
        muscle = float(str(muscle).strip())
        body_fat = float(str(body_fat).strip())
    except (TypeError, ValueError):
        raise ValueError("모든 수치는 숫자로 입력해 주세요.")

    if not all(math.isfinite(v) for v in (height, weight, muscle, body_fat)):
        raise ValueError("유한한 숫자를 입력해 주세요.")

    if not 50 <= height <= 250:
        raise ValueError("키는 50~250 cm 사이여야 합니다.")

    if not 10 <= weight <= 500:
        raise ValueError("체중은 10~500 kg 사이여야 합니다.")

    if muscle < 0:
        raise ValueError("골격근량은 0 이상이어야 합니다.")

    if muscle > weight:
        raise ValueError("골격근량은 체중보다 클 수 없습니다.")

    if not 0 <= body_fat <= 100:
        raise ValueError("체지방률은 0~100 사이여야 합니다.")

    os.makedirs(os.path.dirname(BODY_TRACKER_CSV), exist_ok=True)

    file_exists = (
        os.path.exists(BODY_TRACKER_CSV)
        and os.path.getsize(BODY_TRACKER_CSV) > 0
    )

    record = {
        "id": next_body_id(),
        "date": selected_date.isoformat(),
        "height_cm": height,
        "weight_kg": weight,
        "skeletal_muscle_mass_kg": muscle,
        "body_fat_percentage": body_fat,
    }

    with open(BODY_TRACKER_CSV, "a", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=BODY_TRACKER_HEADER)
        if not file_exists:
            writer.writeheader()
        writer.writerow(record)

    return record


def body_record_for_date(selected_date):
    """Issue #3/#4: 선택 날짜의 가장 최근 인바디 기록을 반환한다."""
    target = selected_date.isoformat()
    matches = [r for r in read_body_records() if r["date"] == target]

    if not matches:
        return None

    return max(matches, key=lambda r: r["id"])


def calculate_bmi(height_cm, weight_kg):
    """Issue #3: BMI 자동 계산."""
    height_m = float(height_cm) / 100

    if height_m <= 0:
        raise ValueError("키는 0보다 커야 합니다.")

    return round(float(weight_kg) / (height_m ** 2), 1)


def previous_body_record(selected_date):
    """Issue #4: 선택 날짜보다 이전인 가장 가까운 인바디 기록을 반환한다."""
    candidates = []

    for record in read_body_records():
        try:
            record_date = date.fromisoformat(record["date"])
        except ValueError:
            continue

        if record_date < selected_date:
            candidates.append((record_date, record))

    if not candidates:
        return None

    candidates.sort(key=lambda item: (item[0], item[1]["id"]))
    return candidates[-1][1]


def calculate_change(current_value, previous_value):
    """변화량과 변화율을 계산한다."""
    diff = current_value - previous_value
    rate = None if previous_value == 0 else diff / previous_value * 100
    return diff, rate


# ---------------------------------------------------------------
# 화면: main.App 안에서 그려진다. app.selected / app.select / app.reload /
#       app.toast를 쓴다. (색, 글꼴, 공통 위젯은 ui.py)
# ---------------------------------------------------------------
def bmi_category(bmi):
    for limit, _, name in BMI_SEGMENTS:
        if bmi < limit:
            return name
    return BMI_SEGMENTS[-1][2]


def build_body(app, parent):
    day = app.selected
    ui.page_header(app, parent, "인바디", f"{ui.format_day(day)}의 신체 수치를 기록하세요.", step=1)

    latest = {}     # 날짜별 가장 최근 기록
    for record in sorted(read_body_records(), key=lambda r: r["id"]):
        latest[record["date"]] = record
    history = [latest[key] for key in sorted(latest)]
    current = latest.get(day.isoformat())
    earlier = [r for r in history if r["date"] < day.isoformat()]
    shown = current or (earlier[-1] if earlier else None)
    # 이전 기록 찾기와 변화량 계산은 기존 함수(previous_body_record, calculate_change)를 쓴다.
    previous = (previous_body_record(date.fromisoformat(shown["date"]))
                if shown else None)

    def change(key, unit):
        if not shown or not previous:
            return "이전 기록 없음"
        diff, rate = calculate_change(shown[key], previous[key])
        if abs(diff) < 0.05:
            return "이전 기록과 같음"
        rate_text = "" if rate is None else f" ({rate:+.1f}%)"
        return f"이전보다 {'▲' if diff > 0 else '▼'} {abs(diff):.1f}{unit}{rate_text}"

    def value(key):
        return f"{shown[key]:g}" if shown else "–"

    bmi = calculate_bmi(shown["height_cm"], shown["weight_kg"]) if shown else None
    ui.tile_row(parent, [
        dict(title="체중", value=value("weight_kg"), unit="kg", color=ui.COLOR_BODY,
             note=change("weight_kg", "kg")),
        dict(title="골격근량", value=value("skeletal_muscle_mass_kg"), unit="kg",
             color=ui.COLOR_TODO, note=change("skeletal_muscle_mass_kg", "kg")),
        dict(title="체지방률", value=value("body_fat_percentage"), unit="%",
             color=ui.COLOR_INTAKE, note=change("body_fat_percentage", "%p")),
        dict(title="BMI", value=f"{bmi}" if bmi else "–", color=ui.COLOR_PRIMARY,
             note=bmi_category(bmi) if bmi else "기록 없음"),
    ]).pack(fill="x", pady=(0, 14))

    main = ui.frame(parent)
    main.pack(fill="both", expand=True)
    form_outer, form = ui.card(main, "수치 입력")
    form_outer.pack(side="left", fill="y")
    right = ui.frame(main)
    right.pack(side="left", fill="both", expand=True, padx=(14, 0))

    if current:
        note = "이 날짜에 저장된 기록이 있습니다. 다시 저장하면 새 값으로 바뀝니다."
    elif shown:
        note = f"이 날짜의 기록이 없어 {shown['date']} 기록을 보여주고 있습니다."
    else:
        note = "아직 인바디 기록이 없습니다."
    ui.label(form, note, "small", wraplength=ui.px(250), justify="left").pack(anchor="w")

    fields = (("height_cm", "키 (cm)"), ("weight_kg", "체중 (kg)"),
              ("skeletal_muscle_mass_kg", "골격근량 (kg)"), ("body_fat_percentage", "체지방률 (%)"))
    inputs = {}
    boxes = []
    for key, text in fields:
        ui.label(form, text, "small").pack(anchor="w", pady=(12, 4))
        inputs[key] = tk.StringVar(master=form)
        if current:
            inputs[key].set(f"{current[key]:g}")
        elif shown and key == "height_cm":
            inputs[key].set(f"{shown[key]:g}")      # 키는 잘 변하지 않으므로 미리 채운다
        box = ui.entry(form, inputs[key], width=30)
        box.pack(fill="x", ipady=7)
        boxes.append(box)
        if key == ("weight_kg" if inputs["height_cm"].get() else "height_cm"):
            app.autofocus(box, always=True)

    def submit():
        try:
            save_body_record(day, *(inputs[key].get() for key, _ in fields))
        except SAVE_ERRORS as error:
            app.toast(str(error), "error")
            return
        app.reload()
        app.toast("인바디 기록을 저장했습니다.")

    # 마지막 칸에서 Enter를 누르면 저장, 그 외에는 다음 칸으로 이동
    for index, box in enumerate(boxes):
        if index < len(boxes) - 1:
            box.bind("<Return>", lambda event, nxt=boxes[index + 1]: nxt.focus_set())
        else:
            box.bind("<Return>", lambda event: submit())

    ui.button(form, "기록 저장", submit).pack(fill="x", pady=(18, 0))

    outer, body = ui.card(right, "BMI")
    outer.pack(fill="x", pady=(0, 14))
    ui.ScaleBar(body, bmi, 15, BMI_SEGMENTS).pack(fill="x")

    outer, body = ui.card(right, "체중 변화")
    outer.pack(fill="both", expand=True)
    points = [(f"{int(r['date'][5:7])}/{int(r['date'][8:10])}", r["weight_kg"])
              for r in history[-10:]]
    if len(points) < 2:
        ui.empty_state(body, "기록이 2개 이상 쌓이면 변화 그래프가 나타납니다",
                       "날짜를 바꿔 가며 수치를 저장해 보세요.").pack(expand=True)
    else:
        ui.LineChart(body, points, color=ui.COLOR_BODY, unit="kg").pack(fill="both", expand=True)
=======
import csv
import math
import os
import tkinter as tk
from datetime import date

import ui
from config import BODY_TRACKER_CSV, BODY_TRACKER_HEADER

SAVE_ERRORS = (ValueError, OSError, csv.Error)
BMI_SEGMENTS = [(18.5, ui.COLOR_BURN, "저체중"), (23, ui.COLOR_TODO, "정상"),
                (25, ui.COLOR_INTAKE, "과체중"), (35, ui.COLOR_DANGER, "비만")]


def read_body_records():
    """인바디 CSV를 읽어 리스트로 반환한다. 파일이 없으면 빈 리스트를 반환한다."""
    if not os.path.exists(BODY_TRACKER_CSV):
        return []

    records = []

    with open(BODY_TRACKER_CSV, "r", newline="", encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            try:
                records.append(
                    {
                        "id": int(row["id"]),
                        "date": row["date"],
                        "height_cm": float(row["height_cm"]),
                        "weight_kg": float(row["weight_kg"]),
                        "skeletal_muscle_mass_kg": float(row["skeletal_muscle_mass_kg"]),
                        "body_fat_percentage": float(row["body_fat_percentage"]),
                    }
                )
            except (KeyError, TypeError, ValueError):
                continue

    return records


def next_body_id(records=None):
    if records is None:
        records = read_body_records()
    return max((r["id"] for r in records), default=0) + 1


def save_body_record(selected_date, height, weight, muscle, body_fat):
    """Issue #2: 선택 날짜의 인바디 수치를 저장한다."""
    try:
        height = float(str(height).strip())
        weight = float(str(weight).strip())
        muscle = float(str(muscle).strip())
        body_fat = float(str(body_fat).strip())
    except (TypeError, ValueError):
        raise ValueError("모든 수치는 숫자로 입력해 주세요.")

    if not all(math.isfinite(v) for v in (height, weight, muscle, body_fat)):
        raise ValueError("유한한 숫자를 입력해 주세요.")

    if not 50 <= height <= 250:
        raise ValueError("키는 50~250 cm 사이여야 합니다.")

    if not 10 <= weight <= 500:
        raise ValueError("체중은 10~500 kg 사이여야 합니다.")

    if muscle < 0:
        raise ValueError("골격근량은 0 이상이어야 합니다.")

    if muscle > weight:
        raise ValueError("골격근량은 체중보다 클 수 없습니다.")

    if not 0 <= body_fat <= 100:
        raise ValueError("체지방률은 0~100 사이여야 합니다.")

    os.makedirs(os.path.dirname(BODY_TRACKER_CSV), exist_ok=True)

    file_exists = (
        os.path.exists(BODY_TRACKER_CSV)
        and os.path.getsize(BODY_TRACKER_CSV) > 0
    )

    record = {
        "id": next_body_id(),
        "date": selected_date.isoformat(),
        "height_cm": height,
        "weight_kg": weight,
        "skeletal_muscle_mass_kg": muscle,
        "body_fat_percentage": body_fat,
    }

    with open(BODY_TRACKER_CSV, "a", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=BODY_TRACKER_HEADER)
        if not file_exists:
            writer.writeheader()
        writer.writerow(record)

    return record


def body_record_for_date(selected_date):
    """Issue #3/#4: 선택 날짜의 가장 최근 인바디 기록을 반환한다."""
    target = selected_date.isoformat()
    matches = [r for r in read_body_records() if r["date"] == target]

    if not matches:
        return None

    return max(matches, key=lambda r: r["id"])


def calculate_bmi(height_cm, weight_kg):
    """Issue #3: BMI 자동 계산."""
    height_m = float(height_cm) / 100

    if height_m <= 0:
        raise ValueError("키는 0보다 커야 합니다.")

    return round(float(weight_kg) / (height_m ** 2), 1)


def previous_body_record(selected_date):
    """Issue #4: 선택 날짜보다 이전인 가장 가까운 인바디 기록을 반환한다."""
    candidates = []

    for record in read_body_records():
        try:
            record_date = date.fromisoformat(record["date"])
        except ValueError:
            continue

        if record_date < selected_date:
            candidates.append((record_date, record))

    if not candidates:
        return None

    candidates.sort(key=lambda item: (item[0], item[1]["id"]))
    return candidates[-1][1]


def calculate_change(current_value, previous_value):
    """변화량과 변화율을 계산한다."""
    diff = current_value - previous_value
    rate = None if previous_value == 0 else diff / previous_value * 100
    return diff, rate


# ---------------------------------------------------------------
# 화면: main.App 안에서 그려진다. app.selected / app.select / app.reload /
#       app.toast를 쓴다. (색, 글꼴, 공통 위젯은 ui.py)
# ---------------------------------------------------------------
def bmi_category(bmi):
    for limit, _, name in BMI_SEGMENTS:
        if bmi < limit:
            return name
    return BMI_SEGMENTS[-1][2]


def build_body(app, parent):
    day = app.selected
    ui.page_header(app, parent, "인바디", f"{ui.format_day(day)}의 신체 수치를 기록하세요.", step=1)

    latest = {}     # 날짜별 가장 최근 기록
    for record in sorted(read_body_records(), key=lambda r: r["id"]):
        latest[record["date"]] = record
    history = [latest[key] for key in sorted(latest)]
    current = latest.get(day.isoformat())
    earlier = [r for r in history if r["date"] < day.isoformat()]
    shown = current or (earlier[-1] if earlier else None)
    # 이전 기록 찾기와 변화량 계산은 기존 함수(previous_body_record, calculate_change)를 쓴다.
    previous = (previous_body_record(date.fromisoformat(shown["date"]))
                if shown else None)

    def change(key, unit):
        if not shown or not previous:
            return "이전 기록 없음"
        diff, rate = calculate_change(shown[key], previous[key])
        if abs(diff) < 0.05:
            return "이전 기록과 같음"
        rate_text = "" if rate is None else f" ({rate:+.1f}%)"
        return f"이전보다 {'▲' if diff > 0 else '▼'} {abs(diff):.1f}{unit}{rate_text}"

    def value(key):
        return f"{shown[key]:g}" if shown else "–"

    bmi = calculate_bmi(shown["height_cm"], shown["weight_kg"]) if shown else None
    ui.tile_row(parent, [
        dict(title="체중", value=value("weight_kg"), unit="kg", color=ui.COLOR_BODY,
             note=change("weight_kg", "kg")),
        dict(title="골격근량", value=value("skeletal_muscle_mass_kg"), unit="kg",
             color=ui.COLOR_TODO, note=change("skeletal_muscle_mass_kg", "kg")),
        dict(title="체지방률", value=value("body_fat_percentage"), unit="%",
             color=ui.COLOR_INTAKE, note=change("body_fat_percentage", "%p")),
        dict(title="BMI", value=f"{bmi}" if bmi else "–", color=ui.COLOR_PRIMARY,
             note=bmi_category(bmi) if bmi else "기록 없음"),
    ]).pack(fill="x", pady=(0, 14))

    main = ui.frame(parent)
    main.pack(fill="both", expand=True)
    form_outer, form = ui.card(main, "수치 입력")
    form_outer.pack(side="left", fill="y")
    right = ui.frame(main)
    right.pack(side="left", fill="both", expand=True, padx=(14, 0))

    if current:
        note = "이 날짜에 저장된 기록이 있습니다. 다시 저장하면 새 값으로 바뀝니다."
    elif shown:
        note = f"이 날짜의 기록이 없어 {shown['date']} 기록을 보여주고 있습니다."
    else:
        note = "아직 인바디 기록이 없습니다."
    ui.label(form, note, "small", wraplength=ui.px(250), justify="left").pack(anchor="w")

    fields = (("height_cm", "키 (cm)"), ("weight_kg", "체중 (kg)"),
              ("skeletal_muscle_mass_kg", "골격근량 (kg)"), ("body_fat_percentage", "체지방률 (%)"))
    inputs = {}
    boxes = []
    for key, text in fields:
        ui.label(form, text, "small").pack(anchor="w", pady=(12, 4))
        inputs[key] = tk.StringVar(master=form)
        if current:
            inputs[key].set(f"{current[key]:g}")
        elif shown and key == "height_cm":
            inputs[key].set(f"{shown[key]:g}")      # 키는 잘 변하지 않으므로 미리 채운다
        box = ui.entry(form, inputs[key], width=30)
        box.pack(fill="x", ipady=7)
        boxes.append(box)
        if key == ("weight_kg" if inputs["height_cm"].get() else "height_cm"):
            app.autofocus(box, always=True)

    def submit():
        try:
            save_body_record(day, *(inputs[key].get() for key, _ in fields))
        except SAVE_ERRORS as error:
            app.toast(str(error), "error")
            return
        app.reload()
        app.toast("인바디 기록을 저장했습니다.")

    # 마지막 칸에서 Enter를 누르면 저장, 그 외에는 다음 칸으로 이동
    for index, box in enumerate(boxes):
        if index < len(boxes) - 1:
            box.bind("<Return>", lambda event, nxt=boxes[index + 1]: nxt.focus_set())
        else:
            box.bind("<Return>", lambda event: submit())

    ui.button(form, "기록 저장", submit).pack(fill="x", pady=(18, 0))

    outer, body = ui.card(right, "BMI")
    outer.pack(fill="x", pady=(0, 14))
    ui.ScaleBar(body, bmi, 15, BMI_SEGMENTS).pack(fill="x")

    outer, body = ui.card(right, "체중 변화")
    outer.pack(fill="both", expand=True)
    points = [(f"{int(r['date'][5:7])}/{int(r['date'][8:10])}", r["weight_kg"])
              for r in history[-10:]]
    if len(points) < 2:
        ui.empty_state(body, "기록이 2개 이상 쌓이면 변화 그래프가 나타납니다",
                       "날짜를 바꿔 가며 수치를 저장해 보세요.").pack(expand=True)
    else:
        ui.LineChart(body, points, color=ui.COLOR_BODY, unit="kg").pack(fill="both", expand=True)
>>>>>>> 2f093ee7b39fba61f2cace8575301f14cc6c70e2
