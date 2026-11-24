"""새 디자인 화면 모음 (1단계, #97).

홈 화면(달력 + 선택한 날짜 요약)과 함께, 할 일 / 칼로리 / 인바디 / 주간 리포트 화면을
각 담당자가 자기 파일로 옮기기 전까지 임시로 이곳에 둔다.
2단계에서 아래 화면은 각 기능 파일로 옮겨지고, 이 파일에는 홈 화면만 남는다.
    build_todo     -> daily_todo.py
    build_calorie  -> calorie_diary.py
    build_body     -> body_tracker.py
    build_weekly   -> weekly_summary.py

모든 화면은 build_xxx(app, parent) 형태이며 main.App 안에서 그려진다.
저장과 계산은 각 기능 파일의 함수를 그대로 쓰고, 여기서는 화면만 만든다.
"""
import calendar
import csv
import tkinter as tk
import tkinter.font as tkfont
from datetime import date, timedelta
from tkinter import messagebox, ttk

import body_tracker
import calorie_diary
import daily_todo
import ui
import weekly_summary as ws

SAVE_ERRORS = (ValueError, OSError, csv.Error)


# ---------------------------------------------------------------
# 홈 화면
# ---------------------------------------------------------------
CALENDAR_HEAD = ["일", "월", "화", "수", "목", "금", "토"]   # 달력 열 순서 (일요일 시작)


def record_marks():
    """달력에 찍을 표시. {날짜: [(색, 채움 여부), ...]}"""
    marks = {}
    for record in ws.load_calorie_records():
        marks.setdefault(record["date"], {})["calorie"] = True
    for todo in ws.load_todo_records():
        day = marks.setdefault(todo["date"], {})
        day["todo_done"] = day.get("todo_done", True) and todo["done"]
    for record in body_tracker.read_body_records():
        try:
            marks.setdefault(date.fromisoformat(record["date"]), {})["body"] = True
        except ValueError:
            continue
    result = {}
    for day, found in marks.items():
        dots = []
        if "todo_done" in found:
            dots.append((ui.COLOR_TODO, found["todo_done"]))
        if found.get("calorie"):
            dots.append((ui.COLOR_INTAKE, True))
        if found.get("body"):
            dots.append((ui.COLOR_BODY, True))
        result[day] = dots
    return result


class CalendarView(tk.Canvas):
    """월 달력. 날짜를 누르면 app.select(날짜)를 부른다."""

    def __init__(self, parent, app, marks):
        super().__init__(parent, bg=parent["bg"], highlightthickness=0, cursor="hand2")
        self.app, self.marks = app, marks
        self.hover = None
        weeks = calendar.Calendar(firstweekday=6).monthdatescalendar(app.view_year,
                                                                     app.view_month)
        while len(weeks) < 6:       # 항상 6주를 그려 달마다 높이가 바뀌지 않게 한다
            last = weeks[-1][-1]
            weeks.append([last + timedelta(days=i) for i in range(1, 8)])
        self.weeks = weeks
        self.bind("<Configure>", lambda event: self.draw())
        self.bind("<Motion>", self.on_motion)
        self.bind("<Leave>", lambda event: self.set_hover(None))
        self.bind("<Button-1>", self.on_click)

    def layout(self):
        head = ui.px(30)
        return head, self.winfo_width() / 7, (self.winfo_height() - head) / 6

    def day_at(self, x, y):
        head, cell_w, cell_h = self.layout()
        if y < head or cell_w <= 0 or cell_h <= 0:
            return None
        row, column = int((y - head) // cell_h), int(x // cell_w)
        if 0 <= row < 6 and 0 <= column < 7:
            return self.weeks[row][column]
        return None

    def set_hover(self, day):
        if day != self.hover:
            self.hover = day
            self.draw()

    def on_motion(self, event):
        self.set_hover(self.day_at(event.x, event.y))

    def on_click(self, event):
        day = self.day_at(event.x, event.y)
        if day:
            self.app.select(day)

    def draw(self):
        self.delete("all")
        head, cell_w, cell_h = self.layout()
        if cell_w < ui.px(20) or cell_h < ui.px(20):
            return
        today, selected = date.today(), self.app.selected

        for column, name in enumerate(CALENDAR_HEAD):
            color = (ui.COLOR_DANGER if column == 0 else ui.COLOR_BURN if column == 6
                     else ui.COLOR_MUTED)
            self.create_text(cell_w * (column + 0.5), head / 2, text=name,
                             font=ui.FONTS["small"], fill=color)

        for row, week in enumerate(self.weeks):
            for column, day in enumerate(week):
                x0, y0 = cell_w * column, head + cell_h * row
                inside = day.month == self.app.view_month
                gap = ui.px(3)
                if day == selected:
                    ui.round_rect(self, x0 + gap, y0 + gap, x0 + cell_w - gap, y0 + cell_h - gap,
                                  ui.px(10), fill=ui.COLOR_PRIMARY_SOFT, outline=ui.COLOR_PRIMARY,
                                  width=ui.px(1.5))
                elif day == self.hover:
                    ui.round_rect(self, x0 + gap, y0 + gap, x0 + cell_w - gap, y0 + cell_h - gap,
                                  ui.px(10), fill=ui.COLOR_HOVER, outline=ui.COLOR_HOVER)

                center_x, number_y = x0 + cell_w / 2, y0 + cell_h * 0.38
                if day == today:
                    radius = min(ui.px(15), cell_h * 0.3)
                    self.create_oval(center_x - radius, number_y - radius, center_x + radius,
                                     number_y + radius, fill=ui.COLOR_PRIMARY,
                                     outline=ui.COLOR_PRIMARY)
                    color, font = "#ffffff", ui.FONTS["day_bold"]
                else:
                    font = ui.FONTS["day"]
                    if not inside:
                        color = ui.COLOR_FAINT
                    elif column == 0:
                        color = ui.COLOR_DANGER
                    elif column == 6:
                        color = ui.COLOR_BURN
                    else:
                        color = ui.COLOR_TEXT
                self.create_text(center_x, number_y, text=str(day.day), font=font, fill=color)

                dots = self.marks.get(day, [])
                radius, spacing = ui.px(3), ui.px(11)
                dot_y = y0 + cell_h * 0.76
                first = center_x - spacing * (len(dots) - 1) / 2
                for index, (dot_color, filled) in enumerate(dots):
                    x = first + spacing * index
                    if not inside:
                        dot_color = ui.COLOR_FAINT
                    self.create_oval(x - radius, dot_y - radius, x + radius, dot_y + radius,
                                     fill=dot_color if filled else self["bg"],
                                     outline=dot_color, width=ui.px(1.5))


def build_home(app, parent):
    today = date.today()
    hour = app.now().hour
    greeting = "좋은 아침이에요" if hour < 12 else "좋은 오후예요" if hour < 18 else "좋은 저녁이에요"
    ui.page_header(app, parent, greeting,
                   f"오늘은 {today.year}년 {ui.format_day(today)}입니다. 날짜를 눌러 기록을 확인하세요.")

    week = ws.weekly_summary(ws.load_calorie_records(), ws.load_todo_records(), today)
    cal, todo = week["calorie"], week["todo"]
    active_days = sum(1 for day in week["daily"] if day["intake"] or day["burn"])
    ui.tile_row(parent, [
        dict(title="이번 주 섭취", value=f"{cal['intake']:,}", unit="kcal",
             color=ui.COLOR_INTAKE, note=f"{active_days}일 기록"),
        dict(title="이번 주 소모", value=f"{cal['burn']:,}", unit="kcal",
             color=ui.COLOR_BURN, note="운동으로 소모"),
        dict(title="순 칼로리", value=f"{cal['net']:+,}", unit="kcal",
             color=ui.COLOR_PRIMARY, note="섭취 − 소모"),
        dict(title="할 일 완료율", value=f"{todo['rate']}", unit="%",
             color=ui.COLOR_TODO, note=f"{todo['total']}개 중 {todo['done']}개 완료"),
    ]).pack(fill="x", pady=(0, 14))

    main = ui.frame(parent)
    main.pack(fill="both", expand=True)
    side = ui.frame(main, width=ui.px(350))
    side.pack(side="right", fill="y", padx=(14, 0))
    side.pack_propagate(False)

    outer, body = ui.card(main)
    outer.pack(side="left", fill="both", expand=True)
    head = ui.frame(body)
    head.pack(fill="x", pady=(0, 8))
    ui.button(head, "‹", lambda: app.move_month(-1), "soft", padx=12, pady=1,
              font=ui.FONTS["arrow"]).pack(side="left")
    ui.label(head, f"{app.view_year}년 {app.view_month}월", "title", width=12).pack(side="left")
    ui.button(head, "›", lambda: app.move_month(1), "soft", padx=12, pady=1,
              font=ui.FONTS["arrow"]).pack(side="left")
    # 오늘 버튼 (#65): 오늘이 속한 달로 이동하고 오늘 날짜를 선택한다.
    ui.button(head, "오늘", lambda: app.select(today), "soft", padx=12,
              pady=4).pack(side="left", padx=(10, 0), fill="y")
    for text, color in (("인바디", ui.COLOR_BODY), ("칼로리", ui.COLOR_INTAKE),
                        ("할 일", ui.COLOR_TODO)):
        ui.label(head, text, "small").pack(side="right", padx=(3, 8))
        dot = tk.Canvas(head, width=ui.px(8), height=ui.px(8), bg=head["bg"], highlightthickness=0)
        dot.create_oval(1, 1, ui.px(8) - 1, ui.px(8) - 1, fill=color, outline=color)
        dot.pack(side="right")
    CalendarView(body, app, record_marks()).pack(fill="both", expand=True)

    build_day_panel(app, side)


def build_day_panel(app, parent):
    """홈 화면 오른쪽: 선택한 날짜의 할 일, 칼로리, 인바디 요약"""
    day = app.selected
    outer, body = ui.card(parent)
    outer.pack(fill="both", expand=True)

    head = ui.frame(body)
    head.pack(fill="x")
    ui.label(head, ui.format_day(day), "title").pack(side="left")
    if day == date.today():
        tk.Label(head, text="오늘", font=ui.FONTS["small"], bg=ui.COLOR_PRIMARY_SOFT,
                 fg=ui.COLOR_PRIMARY, padx=8, pady=1).pack(side="left", padx=8)

    # --- 할 일 ---
    todos = daily_todo.load_todos(day)
    done = sum(1 for todo in todos if todo["done"])
    section_head(body, "할 일", ui.COLOR_TODO, lambda: app.show("todo"))
    summary = ui.frame(body)
    summary.pack(fill="x")
    ui.ring(summary, round(done / len(todos) * 100) if todos else 0, size=50, width=6,
            color=ui.COLOR_TODO).pack(side="left")
    text = ui.frame(summary)
    text.pack(side="left", padx=12)
    ui.label(text, f"{len(todos)}개 중 {done}개 완료" if todos else "등록된 할 일이 없어요",
             "bold").pack(anchor="w")
    ui.label(text, "항목을 누르면 완료로 바뀝니다" if todos else "아래에 바로 추가해 보세요",
             "small").pack(anchor="w")

    shown = todos[:4]
    for todo in shown:
        todo_row(app, body, day, todos, todo, compact=True)
    if len(todos) > len(shown):
        ui.link(body, f"+ {len(todos) - len(shown)}개 더 보기",
                lambda: app.show("todo")).pack(anchor="w", pady=(4, 0))

    add = ui.frame(body)
    add.pack(fill="x", pady=(8, 0))
    title = tk.StringVar(master=body)
    box = ui.entry(add, title)
    box.pack(side="left", fill="x", expand=True, ipady=5)
    box.bind("<Return>", lambda event: add_todo(app, day, todos, title.get()))
    ui.button(add, "추가", lambda: add_todo(app, day, todos, title.get()), "soft",
              pady=5).pack(side="left", padx=(6, 0))
    app.autofocus(box)

    # --- 칼로리 ---
    totals = calorie_diary.calculate_daily_calorie(day)
    section_head(body, "칼로리", ui.COLOR_INTAKE, lambda: app.show("calorie"))
    row = ui.frame(body)
    row.pack(fill="x")
    for column, (name, value, color) in enumerate((
            ("섭취", f"{totals['intake']:,}", ui.COLOR_INTAKE),
            ("소모", f"{totals['burn']:,}", ui.COLOR_BURN),
            ("순", f"{totals['net']:+,}", ui.COLOR_TEXT))):
        cell = ui.frame(row)
        cell.grid(row=0, column=column, sticky="w")
        row.columnconfigure(column, weight=1, uniform="kcal")
        ui.label(cell, name, "small").pack(anchor="w")
        ui.label(cell, value, "title", color=color).pack(anchor="w")
    balance_bar(body, totals["intake"], totals["burn"]).pack(fill="x", pady=(6, 0))

    # --- 인바디 ---
    record = body_tracker.body_record_for_date(day)
    section_head(body, "인바디", ui.COLOR_BODY, lambda: app.show("body"))
    if record:
        bmi = body_tracker.calculate_bmi(record["height_cm"], record["weight_kg"])
        category = bmi_category(bmi)
        ui.label(body, f"체중 {record['weight_kg']:g} kg  ·  BMI {bmi} ({category})",
                 "bold").pack(anchor="w")
        ui.label(body, f"골격근량 {record['skeletal_muscle_mass_kg']:g} kg  ·  "
                 f"체지방률 {record['body_fat_percentage']:g}%", "small").pack(anchor="w")
    else:
        ui.label(body, "이 날짜의 인바디 기록이 없어요", "small").pack(anchor="w")


def section_head(parent, title, color, on_open):
    ui.divider(parent).pack(fill="x", pady=(14, 10))
    head = ui.frame(parent)
    head.pack(fill="x", pady=(0, 8))
    tk.Frame(head, bg=color, width=ui.px(4), height=ui.px(14)).pack(side="left", padx=(0, 8))
    ui.label(head, title, "h2").pack(side="left")
    ui.link(head, "열기 ›", on_open).pack(side="right")


def balance_bar(parent, intake, burn):
    """섭취와 소모의 비율을 보여주는 얇은 막대"""
    canvas = tk.Canvas(parent, height=ui.px(8), bg=parent["bg"], highlightthickness=0)

    def draw(event=None):
        canvas.delete("all")
        width, height = canvas.winfo_width(), canvas.winfo_height()
        ui.round_rect(canvas, 0, 0, width, height, height / 2, fill=ui.COLOR_TRACK,
                      outline=ui.COLOR_TRACK)
        total = intake + burn
        if total <= 0 or width < 20:
            return
        split = width * intake / total
        if intake:
            ui.round_rect(canvas, 0, 0, max(split, height), height, height / 2,
                          fill=ui.COLOR_INTAKE, outline=ui.COLOR_INTAKE)
        if burn:
            ui.round_rect(canvas, min(split + ui.px(2), width - height), 0, width, height,
                          height / 2, fill=ui.COLOR_BURN, outline=ui.COLOR_BURN)

    canvas.bind("<Configure>", draw)
    return canvas


# ---------------------------------------------------------------
# 할 일 화면 (2단계에서 daily_todo.py로 옮김)
# ---------------------------------------------------------------
def next_todo_id():
    """todo.csv 전체에서 가장 큰 id 다음 번호"""
    ids = []
    try:
        with open(daily_todo.TODO_CSV, newline="", encoding="utf-8-sig") as file:
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
        daily_todo.save_todos(todos, day)
    except SAVE_ERRORS as error:
        app.toast(f"저장하지 못했습니다: {error}", "error")
    app.reload(refocus=True)


def toggle_todo(app, day, todos, item):
    item["done"] = not item["done"]
    try:
        daily_todo.save_todos(todos, day)
    except SAVE_ERRORS as error:
        app.toast(f"저장하지 못했습니다: {error}", "error")
    app.reload()


def delete_todo(app, day, todos, item):
    if not messagebox.askyesno("삭제 확인", f"'{item['title']}'을(를) 삭제할까요?",
                               parent=app.root):
        return
    todos.remove(item)
    try:
        daily_todo.save_todos(todos, day)
        app.toast("할 일을 삭제했습니다.")
    except SAVE_ERRORS as error:
        app.toast(f"저장하지 못했습니다: {error}", "error")
    app.reload()


def todo_row(app, parent, day, todos, todo, compact=False):
    """할 일 한 줄. 체크 상자나 글자를 누르면 완료 여부가 바뀐다."""
    row = ui.frame(parent)
    row.pack(fill="x", pady=(6, 0) if compact else 0, ipady=0 if compact else 7)

    def toggle(event=None):
        toggle_todo(app, day, todos, todo)

    ui.check(row, todo["done"], toggle).pack(side="left", padx=(0 if compact else 4, 10))
    font = tkfont.Font(family=ui.FONT_FAMILY, size=10, overstrike=todo["done"])
    text = tk.Label(row, text=todo["title"], font=font, bg=row["bg"], anchor="w", cursor="hand2",
                    fg=ui.COLOR_FAINT if todo["done"] else ui.COLOR_TEXT)
    text.pack(side="left", fill="x", expand=True)
    text.bind("<Button-1>", toggle)
    if not compact:
        ui.button(row, "삭제", lambda: delete_todo(app, day, todos, todo), "danger",
                  font=ui.FONTS["small"], padx=8, pady=2).pack(side="right", padx=4)
    return row


def build_todo(app, parent):
    day = app.selected
    todos = daily_todo.load_todos(day)
    done = sum(1 for todo in todos if todo["done"])
    rate = round(done / len(todos) * 100) if todos else 0
    ui.page_header(app, parent, "할 일", f"{ui.format_day(day)}에 할 일을 정리하세요.", step=1)

    outer, body = ui.card(parent)
    outer.pack(fill="x", pady=(0, 14))
    ui.ring(body, rate, size=72, width=8, color=ui.COLOR_TODO).pack(side="left")
    text = ui.frame(body)
    text.pack(side="left", padx=16)
    ui.label(text, f"{len(todos)}개 중 {done}개 완료" if todos else "아직 할 일이 없어요",
             "title").pack(anchor="w")
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
        side="left", padx=(8, 0))
    app.autofocus(box, always=True)

    outer, body = ui.card(parent, "할 일 목록")
    outer.pack(fill="both", expand=True)
    if not todos:
        ui.empty_state(body, "등록된 할 일이 없습니다",
                       "위 입력란에 내용을 적고 추가해 보세요.").pack(expand=True)
        return
    scroll = ui.ScrollFrame(body)
    scroll.pack(fill="both", expand=True)
    for index, todo in enumerate(sorted(todos, key=lambda item: item["done"])):
        if index:
            ui.divider(scroll.body).pack(fill="x")
        todo_row(app, scroll.body, day, todos, todo)


# ---------------------------------------------------------------
# 칼로리 화면 (2단계에서 calorie_diary.py로 옮김)
# ---------------------------------------------------------------
def build_calorie(app, parent):
    day = app.selected
    records = calorie_diary.records_for_date(day)
    totals = calorie_diary.calorie_totals(records)
    ui.page_header(app, parent, "칼로리", f"{ui.format_day(day)}의 식단과 운동을 기록하세요.", step=1)

    ui.tile_row(parent, [
        dict(title="섭취", value=f"{totals['intake']:,}", unit="kcal", color=ui.COLOR_INTAKE,
             note=f"식단 {sum(1 for r in records if r['type'] == 'intake')}건"),
        dict(title="소모", value=f"{totals['burn']:,}", unit="kcal", color=ui.COLOR_BURN,
             note=f"운동 {sum(1 for r in records if r['type'] == 'burn')}건"),
        dict(title="순 칼로리", value=f"{totals['net']:+,}", unit="kcal", color=ui.COLOR_PRIMARY,
             note="섭취 − 소모"),
    ]).pack(fill="x", pady=(0, 14))

    main = ui.frame(parent)
    main.pack(fill="both", expand=True)
    form_outer, form = ui.card(main)
    form_outer.pack(side="left", fill="y")
    list_outer, listing = ui.card(main, "기록 목록")
    list_outer.pack(side="left", fill="both", expand=True, padx=(14, 0))

    # --- 입력 양식 (추가와 수정에 같이 쓴다) ---
    editing = {"id": None}
    kind = tk.StringVar(master=form, value="intake")
    name = tk.StringVar(master=form)
    kcal = tk.StringVar(master=form)

    form_title = ui.label(form, "새 기록", "h2")
    form_title.pack(anchor="w", pady=(0, 10))
    switch = ui.segmented(form, [("intake", "식단 (섭취)"), ("burn", "운동 (소모)")], kind)
    switch.pack(fill="x")
    ui.label(form, "기록 이름", "small").pack(anchor="w", pady=(14, 4))
    name_box = ui.entry(form, name, width=30)
    name_box.pack(fill="x", ipady=7)
    ui.label(form, "칼로리 (kcal)", "small").pack(anchor="w", pady=(12, 4))
    kcal_box = ui.entry(form, kcal)
    kcal_box.pack(fill="x", ipady=7)

    def submit(event=None):
        try:
            if editing["id"] is None:
                calorie_diary.save_calorie_record(day, kind.get(), name.get(), kcal.get())
                message = "기록을 추가했습니다."
            else:
                calorie_diary.update_calorie_record(editing["id"], kind.get(), name.get(),
                                                    kcal.get())
                message = "기록을 수정했습니다."
        except SAVE_ERRORS as error:
            app.toast(str(error), "error")
            return
        app.reload(refocus=True)
        app.toast(message)

    def stop_editing():
        editing["id"] = None
        kind.set("intake")
        name.set("")
        kcal.set("")
        switch.refresh()
        form_title.config(text="새 기록")
        save_button.config(text="기록 추가")
        cancel_button.pack_forget()

    save_button = ui.button(form, "기록 추가", submit)
    save_button.pack(fill="x", pady=(18, 0))
    cancel_button = ui.button(form, "수정 취소", stop_editing, "soft")
    for box in (name_box, kcal_box):
        box.bind("<Return>", submit)
    app.autofocus(name_box, always=True)

    # --- 기록 목록 ---
    if not records:
        ui.empty_state(listing, "이 날짜의 기록이 없습니다",
                       "왼쪽에서 식단이나 운동을 추가해 보세요.").pack(expand=True)
        return

    actions = ui.frame(listing)
    actions.pack(side="bottom", fill="x", pady=(10, 0))
    table = ttk.Treeview(listing, columns=("type", "name", "kcal"), show="headings",
                         selectmode="browse")
    for column, text, width, anchor in (("type", "구분", 110, "w"), ("name", "이름", 260, "w"),
                                        ("kcal", "칼로리", 100, "e")):
        table.heading(column, text=text, anchor=anchor)
        table.column(column, width=ui.px(width), anchor=anchor, stretch=column == "name")
    table.tag_configure("intake", foreground=ui.COLOR_TEXT)
    table.tag_configure("burn", foreground=ui.COLOR_BURN)
    for record in records:
        table.insert("", "end", iid=str(record["id"]), tags=(record["type"],), values=(
            calorie_diary.TYPE_LABELS.get(record["type"], record["type"]), record["name"],
            f"{record['kcal']:,} kcal"))
    table.pack(fill="both", expand=True)

    def selected_record():
        chosen = table.selection()
        if not chosen:
            app.toast("목록에서 기록을 먼저 선택해 주세요.", "error")
            return None
        return next(r for r in records if str(r["id"]) == chosen[0])

    def start_editing(event=None):
        record = selected_record()
        if record is None:
            return
        editing["id"] = record["id"]
        kind.set(record["type"])
        name.set(record["name"])
        kcal.set(str(record["kcal"]))
        switch.refresh()
        form_title.config(text="기록 수정")
        save_button.config(text="수정 저장")
        cancel_button.pack(fill="x", pady=(8, 0))
        name_box.focus_set()

    def delete():
        record = selected_record()
        if record is None or not messagebox.askyesno(
                "삭제 확인", f"'{record['name']}' 기록을 삭제할까요?", parent=app.root):
            return
        try:
            calorie_diary.delete_calorie_record(record["id"])
        except SAVE_ERRORS as error:
            app.toast(str(error), "error")
            return
        app.reload()
        app.toast("기록을 삭제했습니다.")

    table.bind("<Double-1>", start_editing)
    ui.label(actions, "두 번 누르면 수정할 수 있어요", "small").pack(side="left")
    ui.button(actions, "삭제", delete, "danger").pack(side="right")
    ui.button(actions, "선택한 기록 수정", start_editing, "soft").pack(side="right", padx=6)


# ---------------------------------------------------------------
# 인바디 화면 (2단계에서 body_tracker.py로 옮김)
# ---------------------------------------------------------------
BMI_SEGMENTS = [(18.5, ui.COLOR_BURN, "저체중"), (23, ui.COLOR_TODO, "정상"),
                (25, ui.COLOR_INTAKE, "과체중"), (35, ui.COLOR_DANGER, "비만")]


def bmi_category(bmi):
    for limit, _, name in BMI_SEGMENTS:
        if bmi < limit:
            return name
    return BMI_SEGMENTS[-1][2]


def build_body(app, parent):
    day = app.selected
    ui.page_header(app, parent, "인바디", f"{ui.format_day(day)}의 신체 수치를 기록하세요.", step=1)

    latest = {}     # 날짜별 가장 최근 기록
    for record in sorted(body_tracker.read_body_records(), key=lambda r: r["id"]):
        latest[record["date"]] = record
    history = [latest[key] for key in sorted(latest)]
    current = latest.get(day.isoformat())
    earlier = [r for r in history if r["date"] < day.isoformat()]
    shown = current or (earlier[-1] if earlier else None)
    # 이전 기록 찾기와 변화량 계산은 기존 함수(previous_body_record, calculate_change)를 쓴다.
    previous = (body_tracker.previous_body_record(date.fromisoformat(shown["date"]))
                if shown else None)

    def change(key, unit):
        if not shown or not previous:
            return "이전 기록 없음"
        diff, rate = body_tracker.calculate_change(shown[key], previous[key])
        if abs(diff) < 0.05:
            return "이전 기록과 같음"
        rate_text = "" if rate is None else f" ({rate:+.1f}%)"
        return f"이전보다 {'▲' if diff > 0 else '▼'} {abs(diff):.1f}{unit}{rate_text}"

    def value(key):
        return f"{shown[key]:g}" if shown else "–"

    bmi = body_tracker.calculate_bmi(shown["height_cm"], shown["weight_kg"]) if shown else None
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
            body_tracker.save_body_record(day, *(inputs[key].get() for key, _ in fields))
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


# ---------------------------------------------------------------
# 주간 리포트 화면 (2단계에서 weekly_summary.py로 옮김)
# ---------------------------------------------------------------
def build_weekly(app, parent):
    day = app.selected
    summary = ws.weekly_summary(ws.load_calorie_records(), ws.load_todo_records(), day)
    cal, todo, daily = summary["calorie"], summary["todo"], summary["daily"]
    ui.page_header(app, parent, "주간 리포트", "한 주의 칼로리와 할 일을 한눈에 돌아보세요.", step=7,
                   week_range=ws.get_week_range)

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
