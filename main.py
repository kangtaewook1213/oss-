"""Health Log 실행 파일: 왼쪽 메뉴와 화면 전환을 담당하는 앱 틀.

실행: python main.py
- 창 하나 안에서 홈(달력) / 할 일 / 칼로리 / 인바디 / 주간 리포트를 오간다.
- 화면은 home.py의 build_xxx 함수다. (2단계에서 각 기능 파일로 옮김)
- 색, 글꼴, 공통 위젯은 ui.py에 있다.
- 선택한 날짜(app.selected)는 모든 화면이 함께 쓴다.
"""
import tkinter as tk
import traceback
from datetime import date, datetime

import calorie_diary
import daily_todo
import home
import ui
from config import ensure_data_files

# (이름, 메뉴에 보이는 글자, 메뉴 표시 색, 화면을 만드는 함수)
PAGES = [
    ("home", "홈", ui.COLOR_PRIMARY, home.build_home),
    ("todo", "할 일", ui.COLOR_TODO, home.build_todo),
    ("calorie", "칼로리", ui.COLOR_INTAKE, home.build_calorie),
    ("body", "인바디", ui.COLOR_BODY, home.build_body),
    ("weekly", "주간 리포트", ui.COLOR_BURN, home.build_weekly),
]


class App:
    def __init__(self, root):
        self.root = root
        self.selected = date.today()
        self.view_year, self.view_month = self.selected.year, self.selected.month
        self.page = "home"
        self.refocus = False
        self.nav_items = {}

        root.title("Health Log")
        width = min(ui.px(1180), root.winfo_screenwidth() - ui.px(60))
        height = min(ui.px(760), root.winfo_screenheight() - ui.px(110))
        x = (root.winfo_screenwidth() - width) // 2
        y = max((root.winfo_screenheight() - height) // 2 - ui.px(20), 0)
        root.geometry(f"{width}x{height}+{x}+{y}")
        root.minsize(min(ui.px(1040), width), min(ui.px(680), height))

        self.build_sidebar()
        self.content = tk.Frame(root, bg=ui.COLOR_BG)
        self.content.pack(side="left", fill="both", expand=True)
        self.reload()

    # --- 화면 전환 ---
    def show(self, page):
        self.page = page
        self.reload()

    def select(self, day, page=None):
        """선택 날짜를 바꾼다. page를 주면 그 화면으로 함께 이동한다."""
        self.selected = day
        self.view_year, self.view_month = day.year, day.month
        if page:
            self.page = page
        self.reload()

    def move_month(self, delta):
        month = self.view_year * 12 + self.view_month - 1 + delta
        self.view_year, self.view_month = divmod(month, 12)
        self.view_month += 1
        self.reload()

    def reload(self, refocus=False):
        """현재 화면을 다시 그린다. refocus=True면 입력란에 커서를 다시 둔다."""
        self.refocus = refocus
        for widget in self.content.winfo_children():
            widget.destroy()
        body = tk.Frame(self.content, bg=ui.COLOR_BG)
        body.pack(fill="both", expand=True, padx=24, pady=(20, 22))
        builder = next(build for name, _, _, build in PAGES if name == self.page)
        try:
            builder(self, body)
        except Exception:       # 한 화면의 오류로 프로그램 전체가 멈추지 않게 한다
            traceback.print_exc()
            ui.label(body, "화면을 불러오는 중 오류가 발생했습니다.", "title").pack(pady=(60, 6))
            ui.label(body, "터미널에 표시된 오류 내용을 확인해 주세요.", "muted").pack()
        self.refocus = False
        self.update_sidebar()

    def autofocus(self, widget, always=False):
        """화면을 다시 그린 뒤 입력란에 커서를 둔다."""
        if always or self.refocus:
            widget.focus_set()

    def toast(self, text, kind="ok"):
        ui.toast(self.root, text, kind)

    @staticmethod
    def now():
        return datetime.now()

    # --- 왼쪽 메뉴 ---
    def build_sidebar(self):
        bar = tk.Frame(self.root, bg=ui.COLOR_SIDEBAR, width=ui.px(216))
        bar.pack(side="left", fill="y")
        bar.pack_propagate(False)

        brand = tk.Frame(bar, bg=ui.COLOR_SIDEBAR)
        brand.pack(fill="x", padx=20, pady=(24, 26))
        logo = tk.Canvas(brand, width=ui.px(34), height=ui.px(34), bg=ui.COLOR_SIDEBAR,
                         highlightthickness=0)
        side = ui.px(34)
        ui.round_rect(logo, 0, 0, side, side, ui.px(10), fill=ui.COLOR_PRIMARY,
                      outline=ui.COLOR_PRIMARY)
        points = [(0.14, 0.55), (0.34, 0.55), (0.44, 0.28), (0.57, 0.76), (0.67, 0.5),
                  (0.86, 0.5)]
        logo.create_line(*[side * n for point in points for n in point], fill="#ffffff",
                         width=ui.px(2.2), capstyle="round", joinstyle="round")
        logo.pack(side="left")
        text = tk.Frame(brand, bg=ui.COLOR_SIDEBAR)
        text.pack(side="left", padx=10)
        tk.Label(text, text="Health Log", font=(ui.FONT_FAMILY, 13, "bold"),
                 bg=ui.COLOR_SIDEBAR, fg="#ffffff").pack(anchor="w")
        tk.Label(text, text="나의 건강 기록", font=ui.FONTS["small"], bg=ui.COLOR_SIDEBAR,
                 fg=ui.COLOR_SIDEBAR_TEXT).pack(anchor="w")

        for name, title, color, _ in PAGES:
            self.nav_items[name] = self.build_nav_item(bar, name, title, color)

        self.today_box = tk.Frame(bar, bg=ui.COLOR_SIDEBAR_ACTIVE)
        self.today_box.pack(side="bottom", fill="x", padx=14, pady=16)

    def build_nav_item(self, parent, name, title, color):
        row = tk.Frame(parent, bg=ui.COLOR_SIDEBAR, cursor="hand2")
        row.pack(fill="x", padx=12, pady=2)
        marker = tk.Frame(row, bg=ui.COLOR_SIDEBAR, width=ui.px(3))
        marker.pack(side="left", fill="y")
        dot = tk.Canvas(row, width=ui.px(10), height=ui.px(10), bg=ui.COLOR_SIDEBAR,
                        highlightthickness=0)
        ui.round_rect(dot, 0, 0, ui.px(10), ui.px(10), ui.px(3), fill=color, outline=color)
        dot.pack(side="left", padx=(12, 10), pady=12)
        text = tk.Label(row, text=title, font=ui.FONTS["body"], bg=ui.COLOR_SIDEBAR,
                        fg=ui.COLOR_SIDEBAR_TEXT, anchor="w")
        text.pack(side="left", fill="x", expand=True)
        parts = (row, dot, text)

        def paint(background):
            for widget in parts:
                widget.config(bg=background)

        def on_leave(event):
            paint(ui.COLOR_SIDEBAR_ACTIVE if self.page == name else ui.COLOR_SIDEBAR)

        for widget in parts:
            widget.bind("<Button-1>", lambda event: self.show(name))
            widget.bind("<Enter>", lambda event: paint(ui.COLOR_SIDEBAR_ACTIVE))
            widget.bind("<Leave>", on_leave)
        return {"paint": paint, "marker": marker, "text": text, "color": color}

    def update_sidebar(self):
        for name, item in self.nav_items.items():
            active = name == self.page
            item["paint"](ui.COLOR_SIDEBAR_ACTIVE if active else ui.COLOR_SIDEBAR)
            item["marker"].config(bg=item["color"] if active else ui.COLOR_SIDEBAR)
            item["text"].config(fg="#ffffff" if active else ui.COLOR_SIDEBAR_TEXT,
                                font=ui.FONTS["bold"] if active else ui.FONTS["body"])

        for widget in self.today_box.winfo_children():
            widget.destroy()
        today = date.today()
        todos = daily_todo.load_todos(today)
        done = sum(1 for todo in todos if todo["done"])
        totals = calorie_diary.calculate_daily_calorie(today)
        box = tk.Frame(self.today_box, bg=ui.COLOR_SIDEBAR_ACTIVE, cursor="hand2")
        box.pack(fill="x", padx=14, pady=12)
        lines = (
            ("오늘", ui.FONTS["small"], ui.COLOR_SIDEBAR_TEXT),
            (f"{today.month}월 {today.day}일 {ui.WEEKDAYS[today.weekday()]}요일",
             ui.FONTS["bold"], "#ffffff"),
            (f"할 일 {done}/{len(todos)}  ·  섭취 {totals['intake']:,} kcal",
             ui.FONTS["small"], ui.COLOR_SIDEBAR_TEXT),
        )
        for text, font, color in lines:
            line = tk.Label(box, text=text, font=font, fg=color, bg=ui.COLOR_SIDEBAR_ACTIVE,
                            anchor="w")
            line.pack(fill="x")
            line.bind("<Button-1>", lambda event: self.select(today, page="home"))


def main():
    ensure_data_files()   # data/ 폴더와 CSV(헤더 포함) 없으면 자동 생성
    ui.enable_hidpi()
    root = tk.Tk()
    ui.setup_theme(root)
    App(root)
    root.mainloop()


if __name__ == "__main__":
    main()