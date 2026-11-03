import csv
import os
import tkinter as tk
from tkinter import messagebox

from config import CALORIE_CSV, CALORIE_HEADER


def read_calorie_records():
    if not os.path.exists(CALORIE_CSV):
        return []

    records = []

    with open(CALORIE_CSV, "r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        for row in reader:
            try:
                records.append({
                    "id": int(row["id"]),
                    "date": row["date"],
                    "type": row["type"],
                    "name": row["name"],
                    "kcal": int(row["kcal"]),
                })
            except (KeyError, ValueError):
                continue

    return records


def next_calorie_id():
    records = read_calorie_records()
    return max((r["id"] for r in records), default=0) + 1


def save_calorie_record(selected_date, record_type, name, kcal):
    if record_type not in ("intake", "burn"):
        raise ValueError("구분은 intake 또는 burn이어야 합니다.")

    if not name.strip():
        raise ValueError("기록 이름을 입력해 주세요.")

    try:
        kcal = int(kcal)
    except ValueError:
        raise ValueError("칼로리는 숫자로 입력해 주세요.")

    if kcal < 0:
        raise ValueError("칼로리는 0 이상이어야 합니다.")

    record = {
        "id": next_calorie_id(),
        "date": selected_date.isoformat(),
        "type": record_type,
        "name": name.strip(),
        "kcal": kcal,
    }

    file_exists = os.path.exists(CALORIE_CSV)

    with open(CALORIE_CSV, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CALORIE_HEADER)

        if not file_exists:
            writer.writeheader()

        writer.writerow(record)


def manage_record(records):
    # TODO: 조회, 수정, 삭제 기능 구현
    pass


def calculate_daily_calorie(selected_date):
    # TODO: 섭취, 소모, 순수 칼로리 계산
    pass


def show_calorie_page(parent, selected_date):
    win = tk.Toplevel(parent)
    win.title("칼로리 다이어리")
    win.geometry("400x300")

    tk.Label(
        win,
        text=f"{selected_date.isoformat()} 칼로리 기록",
        font=("맑은 고딕", 13, "bold")
    ).pack(pady=15)

    record_type = tk.StringVar(value="intake")

    tk.OptionMenu(
        win,
        record_type,
        "intake",
        "burn"
    ).pack(pady=5)

    name_entry = tk.Entry(win, width=30)
    name_entry.pack(pady=5)

    kcal_entry = tk.Entry(win, width=30)
    kcal_entry.pack(pady=5)

    def on_save():
        try:
            save_calorie_record(
                selected_date,
                record_type.get(),
                name_entry.get(),
                kcal_entry.get()
            )

            messagebox.showinfo(
                "저장 완료",
                "기록이 저장되었습니다.",
                parent=win
            )

        except ValueError as e:
            messagebox.showerror(
                "입력 오류",
                str(e),
                parent=win
            )

    tk.Button(
        win,
        text="기록 저장",
        command=on_save
    ).pack(pady=15)

    return win