"""선택한 날짜의 할 일을 조회하고 추가·완료·삭제 및 수정한다."""
import csv
import tkinter as tk
import tkinter.font as tkfont
from tkinter import messagebox

import ui
from config import TODO_CSV, TODO_HEADER

SAVE_ERRORS = (ValueError, OSError, csv.Error)


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
                        "done": row["done"].lower() == "true",
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
            "done": str(todo["done"]),
        })

    with open(TODO_CSV, "w", newline="", encoding="utf-8-sig") as file:
        writer = csv.DictWriter(file, fieldnames=TODO_HEADER)
        writer.writeheader()
        writer.writerows(rows)


def next_todo_id():
    """todo.csv 전체에서 가장 큰 id 다음 번호"""
    ids = []
    try:
        with open(TODO_CSV, newline="", encoding="utf-8-sig") as file:
            for row in csv.DictReader(file):
                try:
                    ids.append(int(row["id"]))
                except (KeyError, TypeError, ValueError):
                    continue
    except FileNotFoundError:
        pass
    return str(max(ids, default=0) + 1)


def add_todo(app, day, todos, title):
    title = title.strip()
    if not title:
        app.toast("할 일 내용을 입력해 주세요.", "error")
        return
    todos.append({"id": next_todo_id(), "title": title, "done": False})
    try:
        save_todos(todos, day)
    except SAVE_ERRORS as error:
        app.toast(f"저장하지 못했습니다: {error}", "error")
    app.reload(refocus=True)


def toggle_todo(app, day, todos, item):
    item["done"] = not item["done"]
    try:
        save_todos(todos, day)
    except SAVE_ERRORS as error:
        app.toast(f"저장하지 못했습니다: {error}", "error")
    app.reload()


def start_edit_todo(app, item):
    app.editing_todo_id = item["id"]
    app.reload()


def cancel_edit_todo(app):
    app.editing_todo_id = None
    app.reload()


def save_edit_todo(app, day, todos, item, new_title):
    cleaned = new_title.strip()
    if not cleaned:
        app.toast("할 일 내용을 입력해 주세요.", "error")
        return
    old_title = item["title"]
    item["title"] = cleaned
    try:
        save_todos(todos, day)
        app.editing_todo_id = None
        app.toast("할 일을 수정했습니다.")
    except SAVE_ERRORS as error:
        item["title"] = old_title
        app.toast(f"저장하지 못했습니다: {error}", "error")
    app.reload()


def delete_todo(app, day, todos, item):
    if not messagebox.askyesno(
        "삭제 확인", f"'{item['title']}'을(를) 삭제할까요?", parent=app.root
    ):
        return
    if getattr(app, "editing_todo_id", None) == item["id"]:
        app.editing_todo_id = None
    todos.remove(item)
    try:
        save_todos(todos, day)
        app.toast("할 일을 삭제했습니다.")
    except SAVE_ERRORS as error:
        app.toast(f"저장하지 못했습니다: {error}", "error")
    app.reload()


def todo_row(app, parent, day, todos, todo, compact=False):
    """할 일 한 줄. 체크 상자나 글자를 누르면 완료 여부가 바뀐다."""
    row = ui.frame(parent)
    row.pack(fill="x", pady=(6, 0) if compact else 0, ipady=0 if compact else 7)

    is_editing = (not compact) and (getattr(app, "editing_todo_id", None) == todo["id"])
    if is_editing:
        edit_var = tk.StringVar(master=row, value=todo["title"])
        edit_box = ui.entry(row, edit_var)
        edit_box.pack(side="left", fill="x", expand=True, padx=(4, 8), ipady=4)
        edit_box.focus_set()
        edit_box.bind(
            "<Return>", lambda event: save_edit_todo(app, day, todos, todo, edit_var.get())
        )
        edit_box.bind("<Escape>", lambda event: cancel_edit_todo(app))
        ui.button(
            row, "취소", lambda: cancel_edit_todo(app), "soft", font=ui.FONTS["small"], padx=8, pady=2
        ).pack(side="right")
        ui.button(
            row,
            "저장",
            lambda: save_edit_todo(app, day, todos, todo, edit_var.get()),
            font=ui.FONTS["small"],
            padx=8,
            pady=2,
        ).pack(side="right", padx=(0, 4))
        return row

    def toggle(event=None):
        toggle_todo(app, day, todos, todo)

    ui.check(row, todo["done"], toggle).pack(side="left", padx=(0 if compact else 4, 10))
    font = tkfont.Font(family=ui.FONT_FAMILY, size=10, overstrike=todo["done"])
    text = tk.Label(
        row,
        text=todo["title"],
        font=font,
        bg=row["bg"],
        anchor="w",
        cursor="hand2",
        fg=ui.COLOR_FAINT if todo["done"] else ui.COLOR_TEXT,
    )
    text.pack(side="left", fill="x", expand=True)
    text.bind("<Button-1>", toggle)
    if not compact:
        ui.button(
            row,
            "삭제",
            lambda: delete_todo(app, day, todos, todo),
            "danger",
            font=ui.FONTS["small"],
            padx=8,
            pady=2,
        ).pack(side="right", padx=4)
        ui.button(
            row,
            "수정",
            lambda: start_edit_todo(app, todo),
            "soft",
            font=ui.FONTS["small"],
            padx=8,
            pady=2,
        ).pack(side="right")
    return row


def build_todo(app, parent):
    day = app.selected
    todos = load_todos(day)
    done = sum(1 for todo in todos if todo["done"])
    rate = round(done / len(todos) * 100) if todos else 0
    ui.page_header(app, parent, "할 일", f"{ui.format_day(day)}에 할 일을 정리하세요.", step=1)

    outer, body = ui.card(parent)
    outer.pack(fill="x", pady=(0, 14))
    ui.ring(body, rate, size=72, width=8, color=ui.COLOR_TODO).pack(side="left")
    text = ui.frame(body)
    text.pack(side="left", padx=16)
    ui.label(
        text, f"{len(todos)}개 중 {done}개 완료" if todos else "아직 할 일이 없어요", "title"
    ).pack(anchor="w")
    remaining = len(todos) - done
    if not todos:
        hint = "오른쪽에 할 일을 적고 Enter를 눌러 추가하세요."
    elif remaining:
        hint = f"{remaining}개 남았습니다. 하나씩 끝내 봐요."
    else:
        hint = "오늘 할 일을 모두 끝냈습니다!"
    ui.label(text, hint, "muted").pack(anchor="w")

    add = ui.frame(body)
    add.pack(side="right")
    title = tk.StringVar(master=body)
    box = ui.entry(add, title, width=34)
    box.pack(side="left", ipady=7)
    box.bind("<Return>", lambda event: add_todo(app, day, todos, title.get()))
    ui.button(add, "+ 추가", lambda: add_todo(app, day, todos, title.get())).pack(
        side="left", padx=(8, 0)
    )
    app.autofocus(box, always=True)

    outer, body = ui.card(parent, "할 일 목록")
    outer.pack(fill="both", expand=True)
    if not todos:
        ui.empty_state(
            body, "등록된 할 일이 없습니다", "위 입력란에 내용을 적고 추가해 보세요."
        ).pack(expand=True)
        return
    scroll = ui.ScrollFrame(body)
    scroll.pack(fill="both", expand=True)
    for index, todo in enumerate(sorted(todos, key=lambda item: item["done"])):
        if index:
            ui.divider(scroll.body).pack(fill="x")
        todo_row(app, scroll.body, day, todos, todo)