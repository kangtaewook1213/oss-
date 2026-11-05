
"""선택한 날짜의 할 일을 조회하고 추가·완료·삭제한다."""
import csv
import tkinter as tk
from tkinter import messagebox

from config import TODO_CSV, TODO_HEADER


def load_todos(selected_date):
    """선택한 날짜의 할 일 조회"""
    todos = []

    try:
        with open(TODO_CSV, newline="", encoding="utf-8-sig") as file:
            for row in csv.DictReader(file):
                if row.get("date") == selected_date.isoformat():
                    todos.append({
                        "id": row["id"],
                        "title": row["title"],
                        "done": row["done"].lower() == "true"
                    })
    except FileNotFoundError:
        pass

    return todos


def save_todos(todos, selected_date):
    """선택한 날짜의 할 일 저장"""
    rows = []

    try:
        with open(TODO_CSV, newline="", encoding="utf-8-sig") as file:
            rows = list(csv.DictReader(file))
    except FileNotFoundError:
        pass

    date_text = selected_date.isoformat()

    # 다른 날짜의 데이터는 유지
    rows = [r for r in rows if r.get("date") != date_text]

    for todo in todos:
        rows.append({
            "id": todo["id"],
            "date": date_text,
            "title": todo["title"],
            "done": str(todo["done"])
        })

    with open(TODO_CSV, "w", newline="", encoding="utf-8-sig") as file:
        writer = csv.DictWriter(file, fieldnames=TODO_HEADER)
        writer.writeheader()
        writer.writerows(rows)


def show_daily_todo(parent, selected_date):
    """할 일 관리 화면"""

    win = tk.Toplevel(parent)
    win.title(f"{selected_date} 할 일")
    win.geometry("380x420")

    tk.Label(
        win,
        text=f"{selected_date.strftime('%Y년 %m월 %d일')} 할 일",
        font=("맑은 고딕", 14, "bold")
    ).pack(pady=15)

    todos = load_todos(selected_date)

    # 할 일 목록 영역
    list_frame = tk.Frame(win)
    list_frame.pack(fill="both", expand=True, padx=15)

    # 입력 영역
    input_frame = tk.Frame(win)
    input_frame.pack(fill="x", padx=15, pady=12)

    entry = tk.Entry(input_frame)
    entry.pack(side="left", fill="x", expand=True, padx=5)

    def refresh_list():
        """할 일 목록 새로고침"""

        for widget in list_frame.winfo_children():
            widget.destroy()

        if not todos:
            tk.Label(
                list_frame,
                text="등록된 할 일이 없습니다.",
                fg="gray"
            ).pack(pady=15)
            return

        for todo in todos:
            row = tk.Frame(list_frame)
            row.pack(fill="x", pady=3)

            checked = tk.BooleanVar(value=todo["done"])

            def toggle(item=todo, variable=checked):
                old_value = item["done"]
                item["done"] = variable.get()

                try:
                    save_todos(todos, selected_date)
                except (OSError, csv.Error) as error:
                    item["done"] = old_value
                    variable.set(old_value)
                    messagebox.showerror(
                        "저장 오류", str(error), parent=win
                    )

            tk.Checkbutton(
                row,
                text=todo["title"],
                variable=checked,
                command=toggle,
                anchor="w"
            ).pack(side="left", fill="x", expand=True)

            def delete(item=todo):
                if not messagebox.askyesno(
                    "삭제 확인",
                    "이 할 일을 삭제할까요?",
                    parent=win
                ):
                    return

                todos.remove(item)

                try:
                    save_todos(todos, selected_date)
                    refresh_list()
                except (OSError, csv.Error) as error:
                    todos.append(item)
                    messagebox.showerror(
                        "저장 오류", str(error), parent=win
                    )
                    refresh_list()

            tk.Button(
                row,
                text="삭제",
                command=delete
            ).pack(side="right")

    def add_todo(event=None):
        """새로운 할 일 추가"""

        title = entry.get().strip()

        if not title:
            messagebox.showwarning(
                "입력 확인",
                "할 일 내용을 입력해 주세요.",
                parent=win
            )
            return

        # 기존 CSV에서 ID 확인
        rows = []

        try:
            with open(TODO_CSV, newline="", encoding="utf-8-sig") as file:
                rows = list(csv.DictReader(file))
        except FileNotFoundError:
            pass

        ids = []
        for row in rows:
            try:
                ids.append(int(row["id"]))
            except (ValueError, KeyError, TypeError):
                continue

        new_todo = {
            "id": str(max(ids, default=0) + 1),
            "title": title,
            "done": False
        }

        todos.append(new_todo)

        try:
            save_todos(todos, selected_date)
            entry.delete(0, "end")
            refresh_list()

        except (OSError, csv.Error) as error:
            todos.remove(new_todo)
            messagebox.showerror(
                "저장 오류", str(error), parent=win
            )

    tk.Button(
        input_frame,
        text="추가",
        command=add_todo
    ).pack(side="right")

    entry.bind("<Return>", add_todo)

    refresh_list()
    entry.focus_set()

    return win