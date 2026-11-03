import csv
import math
import os
import tkinter as tk
from datetime import date
from tkinter import messagebox, ttk

from config import BODY_TRACKER_CSV, BODY_TRACKER_HEADER
from ui import style_widgets


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

def show_body_tracker(parent, selected_date, embedded=False):
    """인바디 수치 입력 및 저장 화면을 표시한다."""

    if embedded:
        win = tk.Frame(parent, bg="#FFFFFF")
        win.pack(fill="both", expand=True)
    else:
        win = tk.Toplevel(parent)
        win.title(f"{selected_date.isoformat()} 건강 기록")
        win.geometry("760x580")

    notebook = ttk.Notebook(win)
    notebook.pack(fill="both", expand=True, padx=10, pady=10)

    input_frame = tk.Frame(notebook, padx=15, pady=15)

    tk.Label(
        input_frame,
        text=f"{selected_date.isoformat()} 인바디 수치 입력",
        font=("맑은 고딕", 13, "bold"),
    ).grid(row=0, column=0, columnspan=2, pady=(0, 15))

    fields = [
        ("키(cm)", "height"),
        ("체중(kg)", "weight"),
        ("골격근량(kg)", "muscle"),
        ("체지방률(%)", "fat"),
    ]

    entries = {}

    for row, (label, key) in enumerate(fields, start=1):
        tk.Label(input_frame, text=label).grid(
            row=row, column=0, sticky="e", padx=5, pady=5
        )

        entry = tk.Entry(input_frame, width=24)
        entry.grid(row=row, column=1, sticky="w")
        entries[key] = entry

    def on_save():
        try:
            save_body_record(
                selected_date,
                entries["height"].get(),
                entries["weight"].get(),
                entries["muscle"].get(),
                entries["fat"].get(),
            )

            messagebox.showinfo(
                "저장 완료",
                "인바디 기록을 저장했습니다.",
                parent=win,
            )

        except (ValueError, OSError, csv.Error) as e:
            messagebox.showerror(
                "입력 오류",
                str(e),
                parent=win,
            )

    tk.Button(
        input_frame,
        text="기록 저장",
        command=on_save,
    ).grid(row=5, column=0, columnspan=2, pady=15)

    notebook.add(input_frame, text="입력·저장")

    style_widgets(win)
    return win