import csv
import os
import tkinter as tk
from tkinter import messagebox
from datetime import date

BASE_DIR = os.path.dirname(__file__)
DATA_DIR = os.path.join(BASE_DIR, "data")
INBODY_CSV = os.path.join(DATA_DIR, "body_tracker.csv")

CSV_FIELDS = [
    "date",
    "height_cm",
    "weight_kg",
    "skeletal_muscle_mass_kg",
    "body_fat_percentage",
]


def save_inbody_record(record):
    """인바디 기록 한 건을 CSV 파일에 저장한다."""
    os.makedirs(DATA_DIR, exist_ok=True)
    file_exists = os.path.exists(INBODY_CSV)

    with open(INBODY_CSV, "a", newline="", encoding="utf-8-sig") as file:
        writer = csv.DictWriter(file, fieldnames=CSV_FIELDS)
        if not file_exists or os.path.getsize(INBODY_CSV) == 0:
            writer.writeheader()
        writer.writerow(record)


def create_body_tracker_frame(parent):
    """부모 프레임에 인바디 수치 입력 화면을 만든다."""
    frame = tk.Frame(parent, padx=10, pady=10)

    tk.Label(
        frame,
        text="인바디 수치 입력",
        font=("맑은 고딕", 14, "bold"),
    ).grid(row=0, column=0, columnspan=2, pady=(0, 12))

    fields = [
        ("날짜 (YYYY-MM-DD)", "date", date.today().isoformat()),
        ("키 (cm)", "height_cm", ""),
        ("체중 (kg)", "weight_kg", ""),
        ("골격근량 (kg)", "skeletal_muscle_mass_kg", ""),
        ("체지방률 (%)", "body_fat_percentage", ""),
    ]

    entries = {}
    for row_index, (label_text, key, default_value) in enumerate(fields, start=1):
        tk.Label(frame, text=label_text).grid(
            row=row_index, column=0, sticky="e", padx=5, pady=5
        )
        entry = tk.Entry(frame, width=22)
        entry.grid(row=row_index, column=1, sticky="w", padx=5, pady=5)
        if default_value:
            entry.insert(0, default_value)
        entries[key] = entry

    def on_save():
        try:
            record_date = entries["date"].get().strip()
            date.fromisoformat(record_date)

            height = float(entries["height_cm"].get())
            weight = float(entries["weight_kg"].get())
            muscle = float(entries["skeletal_muscle_mass_kg"].get())
            body_fat = float(entries["body_fat_percentage"].get())

            if height <= 0 or weight <= 0 or muscle < 0:
                raise ValueError
            if not 0 <= body_fat <= 100:
                raise ValueError

            record = {
                "date": record_date,
                "height_cm": height,
                "weight_kg": weight,
                "skeletal_muscle_mass_kg": muscle,
                "body_fat_percentage": body_fat,
            }
            save_inbody_record(record)
            messagebox.showinfo("저장 완료", "인바디 기록을 저장했습니다.")

            for key in entries:
                if key != "date":
                    entries[key].delete(0, tk.END)

        except (ValueError, TypeError):
            messagebox.showerror(
                "입력 확인",
                "날짜와 수치를 올바르게 입력해 주세요.\n"
                "키·체중은 0보다 커야 하고, 골격근량은 0 이상, "
                "체지방률은 0~100 사이여야 합니다.",
            )
        except OSError as error:
            messagebox.showerror(
                "저장 오류", f"파일 저장 중 오류가 발생했습니다.\n{error}"
            )

    tk.Button(frame, text="기록 저장", command=on_save).grid(
        row=len(fields) + 1, column=0, columnspan=2, pady=12
    )

    # TODO: 저장된 기록 목록 표시 기능 추가
    # TODO: BMI 자동 계산 기능 추가
    # TODO: 이전 기록 비교 및 변화 추이 그래프 추가

    return frame


if __name__ == "__main__":
    # 단독 실행 테스트용 화면. main.py와 연결할 때는 이 부분을 실행하지 않는다.
    root = tk.Tk()
    root.title("인바디 기록")
    root.geometry("400x380")
    create_body_tracker_frame(root).pack(fill="both", expand=True)
    root.mainloop()
