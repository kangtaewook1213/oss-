import csv
import os
import tkinter as tk
from tkinter import messagebox, ttk

import ui
from config import CALORIE_CSV, CALORIE_HEADER


TYPE_CODES = {"식단 (섭취)": "intake", "운동 (소모)": "burn"}
TYPE_LABELS = {"intake": "식단 (섭취)", "burn": "운동 (소모)"}
SAVE_ERRORS = (ValueError, OSError, csv.Error)


# 1. CSV 읽기와 쓰기

def read_calorie_records():
    if not os.path.exists(CALORIE_CSV):
        return []
    records = []
    with open(CALORIE_CSV, "r", newline="", encoding="utf-8-sig") as file:
        for row in csv.DictReader(file):
            try:
                records.append({
                    "id": int(row["id"]), "date": row["date"],
                    "type": row["type"].strip().lower(),
                    "name": row["name"], "kcal": int(row["kcal"]),
                })
            except (KeyError, TypeError, ValueError, AttributeError):
                continue
    return records


def write_all_calorie_records(records):
    os.makedirs(os.path.dirname(CALORIE_CSV), exist_ok=True)
    with open(CALORIE_CSV, "w", newline="", encoding="utf-8-sig") as file:
        writer = csv.DictWriter(file, fieldnames=CALORIE_HEADER)
        writer.writeheader()
        writer.writerows(records)


def next_calorie_id():
    records = read_calorie_records()
    return max((record["id"] for record in records), default=0) + 1


def records_for_date(selected_date):
    return [record for record in read_calorie_records()
            if record["date"] == selected_date.isoformat()]


# 2. 입력 검사, 저장, 수정, 삭제

def check_input(record_type, name, kcal):
    record_type = record_type.strip().lower()
    name = name.strip()
    if record_type not in TYPE_LABELS:
        raise ValueError("식단/운동 구분이 올바르지 않습니다.")
    if not name:
        raise ValueError("기록 이름을 입력해 주세요.")
    try:
        kcal = int(kcal)
    except (TypeError, ValueError):
        raise ValueError("칼로리는 정수로 입력해 주세요.")
    if kcal < 0:
        raise ValueError("칼로리는 0 이상이어야 합니다.")
    return record_type, name, kcal


def save_calorie_record(selected_date, record_type, name, kcal):
    record_type, name, kcal = check_input(record_type, name, kcal)
    record = {"id": next_calorie_id(), "date": selected_date.isoformat(),
              "type": record_type, "name": name, "kcal": kcal}
    os.makedirs(os.path.dirname(CALORIE_CSV), exist_ok=True)
    has_data = os.path.exists(CALORIE_CSV) and os.path.getsize(CALORIE_CSV) > 0
    with open(CALORIE_CSV, "a", newline="", encoding="utf-8-sig") as file:
        writer = csv.DictWriter(file, fieldnames=CALORIE_HEADER)
        if not has_data:
            writer.writeheader()
        writer.writerow(record)
    return record


def update_calorie_record(record_id, record_type, name, kcal):
    record_type, name, kcal = check_input(record_type, name, kcal)
    records = read_calorie_records()
    for record in records:
        if record["id"] == int(record_id):
            record.update(type=record_type, name=name, kcal=kcal)
            write_all_calorie_records(records)
            return
    raise ValueError("수정할 기록을 찾지 못했습니다.")


def delete_calorie_record(record_id):
    records = read_calorie_records()
    remaining = [record for record in records if record["id"] != int(record_id)]
    if len(records) == len(remaining):
        raise ValueError("삭제할 기록을 찾지 못했습니다.")
    write_all_calorie_records(remaining)


# 3. 하루 칼로리 계산

def calorie_totals(records):
    intake = sum(record["kcal"] for record in records if record["type"] == "intake")
    burn = sum(record["kcal"] for record in records if record["type"] == "burn")
    return {"intake": intake, "burn": burn, "net": intake - burn}


def calculate_daily_calorie(selected_date):
    return calorie_totals(records_for_date(selected_date))


# ---------------------------------------------------------------
# 4. 화면: main.App 안에서 그려진다. app.selected / app.reload /
#       app.toast를 쓴다. (색, 글꼴, 공통 위젯은 ui.py)
# ---------------------------------------------------------------

def build_calorie(app, parent):
    day = app.selected
    records = records_for_date(day)
    totals = calorie_totals(records)

    ui.page_header(
        app,
        parent,
        "칼로리",
        f"{ui.format_day(day)}의 식단과 운동을 기록하세요.",
        step=1
    )

    ui.tile_row(parent, [
        dict(
            title="섭취",
            value=f"{totals['intake']:,}",
            unit="kcal",
            color=ui.COLOR_INTAKE,
            note=f"식단 {sum(1 for r in records if r['type'] == 'intake')}건"
        ),
        dict(
            title="소모",
            value=f"{totals['burn']:,}",
            unit="kcal",
            color=ui.COLOR_BURN,
            note=f"운동 {sum(1 for r in records if r['type'] == 'burn')}건"
        ),
        dict(
            title="순 칼로리",
            value=f"{totals['net']:+,}",
            unit="kcal",
            color=ui.COLOR_PRIMARY,
            note="섭취 − 소모"
        ),
    ]).pack(fill="x", pady=(0, 14))

    main = ui.frame(parent)
    main.pack(fill="both", expand=True)

    form_outer, form = ui.card(main)
    form_outer.pack(side="left", fill="y")

    kind = tk.StringVar(master=form, value="intake")
    name = tk.StringVar(master=form)
    kcal = tk.StringVar(master=form)

    ui.label(form, "새 기록", "h2").pack(
        anchor="w",
        pady=(0, 10)
    )

    switch = ui.segmented(
        form,
        [
            ("intake", "식단 (섭취)"),
            ("burn", "운동 (소모)")
        ],
        kind
    )
    switch.pack(fill="x")

    ui.label(
        form,
        "기록 이름",
        "small"
    ).pack(anchor="w", pady=(14, 4))

    name_box = ui.entry(form, name, width=30)
    name_box.pack(fill="x", ipady=7)

    ui.label(
        form,
        "칼로리 (kcal)",
        "small"
    ).pack(anchor="w", pady=(12, 4))

    kcal_box = ui.entry(form, kcal)
    kcal_box.pack(fill="x", ipady=7)

    def submit(event=None):
        try:
            save_calorie_record(
                day,
                kind.get(),
                name.get(),
                kcal.get()
            )
        except SAVE_ERRORS as error:
            app.toast(str(error), "error")
            return

        app.reload(refocus=True)
        app.toast("기록을 추가했습니다.")

    save_button = ui.button(
        form,
        "기록 추가",
        submit
    )
    save_button.pack(fill="x", pady=(18, 0))

    for box in (name_box, kcal_box):
        box.bind("<Return>", submit)

    app.autofocus(name_box, always=True)