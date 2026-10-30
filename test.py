import datetime as dt
import tkinter as tk
from tkinter import font as tkfont

from tkcalendar import Calendar


# 전체 화면에서 사용하는 색상
COLORS = {
    "background": "#F2F9F6",
    "header": "#E6F5F4",
    "white": "#FFFFFF",
    "text": "#294653",
    "muted": "#778F96",
    "line": "#DDEDE9",
    "blue": "#DDF1F9",
    "blue_text": "#377E9B",
    "green": "#DDF2DC",
    "green_text": "#47835D",
    "green_dark": "#5DAE79",
    "green_hover": "#4B9867",
    "row": "#F7FBFA",
    "row_done": "#F1F7F2",
}


class MainApplication(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Health Log")
        self.geometry("1000x720")
        self.minsize(860, 640)
        self.configure(bg=COLORS["background"])

        self.font_family = self._find_font()
        self.selected_date = dt.date.today()
        # 화면을 바꿔도 할 일과 완료 상태가 유지됩니다. 종료 후에는 초기화됩니다.
        self.todos = []
        self.next_todo_id = 0
        self.nav_buttons = {}
        self.current_page = None

        self._build_header()
        self._build_navigation()

        self.content_container = tk.Frame(self, bg=COLORS["background"])
        self.content_container.pack(fill="both", expand=True)
        self.show_todo_page()

    def _find_font(self):
        available = set(tkfont.families(self))
        for family in ("맑은 고딕", "Malgun Gothic", "Apple SD Gothic Neo", "Noto Sans CJK KR"):
            if family in available:
                return family
        return "TkDefaultFont"

    def _font(self, size, *styles):
        return (self.font_family, size, *styles)

    def _build_header(self):
        header = tk.Frame(self, bg=COLORS["header"])
        header.pack(fill="x")
        inner = tk.Frame(header, bg=COLORS["header"])
        inner.pack(fill="x", padx=32, pady=(20, 18))

        title = tk.Frame(inner, bg=COLORS["header"])
        title.pack(side="left")
        tk.Label(
            title, text="HEALTH LOG", font=self._font(19, "bold"),
            bg=COLORS["header"], fg=COLORS["text"],
        ).pack(anchor="w")
        tk.Label(
            title, text="나를 돌보는 작은 습관", font=self._font(10),
            bg=COLORS["header"], fg=COLORS["muted"],
        ).pack(anchor="w", pady=(3, 0))

        tk.Label(
            inner, text="  오늘도 천천히, 건강하게  ",
            font=self._font(10, "bold"), bg=COLORS["green"],
            fg=COLORS["green_text"], padx=8, pady=7,
        ).pack(side="right")

    def _build_navigation(self):
        nav = tk.Frame(self, bg=COLORS["white"])
        nav.pack(fill="x")
        inner = tk.Frame(nav, bg=COLORS["white"])
        inner.pack(fill="x", padx=25, pady=10)

        pages = [
            ("calendar", "오늘의 달력", self.show_calendar_page),
            ("todo", "오늘의 할 일", self.show_todo_page),
            ("calorie", "칼로리 다이어리", lambda: self.show_empty_page("칼로리 다이어리", "calorie")),
            ("report", "주간 건강 리포트", lambda: self.show_empty_page("주간 건강 리포트", "report")),
            ("profile", "내 정보", lambda: self.show_empty_page("내 정보", "profile")),
        ]
        for key, title, command in pages:
            button = tk.Button(
                inner, text=title, command=command, font=self._font(10, "bold"),
                relief="flat", bd=0, padx=12, pady=8, cursor="hand2",
                highlightthickness=0,
            )
            button.pack(side="left", padx=(0, 4))
            self.nav_buttons[key] = button

    def _select_page(self, page):
        self.current_page = page
        for key, button in self.nav_buttons.items():
            selected = key == page
            button.configure(
                bg=COLORS["blue"] if selected else COLORS["white"],
                fg=COLORS["blue_text"] if selected else COLORS["muted"],
                activebackground=COLORS["blue"], activeforeground=COLORS["blue_text"],
            )
        for widget in self.content_container.winfo_children():
            widget.destroy()

    def _page(self, title, subtitle):
        outer = tk.Frame(self.content_container, bg=COLORS["background"])
        outer.pack(fill="both", expand=True, padx=32, pady=(24, 26))
        tk.Label(
            outer, text=title, font=self._font(19, "bold"),
            bg=COLORS["background"], fg=COLORS["text"],
        ).pack(anchor="w")
        tk.Label(
            outer, text=subtitle, font=self._font(10),
            bg=COLORS["background"], fg=COLORS["muted"],
        ).pack(anchor="w", pady=(5, 18))
        return outer

    def _card(self, parent):
        card = tk.Frame(
            parent, bg=COLORS["white"], highlightthickness=1,
            highlightbackground=COLORS["line"], highlightcolor=COLORS["line"],
        )
        card.pack(fill="both", expand=True)
        return card

    def show_todo_page(self):
        self._select_page("todo")
        page = self._page("오늘의 할 일", "하루에 필요한 일들을 가볍게 적어 보세요.")
        card = self._card(page)
        inner = tk.Frame(card, bg=COLORS["white"])
        inner.pack(fill="both", expand=True, padx=25, pady=22)

        top = tk.Frame(inner, bg=COLORS["white"])
        top.pack(fill="x", pady=(0, 14))
        today = dt.date.today()
        tk.Label(
            top, text=f"{today.year}년 {today.month}월 {today.day}일의 목록",
            font=self._font(12, "bold"), bg=COLORS["white"], fg=COLORS["text"],
        ).pack(side="left")
        self.count_label = tk.Label(
            top, font=self._font(10, "bold"), bg=COLORS["white"], fg=COLORS["green_text"],
        )
        self.count_label.pack(side="right")

        entry_row = tk.Frame(inner, bg=COLORS["white"])
        entry_row.pack(fill="x", pady=(0, 14))
        entry_border = tk.Frame(
            entry_row, bg=COLORS["white"], highlightthickness=1,
            highlightbackground=COLORS["line"], highlightcolor=COLORS["green_dark"],
        )
        entry_border.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.todo_entry = tk.Entry(
            entry_border, font=self._font(11), bg=COLORS["white"], fg=COLORS["text"],
            relief="flat", bd=0, highlightthickness=0, insertbackground=COLORS["text"],
        )
        self.todo_entry.pack(fill="x", padx=12, pady=10)
        self.todo_entry.bind("<Return>", self.add_todo)
        tk.Button(
            entry_row, text="추가", font=self._font(10, "bold"), command=self.add_todo,
            bg=COLORS["green_dark"], fg=COLORS["white"], activebackground=COLORS["green_hover"],
            activeforeground=COLORS["white"], relief="flat", bd=0, padx=20, pady=9,
            cursor="hand2", highlightthickness=0,
        ).pack(side="right")

        tk.Label(
            inner, text="체크하여 완료 표시 · 목록은 앱을 종료하면 초기화됩니다",
            font=self._font(9), bg=COLORS["white"], fg=COLORS["muted"],
        ).pack(side="bottom", anchor="w", pady=(12, 0))
        list_container = tk.Frame(inner, bg=COLORS["white"])
        list_container.pack(fill="both", expand=True)
        self.todo_canvas = tk.Canvas(
            list_container, bg=COLORS["white"], highlightthickness=0, bd=0,
        )
        scrollbar = tk.Scrollbar(list_container, orient="vertical", command=self.todo_canvas.yview)
        self.todo_canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.todo_canvas.pack(side="left", fill="both", expand=True)
        self.todo_list_frame = tk.Frame(self.todo_canvas, bg=COLORS["white"])
        self.todo_canvas_window = self.todo_canvas.create_window(
            (0, 0), window=self.todo_list_frame, anchor="nw",
        )
        self.todo_list_frame.bind(
            "<Configure>",
            lambda event: self.todo_canvas.configure(scrollregion=self.todo_canvas.bbox("all")),
        )
        self.todo_canvas.bind(
            "<Configure>",
            lambda event: self.todo_canvas.itemconfigure(self.todo_canvas_window, width=event.width),
        )
        self._bind_scroll(self.todo_canvas)
        self._bind_scroll(self.todo_list_frame)
        self._render_todos()

    def add_todo(self, event=None):
        text = self.todo_entry.get().strip()
        if not text:
            self.todo_entry.focus_set()
            return
        self.todos.append({"id": self.next_todo_id, "text": text, "done": False})
        self.next_todo_id += 1
        self.todo_entry.delete(0, "end")
        self._render_todos()
        self.todo_entry.focus_set()

    def toggle_todo(self, todo_id, done):
        for todo in self.todos:
            if todo["id"] == todo_id:
                todo["done"] = bool(done)
                break
        self._render_todos()

    def delete_todo(self, todo_id):
        self.todos = [todo for todo in self.todos if todo["id"] != todo_id]
        self._render_todos()

    def _render_todos(self):
        previous_position = self.todo_canvas.yview()[0]
        for widget in self.todo_list_frame.winfo_children():
            widget.destroy()
        completed = sum(todo["done"] for todo in self.todos)
        self.count_label.configure(text=f"완료 {completed} / 전체 {len(self.todos)}")
        self.todo_vars = {}

        if not self.todos:
            empty = tk.Label(
                self.todo_list_frame, text="아직 등록된 할 일이 없어요.\n작은 일부터 하나씩 적어 볼까요?",
                font=self._font(11), bg=COLORS["row"], fg=COLORS["muted"],
                pady=35, justify="center",
            )
            empty.pack(fill="x")
            self._bind_scroll(empty)
        else:
            for todo in self.todos:
                bg = COLORS["row_done"] if todo["done"] else COLORS["row"]
                row = tk.Frame(self.todo_list_frame, bg=bg)
                row.pack(fill="x", pady=(0, 7))
                variable = tk.BooleanVar(value=todo["done"])
                self.todo_vars[todo["id"]] = variable
                font_style = ("overstrike",) if todo["done"] else ()
                checkbox = tk.Checkbutton(
                    row, text=todo["text"], variable=variable,
                    command=lambda item_id=todo["id"], var=variable: self.toggle_todo(item_id, var.get()),
                    font=self._font(11, *font_style), bg=bg,
                    fg=COLORS["muted"] if todo["done"] else COLORS["text"],
                    activebackground=bg, activeforeground=COLORS["text"],
                    selectcolor=COLORS["white"], anchor="w", justify="left", wraplength=580,
                    cursor="hand2", bd=0, highlightthickness=0, padx=12, pady=10,
                )
                checkbox.pack(side="left", fill="x", expand=True)
                delete_button = tk.Button(
                    row, text="삭제", command=lambda item_id=todo["id"]: self.delete_todo(item_id),
                    font=self._font(9), bg=bg, fg=COLORS["muted"],
                    activebackground=COLORS["blue"], activeforeground=COLORS["blue_text"],
                    relief="flat", bd=0, padx=10, pady=6, cursor="hand2", highlightthickness=0,
                )
                delete_button.pack(side="right", padx=(0, 8))
                row.bind(
                    "<Configure>",
                    lambda event, label=checkbox: label.configure(wraplength=max(120, event.width - 135)),
                )
                for widget in (row, checkbox, delete_button):
                    self._bind_scroll(widget)

        self.todo_list_frame.update_idletasks()
        self.todo_canvas.configure(scrollregion=self.todo_canvas.bbox("all"))
        self.todo_canvas.yview_moveto(previous_position)

    def _bind_scroll(self, widget):
        widget.bind("<MouseWheel>", self._on_mousewheel)
        widget.bind("<Button-4>", self._on_mousewheel)
        widget.bind("<Button-5>", self._on_mousewheel)

    def _on_mousewheel(self, event):
        if getattr(event, "num", None) == 4:
            direction = -1
        elif getattr(event, "num", None) == 5:
            direction = 1
        else:
            direction = -1 if event.delta > 0 else 1
        self.todo_canvas.yview_scroll(direction, "units")
        return "break"

    def show_calendar_page(self):
        self._select_page("calendar")
        page = self._page("오늘의 달력", "날짜를 선택해 하루를 천천히 살펴보세요.")
        card = self._card(page)
        inner = tk.Frame(card, bg=COLORS["white"])
        inner.pack(fill="both", expand=True, padx=26, pady=24)

        # 달력 화면과 할 일 화면은 서로 독립적입니다.
        heading = tk.Frame(inner, bg=COLORS["white"])
        heading.pack(fill="x", pady=(0, 18))
        tk.Label(
            heading, text="날짜 살펴보기", font=self._font(12, "bold"),
            bg=COLORS["white"], fg=COLORS["text"],
        ).pack(side="left")
        self.selected_date_label = tk.Label(
            heading, font=self._font(10, "bold"), bg=COLORS["green"],
            fg=COLORS["green_text"], padx=10, pady=6,
        )
        self.selected_date_label.pack(side="right")
        self._update_selected_date_label()

        self.cal = Calendar(
            inner, selectmode="day", locale="ko_KR", date_pattern="yyyy-mm-dd",
            year=self.selected_date.year, month=self.selected_date.month, day=self.selected_date.day,
            font=self._font(11), cursor="hand2", showweeknumbers=False,
            background=COLORS["blue_text"], foreground=COLORS["white"], bordercolor=COLORS["blue"],
            headersbackground=COLORS["blue"], headersforeground=COLORS["blue_text"],
            selectbackground=COLORS["green_dark"], selectforeground=COLORS["white"],
            normalbackground=COLORS["white"], normalforeground=COLORS["text"],
            weekendbackground=COLORS["white"], weekendforeground=COLORS["blue_text"],
            othermonthbackground="#F4F8F7", othermonthforeground="#BCCDC9",
            othermonthwebackground="#F4F8F7", othermonthweforeground="#BCCDC9",
        )
        self.cal.pack(fill="both", expand=True)
        self.cal.bind("<<CalendarSelected>>", self.on_date_selected)

    def on_date_selected(self, event=None):
        date = self.cal.selection_get()
        if date is not None:
            self.selected_date = date
            self._update_selected_date_label()

    def _update_selected_date_label(self):
        date = self.selected_date
        self.selected_date_label.configure(text=f"선택한 날짜  {date.year}.{date.month:02d}.{date.day:02d}")

    def show_empty_page(self, title, key):
        self._select_page(key)
        page = self._page(title, "조금 더 편리한 건강 기록을 준비하고 있어요.")
        card = self._card(page)
        center = tk.Frame(card, bg=COLORS["white"])
        center.place(relx=0.5, rely=0.5, anchor="center")
        tk.Label(
            center, text="준비 중이에요", font=self._font(16, "bold"),
            bg=COLORS["white"], fg=COLORS["text"],
        ).pack(pady=(0, 8))
        tk.Label(
            center, text="이 기능은 곧 만날 수 있어요.", font=self._font(10),
            bg=COLORS["white"], fg=COLORS["muted"],
        ).pack()


if __name__ == "__main__":
    app = MainApplication()
    app.mainloop()
