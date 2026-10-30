"""날짜별 할 일과 메모를 관리하는 간단한 Tkinter 앱.

필요한 라이브러리: Python 표준 라이브러리(tkinter 포함)
기록 위치: 사용자 홈 디렉터리의 HealthLog/records.json
"""

import calendar
import datetime as dt
import json
import os
from pathlib import Path
import re
import tempfile
import tkinter as tk
from tkinter import font as tkfont
from tkinter import messagebox, ttk
from uuid import uuid4


COLORS = {
    "bg": "#F2F9F7",
    "header": "#E4F4F3",
    "white": "#FFFFFF",
    "ink": "#294755",
    "muted": "#718A90",
    "line": "#DCECE7",
    "blue_light": "#DDF1F8",
    "blue": "#478CA5",
    "green_light": "#DDF2DF",
    "green": "#59A976",
    "green_dark": "#43885C",
    "row": "#F6FAF9",
    "other": "#F5F9F8",
    "other_text": "#A9BBB8",
    "red": "#AD6666",
}
WEEKDAYS = ("월", "화", "수", "목", "금", "토", "일")
DEFAULT_STORAGE = Path.home() / "HealthLog" / "records.json"


def month_weeks(year, month):
    """해당 월의 날짜가 하나 이상 포함된 주만 반환한다(월요일 시작)."""
    return calendar.Calendar(firstweekday=0).monthdatescalendar(year, month)


def shift_month(date, delta):
    """월을 이동하며 새 달에 없는 날짜는 그 달의 마지막 날로 맞춘다."""
    year, month_zero = divmod(date.year * 12 + date.month - 1 + delta, 12)
    month = month_zero + 1
    day = min(date.day, calendar.monthrange(year, month)[1])
    return dt.date(year, month, day)


def parse_optional_time(value):
    """빈 값 또는 24시간 형식(HH:MM)을 검사하고 정규화한다."""
    value = value.strip()
    if not value:
        return None
    match = re.fullmatch(r"([01]?\d|2[0-3]):([0-5]\d)", value)
    if not match:
        raise ValueError("시간은 24시간 형식으로 입력해 주세요. 예: 09:30, 14:00")
    return f"{int(match.group(1)):02d}:{match.group(2)}"


def _validate_records(records):
    if not isinstance(records, dict):
        raise ValueError("기록 데이터 형식이 올바르지 않습니다.")
    for date_string, items in records.items():
        if not isinstance(date_string, str):
            raise ValueError("날짜 형식이 올바르지 않습니다.")
        try:
            parsed = dt.date.fromisoformat(date_string)
        except ValueError as exc:
            raise ValueError("날짜 형식이 올바르지 않습니다.") from exc
        if parsed.isoformat() != date_string or not isinstance(items, list):
            raise ValueError("날짜별 기록 형식이 올바르지 않습니다.")
        seen_ids = set()
        for item in items:
            if not isinstance(item, dict):
                raise ValueError("항목 형식이 올바르지 않습니다.")
            if not isinstance(item.get("id"), str) or not item["id"] or item["id"] in seen_ids:
                raise ValueError("항목 ID가 올바르지 않습니다.")
            seen_ids.add(item["id"])
            if item.get("kind") not in ("todo", "memo"):
                raise ValueError("항목 종류가 올바르지 않습니다.")
            if not isinstance(item.get("text"), str) or not item["text"].strip():
                raise ValueError("항목 내용이 올바르지 않습니다.")
            if not isinstance(item.get("done"), bool):
                raise ValueError("완료 상태가 올바르지 않습니다.")
            time = item.get("time")
            if time is not None and (not isinstance(time, str) or parse_optional_time(time) != time):
                raise ValueError("저장된 시간 형식이 올바르지 않습니다.")


def load_records(path):
    path = Path(path)
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as file:
        data = json.load(file)
    if not isinstance(data, dict) or data.get("version") != 1:
        raise ValueError("지원하지 않는 기록 파일 형식입니다.")
    records = data.get("records")
    _validate_records(records)
    return records


def save_records(path, records):
    """임시 파일에 쓴 뒤 교체하여 저장 중 원본 손상을 줄인다."""
    path = Path(path)
    _validate_records(records)
    path.parent.mkdir(parents=True, exist_ok=True)
    temp_name = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", dir=path.parent,
            prefix=".health_log_", suffix=".tmp", delete=False,
        ) as file:
            temp_name = file.name
            json.dump({"version": 1, "records": records}, file, ensure_ascii=False, indent=2)
            file.write("\n")
        os.replace(temp_name, path)
        temp_name = None
    finally:
        if temp_name is not None:
            try:
                os.remove(temp_name)
            except OSError:
                pass


class ScrollableFrame(tk.Frame):
    """기록이 길어질 때 사용할 수직 스크롤 영역."""

    def __init__(self, parent, bg):
        super().__init__(parent, bg=bg)
        self.canvas = tk.Canvas(self, bg=bg, highlightthickness=0, bd=0)
        self.scrollbar = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        self.content = tk.Frame(self.canvas, bg=bg)
        self.window_id = self.canvas.create_window((0, 0), window=self.content, anchor="nw")
        self.content.bind("<Configure>", self._update_scrollregion)
        self.canvas.bind("<Configure>", self._resize_content)
        self.enable_scroll(self.canvas, self.content)

    def _update_scrollregion(self, event=None):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _resize_content(self, event):
        self.canvas.itemconfigure(self.window_id, width=event.width)

    def enable_scroll(self, *widgets):
        for widget in widgets:
            widget.bind("<MouseWheel>", self._scroll)
            widget.bind("<Button-4>", self._scroll)
            widget.bind("<Button-5>", self._scroll)

    def _scroll(self, event):
        if getattr(event, "num", None) == 4:
            direction = -1
        elif getattr(event, "num", None) == 5:
            direction = 1
        elif event.delta:
            direction = -1 if event.delta > 0 else 1
        else:
            return "break"
        self.canvas.yview_scroll(direction, "units")
        return "break"


class MainApplication(tk.Tk):
    def __init__(self, storage_path=DEFAULT_STORAGE):
        super().__init__()
        self.title("Health Log")
        self.geometry("1120x720")
        self.minsize(960, 620)
        self.configure(bg=COLORS["bg"])
        self.storage_path = Path(storage_path)
        self.storage_readable = True
        self.selected_date = dt.date.today()
        self.current_page = "calendar"
        self.editing_id = None
        self.records = {}
        self.font_family = self._find_font()
        self.kind_var = tk.StringVar(value="할 일")
        self.text_var = tk.StringVar()
        self.time_var = tk.StringVar()
        self.nav_buttons = {}
        self.active_scroll = None

        self._configure_combobox_style()
        self._load_data()
        self._build_header()
        self.body = tk.Frame(self, bg=COLORS["bg"])
        self.body.pack(fill="both", expand=True, padx=20, pady=16)
        self.show_calendar_page()

    def _find_font(self):
        available = set(tkfont.families(self))
        for name in ("맑은 고딕", "Malgun Gothic", "Apple SD Gothic Neo", "Noto Sans CJK KR"):
            if name in available:
                return name
        return "TkDefaultFont"

    def _font(self, size, *styles):
        return (self.font_family, size, *styles)

    def _configure_combobox_style(self):
        style = ttk.Style(self)
        if "clam" in style.theme_names():
            style.theme_use("clam")
        style.configure(
            "Health.TCombobox", padding=5, fieldbackground=COLORS["white"],
            background=COLORS["blue_light"], foreground=COLORS["ink"],
            bordercolor=COLORS["line"], arrowcolor=COLORS["blue"],
        )
        style.map(
            "Health.TCombobox", fieldbackground=[("readonly", COLORS["white"])],
            selectbackground=[("readonly", COLORS["white"])],
            selectforeground=[("readonly", COLORS["ink"])],
        )

    def _load_data(self):
        try:
            self.records = load_records(self.storage_path)
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            # 읽을 수 없는 파일은 덮어쓰지 않는다.
            self.storage_readable = False
            self.records = {}
            messagebox.showerror(
                "저장된 기록을 읽을 수 없어요",
                f"기존 파일을 보호하기 위해 자동 저장을 중지합니다.\n"
                f"파일을 확인한 후 앱을 다시 실행해 주세요.\n\n"
                f"위치: {self.storage_path}\n이유: {exc}", parent=self,
            )

    def _save_data(self):
        if not self.storage_readable:
            messagebox.showwarning(
                "자동 저장이 중지되어 있어요",
                "기록 파일을 읽지 못해 현재 변경 사항을 저장할 수 없습니다.\n"
                "기존 파일을 확인한 뒤 앱을 다시 실행해 주세요.", parent=self,
            )
            return False
        try:
            save_records(self.storage_path, self.records)
            return True
        except (OSError, ValueError) as exc:
            messagebox.showerror(
                "저장하지 못했어요",
                f"변경 내용은 현재 실행 중에만 유지됩니다. 저장 위치와 권한을 확인해 주세요.\n\n"
                f"위치: {self.storage_path}\n이유: {exc}", parent=self,
            )
            return False

    def _button(self, parent, text, command, *, bg=None, fg=None, size=10, bold=False, padx=11, pady=6):
        bg = bg or COLORS["white"]
        fg = fg or COLORS["ink"]
        return tk.Button(
            parent, text=text, command=command, font=self._font(size, *(('bold',) if bold else ())),
            bg=bg, fg=fg, activebackground=COLORS["blue_light"], activeforeground=COLORS["ink"],
            relief="flat", bd=0, highlightthickness=0, padx=padx, pady=pady, cursor="hand2",
        )

    def _build_header(self):
        header = tk.Frame(self, bg=COLORS["header"])
        header.pack(fill="x")
        tk.Label(
            header, text="HEALTH LOG", font=self._font(16, "bold"),
            bg=COLORS["header"], fg=COLORS["ink"],
        ).pack(side="left", padx=(20, 22), pady=12)
        nav = tk.Frame(header, bg=COLORS["header"])
        nav.pack(side="left", fill="x", expand=True)
        pages = [
            ("calendar", "오늘의 달력", self.show_calendar_page),
            ("todo", "오늘의 할 일", self.show_todo_page),
            ("calorie", "칼로리 다이어리", lambda: self.show_empty_page("calorie", "칼로리 다이어리")),
            ("report", "주간 건강 리포트", lambda: self.show_empty_page("report", "주간 건강 리포트")),
            ("profile", "내 정보", lambda: self.show_empty_page("profile", "내 정보")),
        ]
        for key, label, action in pages:
            button = self._button(nav, label, action, bg=COLORS["header"], fg=COLORS["muted"], size=9, bold=True, padx=10)
            button.pack(side="left", padx=(0, 4))
            self.nav_buttons[key] = button

    def _clear_page(self, name):
        self.current_page = name
        for key, button in self.nav_buttons.items():
            active = key == name
            button.configure(
                bg=COLORS["blue_light"] if active else COLORS["header"],
                fg=COLORS["blue"] if active else COLORS["muted"],
            )
        self.active_scroll = None
        for child in self.body.winfo_children():
            child.destroy()

    def _card(self, parent):
        return tk.Frame(
            parent, bg=COLORS["white"], highlightthickness=1,
            highlightbackground=COLORS["line"], highlightcolor=COLORS["line"],
        )

    def _items(self, date=None):
        return self.records.get((date or self.selected_date).isoformat(), [])

    @staticmethod
    def _ordered(items):
        # 시간이 있는 항목은 시각 순서, 없는 항목은 추가한 순서대로 표시한다.
        return sorted(items, key=lambda item: item.get("time") or "99:99")

    def _redraw(self, preserve_scroll=True):
        position = None
        if preserve_scroll and self.active_scroll is not None:
            position = self.active_scroll.canvas.yview()[0]
        if self.current_page == "calendar":
            self.show_calendar_page()
        elif self.current_page == "todo":
            self.show_todo_page()
        if position is not None and self.active_scroll is not None:
            self.update_idletasks()
            self.active_scroll.canvas.yview_moveto(position)

    def set_date(self, date):
        if not isinstance(date, dt.date):
            raise TypeError("date must be a datetime.date")
        if date != self.selected_date and self.editing_id is not None:
            self.cancel_edit(redraw=False)
        self.selected_date = date
        self._redraw(preserve_scroll=False)

    def _change_day(self, amount):
        try:
            self.set_date(self.selected_date + dt.timedelta(days=amount))
        except OverflowError:
            pass

    def _change_month(self, amount):
        try:
            self.set_date(shift_month(self.selected_date, amount))
        except (ValueError, OverflowError):
            pass

    def _date_selectors(self, parent, *, show_month_arrows=False):
        """연도/월 선택 시 기존 일이 없는 달이면 말일로 보정한다."""
        line = tk.Frame(parent, bg=COLORS["white"])
        line.pack()
        if show_month_arrows:
            self._button(line, "‹", lambda: self._change_month(-1), bg=COLORS["row"], size=15, padx=10, pady=1).pack(side="left", padx=(0, 8))
        year_var = tk.StringVar(value=f"{self.selected_date.year}년")
        month_var = tk.StringVar(value=f"{self.selected_date.month}월")
        years = tuple(f"{year}년" for year in range(1900, 2101))
        months = tuple(f"{month}월" for month in range(1, 13))
        year_box = ttk.Combobox(line, textvariable=year_var, values=years, state="readonly", width=7, style="Health.TCombobox", font=self._font(10))
        month_box = ttk.Combobox(line, textvariable=month_var, values=months, state="readonly", width=5, style="Health.TCombobox", font=self._font(10))
        year_box.pack(side="left", padx=(0, 6))
        month_box.pack(side="left")

        def on_change(event=None):
            year = int(year_var.get()[:-1])
            month = int(month_var.get()[:-1])
            day = min(self.selected_date.day, calendar.monthrange(year, month)[1])
            self.set_date(dt.date(year, month, day))

        year_box.bind("<<ComboboxSelected>>", on_change)
        month_box.bind("<<ComboboxSelected>>", on_change)
        if show_month_arrows:
            self._button(line, "›", lambda: self._change_month(1), bg=COLORS["row"], size=15, padx=10, pady=1).pack(side="left", padx=(8, 0))
        return line

    def show_calendar_page(self):
        self._clear_page("calendar")
        self.body.grid_rowconfigure(0, weight=1)
        self.body.grid_columnconfigure(0, weight=7, uniform="columns")
        self.body.grid_columnconfigure(1, weight=3, uniform="columns")

        calendar_card = self._card(self.body)
        calendar_card.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        main = tk.Frame(calendar_card, bg=COLORS["white"])
        main.pack(fill="both", expand=True, padx=14, pady=14)
        controls = tk.Frame(main, bg=COLORS["white"])
        controls.pack(fill="x", pady=(0, 12))
        self._date_selectors(controls, show_month_arrows=True)

        weekdays = tk.Frame(main, bg=COLORS["white"])
        weekdays.pack(fill="x", pady=(0, 3))
        for column, name in enumerate(WEEKDAYS):
            weekdays.grid_columnconfigure(column, weight=1, uniform="weekdays")
            tk.Label(
                weekdays, text=name, font=self._font(9, "bold"), bg=COLORS["white"],
                fg=COLORS["blue"] if column >= 5 else COLORS["muted"], pady=4,
            ).grid(row=0, column=column, sticky="ew")

        grid = tk.Frame(main, bg=COLORS["line"])
        grid.pack(fill="both", expand=True)
        weeks = month_weeks(self.selected_date.year, self.selected_date.month)
        for column in range(7):
            grid.grid_columnconfigure(column, weight=1, uniform="days")
        for row, week in enumerate(weeks):
            grid.grid_rowconfigure(row, weight=1, uniform="weeks")
            for column, date in enumerate(week):
                self._calendar_cell(grid, date, row, column)

        summary_card = self._card(self.body)
        summary_card.grid(row=0, column=1, sticky="nsew")
        self._build_summary(summary_card)

    def _calendar_cell(self, parent, date, row, column):
        in_month = date.month == self.selected_date.month
        selected = date == self.selected_date
        bg = COLORS["green_light"] if selected else (COLORS["white"] if in_month else COLORS["other"])
        fg = COLORS["ink"] if in_month else COLORS["other_text"]
        cell = tk.Frame(parent, bg=bg, cursor="hand2")
        cell.grid(row=row, column=column, sticky="nsew", padx=(0, 1), pady=(0, 1))
        day_title = str(date.day)
        if date == dt.date.today():
            day_title += " · 오늘"
        day_label = tk.Label(cell, text=day_title, font=self._font(9, "bold"), bg=bg, fg=COLORS["green_dark"] if selected else fg, anchor="w")
        day_label.pack(fill="x", padx=5, pady=(3, 1))
        parts = [cell, day_label]
        items = self._ordered(self._items(date))
        for item in items[:2]:
            prefix = "✓ " if item["kind"] == "todo" and item["done"] else "· "
            text = item["text"].replace("\n", " ")
            if len(text) > 7:
                text = text[:7] + "…"
            item_color = COLORS["other_text"] if not in_month or item["done"] else COLORS["ink"]
            label = tk.Label(cell, text=prefix + text, font=self._font(8), bg=bg, fg=item_color, anchor="w")
            label.pack(fill="x", padx=5)
            parts.append(label)
        if len(items) > 2:
            more = tk.Label(cell, text=f"+{len(items) - 2}개", font=self._font(8), bg=bg, fg=COLORS["blue"], anchor="w")
            more.pack(fill="x", padx=5)
            parts.append(more)
        for widget in parts:
            widget.bind("<Button-1>", lambda event, chosen=date: self.set_date(chosen))

    def _build_summary(self, card):
        inner = tk.Frame(card, bg=COLORS["white"])
        inner.pack(fill="both", expand=True, padx=16, pady=16)
        date = self.selected_date
        date_text = f"{date.month}월 {date.day}일 {WEEKDAYS[date.weekday()]}요일"
        tk.Label(inner, text=date_text, font=self._font(13, "bold"), bg=COLORS["white"], fg=COLORS["ink"]).pack(anchor="w")
        items = self._items()
        todo_items = [item for item in items if item["kind"] == "todo"]
        done_count = sum(item["done"] for item in todo_items)
        tk.Label(
            inner, text=f"할 일 {len(todo_items)}개 중 {done_count}개 완료 · 기록 {len(items)}개",
            font=self._font(9), bg=COLORS["white"], fg=COLORS["muted"],
        ).pack(anchor="w", pady=(5, 12))
        self._button(
            inner, "자세히 관리  ›", self.show_todo_page, bg=COLORS["blue_light"],
            fg=COLORS["blue"], size=9, bold=True, pady=8,
        ).pack(side="bottom", fill="x", pady=(12, 0))
        scroll = ScrollableFrame(inner, COLORS["white"])
        self.active_scroll = scroll
        scroll.pack(fill="both", expand=True)
        if not items:
            label = tk.Label(scroll.content, text="이 날짜에는 기록이 없어요.\n할 일이나 메모를 추가해 보세요.", font=self._font(9), bg=COLORS["row"], fg=COLORS["muted"], justify="left", anchor="w", padx=12, pady=18)
            label.pack(fill="x")
            scroll.enable_scroll(label)
            return
        for item in self._ordered(items):
            row = tk.Frame(scroll.content, bg=COLORS["row"])
            row.pack(fill="x", pady=(0, 6))
            if item["kind"] == "todo":
                mark = "✓" if item["done"] else "○"
                flag = self._button(row, mark, lambda item_id=item["id"]: self.toggle_item(item_id), bg=COLORS["row"], fg=COLORS["green_dark"], size=12, bold=True, padx=7, pady=8)
            else:
                flag = tk.Label(row, text="메모", font=self._font(8, "bold"), bg=COLORS["row"], fg=COLORS["blue"], padx=6)
            flag.pack(side="left", anchor="n")
            text_box = tk.Frame(row, bg=COLORS["row"])
            text_box.pack(side="left", fill="both", expand=True, pady=7)
            if item["time"]:
                time_label = tk.Label(text_box, text=item["time"], font=self._font(8, "bold"), bg=COLORS["row"], fg=COLORS["blue"], anchor="w")
                time_label.pack(fill="x")
                scroll.enable_scroll(time_label)
            styles = ("overstrike",) if item["kind"] == "todo" and item["done"] else ()
            label = tk.Label(text_box, text=item["text"], font=self._font(9, *styles), bg=COLORS["row"], fg=COLORS["muted"] if item["done"] else COLORS["ink"], anchor="w", justify="left", wraplength=180)
            label.pack(fill="x")
            row.bind("<Configure>", lambda event, label=label: label.configure(wraplength=max(80, event.width - 65)))
            scroll.enable_scroll(row, flag, text_box, label)

    def show_todo_page(self):
        self._clear_page("todo")
        card = self._card(self.body)
        card.pack(fill="both", expand=True)
        inner = tk.Frame(card, bg=COLORS["white"])
        inner.pack(fill="both", expand=True, padx=22, pady=15)

        date_area = tk.Frame(inner, bg=COLORS["white"])
        date_area.pack(fill="x")
        self._date_selectors(date_area)
        day_line = tk.Frame(date_area, bg=COLORS["white"])
        day_line.pack(pady=(7, 0))
        self._button(day_line, "‹", lambda: self._change_day(-1), bg=COLORS["blue_light"], fg=COLORS["blue"], size=15, padx=12, pady=1).pack(side="left", padx=(0, 20))
        date = self.selected_date
        date_center = tk.Frame(day_line, bg=COLORS["white"])
        date_center.pack(side="left")
        tk.Label(date_center, text=f"{date.month}월 {date.day}일 {WEEKDAYS[date.weekday()]}요일", font=self._font(14, "bold"), bg=COLORS["white"], fg=COLORS["ink"]).pack()
        self._button(date_center, "오늘로", lambda: self.set_date(dt.date.today()), bg=COLORS["white"], fg=COLORS["green_dark"], size=9, bold=True, padx=5, pady=1).pack()
        self._button(day_line, "›", lambda: self._change_day(1), bg=COLORS["blue_light"], fg=COLORS["blue"], size=15, padx=12, pady=1).pack(side="left", padx=(20, 0))

        tk.Frame(inner, bg=COLORS["line"], height=1).pack(fill="x", pady=(14, 12))
        items = self._items()
        todos = [item for item in items if item["kind"] == "todo"]
        completed = sum(item["done"] for item in todos)
        heading = tk.Frame(inner, bg=COLORS["white"])
        heading.pack(fill="x", pady=(0, 9))
        tk.Label(heading, text="할 일과 메모", font=self._font(11, "bold"), bg=COLORS["white"], fg=COLORS["ink"]).pack(side="left")
        tk.Label(heading, text=f"할 일 {len(todos)}개 중 {completed}개 완료", font=self._font(9, "bold"), bg=COLORS["white"], fg=COLORS["green_dark"]).pack(side="right")

        form = tk.Frame(inner, bg=COLORS["white"])
        form.pack(fill="x")
        add_text = "저장" if self.editing_id else "+ 추가"
        self._button(form, add_text, self.add_item, bg=COLORS["green"], fg=COLORS["white"], size=10, bold=True, padx=15, pady=8).pack(side="left", padx=(0, 7))
        kind = ttk.Combobox(form, textvariable=self.kind_var, values=("할 일", "메모"), state="readonly", width=7, style="Health.TCombobox", font=self._font(10))
        kind.pack(side="left", padx=(0, 8))
        if self.editing_id:
            self._button(form, "취소", self.cancel_edit, bg=COLORS["row"], fg=COLORS["muted"], size=9, padx=8).pack(side="right", padx=(7, 0))
        time = tk.Entry(form, textvariable=self.time_var, width=7, font=self._font(10), relief="flat", bd=0, highlightthickness=1, highlightbackground=COLORS["line"], highlightcolor=COLORS["green"], fg=COLORS["ink"])
        time.pack(side="right", ipady=7)
        time.bind("<Return>", lambda event: self.add_item())
        tk.Label(form, text="시간", font=self._font(9), bg=COLORS["white"], fg=COLORS["muted"]).pack(side="right", padx=(10, 6))
        text_entry = tk.Entry(form, textvariable=self.text_var, font=self._font(10), relief="flat", bd=0, highlightthickness=1, highlightbackground=COLORS["line"], highlightcolor=COLORS["green"], fg=COLORS["ink"])
        text_entry.pack(side="left", fill="x", expand=True, ipady=7)
        text_entry.bind("<Return>", lambda event: self.add_item())
        tk.Label(inner, text="내용을 입력하고 추가해 주세요. 시간은 선택 사항이에요. 예: 09:30, 14:00", font=self._font(9), bg=COLORS["white"], fg=COLORS["muted"]).pack(anchor="w", pady=(7, 10))

        scroll = ScrollableFrame(inner, COLORS["white"])
        self.active_scroll = scroll
        scroll.pack(fill="both", expand=True)
        if not items:
            empty = tk.Label(scroll.content, text="아직 기록이 없어요.\n오늘 해야 할 일이나 기억하고 싶은 내용을 적어 보세요.", font=self._font(10), bg=COLORS["row"], fg=COLORS["muted"], pady=28, justify="center")
            empty.pack(fill="x")
            scroll.enable_scroll(empty)
        else:
            for item in self._ordered(items):
                self._todo_row(scroll, item)

    def _todo_row(self, scroll, item):
        bg = COLORS["row"]
        row = tk.Frame(scroll.content, bg=bg)
        row.pack(fill="x", pady=(0, 7))
        if item["kind"] == "todo":
            button_text = "✓ 완료" if item["done"] else "○ 할 일"
            button_bg = COLORS["green_light"] if item["done"] else COLORS["blue_light"]
            button_fg = COLORS["green_dark"] if item["done"] else COLORS["blue"]
            flag = self._button(row, button_text, lambda item_id=item["id"]: self.toggle_item(item_id), bg=button_bg, fg=button_fg, size=9, bold=True, padx=9, pady=6)
        else:
            flag = tk.Label(row, text="메모", font=self._font(9, "bold"), bg=COLORS["white"], fg=COLORS["blue"], padx=12, pady=7)
        flag.pack(side="left", padx=(10, 8), pady=8, anchor="n")

        actions = tk.Frame(row, bg=bg)
        actions.pack(side="right", padx=(5, 8), anchor="n", pady=8)
        edit = self._button(actions, "수정", lambda item_id=item["id"]: self.start_edit(item_id), bg=bg, fg=COLORS["blue"], size=9, padx=7, pady=5)
        edit.pack(side="left")
        delete = self._button(actions, "삭제", lambda item_id=item["id"]: self.delete_item(item_id), bg=bg, fg=COLORS["red"], size=9, padx=7, pady=5)
        delete.pack(side="left")

        info = tk.Frame(row, bg=bg)
        info.pack(side="left", fill="both", expand=True, pady=8)
        labels = []
        if item["time"]:
            time = tk.Label(info, text=item["time"], font=self._font(9, "bold"), bg=bg, fg=COLORS["blue"], anchor="w")
            time.pack(fill="x")
            labels.append(time)
        styles = ("overstrike",) if item["kind"] == "todo" and item["done"] else ()
        label = tk.Label(info, text=item["text"], font=self._font(10, *styles), bg=bg, fg=COLORS["muted"] if item["done"] else COLORS["ink"], anchor="w", justify="left", wraplength=500)
        label.pack(fill="x")
        info.bind("<Configure>", lambda event, label=label: label.configure(wraplength=max(100, event.width - 8)))
        scroll.enable_scroll(row, flag, actions, edit, delete, info, label, *labels)

    def add_item(self):
        text = self.text_var.get().strip()
        if not text:
            messagebox.showwarning("내용을 입력해 주세요", "추가할 할 일이나 메모를 입력해 주세요.", parent=self)
            return
        try:
            time = parse_optional_time(self.time_var.get())
        except ValueError as exc:
            messagebox.showwarning("시간을 확인해 주세요", str(exc), parent=self)
            return
        kind = "todo" if self.kind_var.get() == "할 일" else "memo"
        date_key = self.selected_date.isoformat()
        items = self.records.setdefault(date_key, [])
        if self.editing_id:
            item = next((item for item in items if item["id"] == self.editing_id), None)
            if item is None:
                self.cancel_edit()
                return
            item.update({"text": text, "time": time, "kind": kind})
            if kind == "memo":
                item["done"] = False
        else:
            items.append({"id": uuid4().hex, "kind": kind, "text": text, "time": time, "done": False})
        self._save_data()
        self.editing_id = None
        self.text_var.set("")
        self.time_var.set("")
        self._redraw()

    def start_edit(self, item_id):
        item = next((item for item in self._items() if item["id"] == item_id), None)
        if item is None:
            return
        self.editing_id = item_id
        self.kind_var.set("할 일" if item["kind"] == "todo" else "메모")
        self.text_var.set(item["text"])
        self.time_var.set(item["time"] or "")
        self.show_todo_page()

    def cancel_edit(self, redraw=True):
        self.editing_id = None
        self.text_var.set("")
        self.time_var.set("")
        if redraw:
            self._redraw()

    def toggle_item(self, item_id):
        item = next((item for item in self._items() if item["id"] == item_id), None)
        if item is None or item["kind"] != "todo":
            return
        item["done"] = not item["done"]
        self._save_data()
        self._redraw()

    def delete_item(self, item_id):
        date_key = self.selected_date.isoformat()
        items = self.records.get(date_key, [])
        filtered = [item for item in items if item["id"] != item_id]
        if len(filtered) == len(items):
            return
        if filtered:
            self.records[date_key] = filtered
        else:
            self.records.pop(date_key, None)
        if self.editing_id == item_id:
            self.cancel_edit(redraw=False)
        self._save_data()
        self._redraw()

    def show_empty_page(self, key, title):
        self._clear_page(key)
        card = self._card(self.body)
        card.pack(fill="both", expand=True)
        center = tk.Frame(card, bg=COLORS["white"])
        center.place(relx=0.5, rely=0.5, anchor="center")
        tk.Label(center, text=title, font=self._font(15, "bold"), bg=COLORS["white"], fg=COLORS["ink"]).pack(pady=(0, 8))
        tk.Label(center, text="이 기능은 준비 중이에요.", font=self._font(10), bg=COLORS["white"], fg=COLORS["muted"]).pack()


if __name__ == "__main__":
    app = MainApplication()
    app.mainloop()
