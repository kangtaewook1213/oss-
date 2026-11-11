import csv
import os
import tkinter as tk
from tkinter import messagebox, ttk

from config import CALORIE_CSV, CALORIE_HEADER


TYPE_CODES = {"식단 (섭취)": "intake", "운동 (소모)": "burn"}
TYPE_LABELS = {"intake": "식단 (섭취)", "burn": "운동 (소모)"}


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


# 4. 화면 만들기

def make_input_form(parent):
    """추가와 수정 화면에서 같은 입력 양식을 사용한다."""
    form = tk.Frame(parent)
    form.pack(anchor="w", padx=15, pady=10)
    record_type = tk.StringVar(master=parent, value="식단 (섭취)")
    name = tk.StringVar(master=parent)
    kcal = tk.StringVar(master=parent)
    fields = [tk.OptionMenu(form, record_type, *TYPE_CODES),
              tk.Entry(form, textvariable=name, width=28),
              tk.Entry(form, textvariable=kcal, width=28)]
    for row, (label, field) in enumerate(zip(("구분", "기록 이름", "칼로리(kcal)"), fields)):
        tk.Label(form, text=label).grid(row=row, column=0, sticky="e", padx=8, pady=6)
        field.grid(row=row, column=1, sticky="w")
    return record_type, name, kcal


def show_calorie_page(parent, selected_date, embedded=False):
    if embedded:
        win = tk.Frame(parent, bg="#FFFFFF")
        win.pack(fill="both", expand=True)
    else:
        win = tk.Toplevel(parent)
        win.title(f"{selected_date.isoformat()} 건강 기록")
        win.geometry("760x580")
        win.minsize(700, 540)

    notebook = ttk.Notebook(win)
    notebook.pack(fill="both", expand=True, padx=10, pady=10)
    input_page = tk.Frame(notebook)
    manage_page = tk.Frame(notebook)
    daily_page = tk.Frame(notebook)
    for page, title in ((input_page, "입력·저장"), (manage_page, "조회·수정·삭제"),
                        (daily_page, "일일 계산")):
        notebook.add(page, text=title)

    tk.Label(input_page, text=f"{selected_date.isoformat()} 식단·운동 기록 입력",
             font=("맑은 고딕", 13, "bold")).pack(anchor="w", padx=20, pady=15)
    add_type, add_name, add_kcal = make_input_form(input_page)

    # 수정 입력란과 버튼을 아래에 확보하고, 나머지 공간에 표를 표시한다.
    edit_area = tk.Frame(manage_page)
    edit_area.pack(side="bottom", fill="x")
    edit_type, edit_name, edit_kcal = make_input_form(edit_area)

    buttons = tk.Frame(edit_area)
    buttons.pack(pady=8)
    table_area = tk.Frame(manage_page)
    table_area.pack(fill="both", expand=True, padx=12, pady=10)
    tree = ttk.Treeview(table_area, columns=("id", "type", "name", "kcal"),
                        show="headings", selectmode="browse", height=6)
    for column, title, width in (("id", "ID", 50), ("type", "구분", 120),
                                 ("name", "이름", 220), ("kcal", "kcal", 90)):
        tree.heading(column, text=title)
        tree.column(column, width=width, anchor="center")
    scrollbar = ttk.Scrollbar(table_area, command=tree.yview)
    scrollbar.pack(side="right", fill="y")
    tree.configure(yscrollcommand=scrollbar.set)
    tree.pack(fill="both", expand=True)
    daily_label = tk.Label(daily_page, font=("맑은 고딕", 12), justify="left")
    daily_label.pack(anchor="w", padx=20, pady=20)

    # 5. 버튼을 눌렀을 때 실행할 함수
    def refresh_all():
        records = records_for_date(selected_date)
        for item in tree.get_children():
            tree.delete(item)
        for record in records:
            tree.insert("", "end", values=(record["id"],
                        TYPE_LABELS.get(record["type"], record["type"]),
                        record["name"], record["kcal"]))
        totals = calorie_totals(records)
        daily_label.config(text=f"총 섭취 칼로리: {totals['intake']} kcal\n"
                                f"총 소모 칼로리: {totals['burn']} kcal\n"
                                f"섭취 - 운동 소모: {totals['net']} kcal")

    def selected_values():
        selected = tree.selection()
        if not selected:
            raise ValueError("기록을 먼저 선택해 주세요.")
        return tree.item(selected[0], "values")

    def fill_selected(event=None):
        if tree.selection():
            values = selected_values()
            edit_type.set(values[1])
            edit_name.set(values[2])
            edit_kcal.set(values[3])

    def on_save(edit=False):
        try:
            if edit:
                record_id = int(selected_values()[0])
                update_calorie_record(record_id, TYPE_CODES[edit_type.get()],
                                      edit_name.get(), edit_kcal.get())
            else:
                save_calorie_record(selected_date, TYPE_CODES[add_type.get()],
                                    add_name.get(), add_kcal.get())
                add_name.set("")
                add_kcal.set("")

            refresh_all()

            if edit:
                edit_type.set("식단 (섭취)")
                edit_name.set("")
                edit_kcal.set("")

            if not edit:
                messagebox.showinfo("저장 완료", "기록이 저장되었습니다.", parent=win)
        except (ValueError, OSError) as error:
            messagebox.showerror("저장 오류", str(error), parent=win)

    def on_delete():
        try:
            record_id = int(selected_values()[0])
            if messagebox.askyesno("삭제 확인", "선택한 기록을 삭제할까요?", parent=win):
                delete_calorie_record(record_id)
                edit_type.set("식단 (섭취)")
                edit_name.set("")
                edit_kcal.set("")
                refresh_all()
        except (ValueError, OSError) as error:
            messagebox.showerror("삭제 오류", str(error), parent=win)

    tree.bind("<<TreeviewSelect>>", fill_selected)
    tk.Button(input_page, text="기록 저장", command=on_save).pack(anchor="w", padx=20, pady=10)
    for text, action in (("새로고침", refresh_all), ("수정", lambda: on_save(True)),
                         ("삭제", on_delete)):
        tk.Button(buttons, text=text, command=action).pack(side="left", padx=4)
    tk.Button(daily_page, text="다시 계산", command=refresh_all).pack(anchor="w", padx=20)

    refresh_all()
    return win