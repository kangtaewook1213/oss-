"""메인 화면: 달력 + 날짜 상세 페이지(기능 4개 진입점).

실행: python main.py
- 달력의 날짜를 누르면 상세 페이지가 열린다.
- 상세 페이지에는 칼로리 / 할 일 / 인바디 / 주간 리포트 버튼이 있다.
- 각 기능은 담당자가 만든 함수로 아래 open_* 함수 안에서 연결한다.
- selected_date는 datetime.date 객체로 전달한다. (문자열이 필요하면 .isoformat())
"""
import calendar
import datetime as dt
import tkinter as tk
from datetime import date

from config import ensure_data_files
from calorie_diary import show_calorie_page
from body_tracker import show_body_tracker
from daily_todo import show_daily_todo
from weekly_summary import show_weekly_report
<<<<<<< HEAD
from daily_todo import show_daily_todo
WEEKDAYS = ['일', '월', '화', '수', '목', '금', '토']
=======

WEEKDAYS = ["일", "월", "화", "수", "목", "금", "토"]  # 일요일 시작 (주간 리포트 기준과 동일)
>>>>>>> main


# ---------------------------------------------------------------
# 기능 연결부: 담당자가 자기 함수를 만들면 여기만 고치면 된다.
# ---------------------------------------------------------------
def open_calorie(parent, selected_date):
    show_calorie_page(parent, selected_date)


def open_todo(parent, selected_date):
    show_daily_todo(parent, selected_date)
<<<<<<< HEAD
=======

>>>>>>> main

def open_inbody(parent, selected_date):
    show_body_tracker(parent, selected_date)

    def _font(self, size, *styles):
        return (self.font_family, size, *styles)

def open_weekly_report(parent, selected_date):
    show_weekly_report(parent, selected_date)

    def shift_month(self, date, delta):
        year, month_zero = divmod(date.year * 12 + date.month - 1 + delta, 12)
        month = month_zero + 1
        day = min(date.day, calendar.monthrange(year, month)[1])
        return dt.date(year, month, day)

# ---------------------------------------------------------------
# 상세 페이지
# ---------------------------------------------------------------
def show_detail_page(root, selected_date):
    win = tk.Toplevel(root)
    win.title(f"{selected_date.isoformat()} 상세")
    win.geometry("320x300")

    tk.Label(win, text=selected_date.strftime("%Y년 %m월 %d일"),
             font=("맑은 고딕", 14, "bold")).pack(pady=15)

    buttons = [
        ("칼로리 입력", open_calorie),
        ("할 일 입력", open_todo),
        ("인바디 트래커", open_inbody),
        ("주간 리포트", open_weekly_report),
    ]
    for text, handler in buttons:
        tk.Button(win, text=text, width=22, height=2,
                  command=lambda h=handler: h(win, selected_date)).pack(pady=4)

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

# ---------------------------------------------------------------
# 달력
# ---------------------------------------------------------------
class CalendarApp:
    def __init__(self, root):
        self.root = root
        root.title("Health Log")
        root.geometry("420x400")

        today = date.today()
        self.year, self.month = today.year, today.month
        self.cal = calendar.Calendar(firstweekday=6)  # 6 = 일요일 시작

        header = tk.Frame(root)
        header.pack(pady=10)
        tk.Button(header, text="◀", width=3, command=self.prev_month).pack(side="left")
        self.title_label = tk.Label(header, width=14, font=("맑은 고딕", 14, "bold"))
        self.title_label.pack(side="left", padx=5)
        tk.Button(header, text="▶", width=3, command=self.next_month).pack(side="left")

        self.grid_frame = tk.Frame(root)
        self.grid_frame.pack(padx=10, pady=5, fill="both", expand=True)

        self.draw()

    def draw(self):
        for w in self.grid_frame.winfo_children():
            w.destroy()
        self.title_label.config(text=f"{self.year}년 {self.month}월")

        for c, name in enumerate(WEEKDAYS):
            fg = "red" if c == 0 else "blue" if c == 6 else "black"
            tk.Label(self.grid_frame, text=name, fg=fg).grid(row=0, column=c, sticky="nsew")

        today = date.today()
        for r, week in enumerate(self.cal.monthdayscalendar(self.year, self.month), start=1):
            for c, day in enumerate(week):
                if day == 0:
                    continue
                d = date(self.year, self.month, day)
                is_today = d == today
                tk.Button(
                    self.grid_frame, text=str(day), width=4, height=2,
                    bg="#cde7ff" if is_today else None,
                    command=lambda d=d: show_detail_page(self.root, d),
                ).grid(row=r, column=c, padx=1, pady=1, sticky="nsew")

        for c in range(7):
            self.grid_frame.columnconfigure(c, weight=1)

    def prev_month(self):
        self.year, self.month = (self.year - 1, 12) if self.month == 1 else (self.year, self.month - 1)
        self.draw()

    def next_month(self):
        self.year, self.month = (self.year + 1, 1) if self.month == 12 else (self.year, self.month + 1)
        self.draw()

        calendar_card = self._card(self.body)
        calendar_card.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        main = tk.Frame(calendar_card, bg=COLORS["white"])
        main.pack(fill="both", expand=True, padx=14, pady=14)
        
        controls = tk.Frame(main, bg=COLORS["white"])
        controls.pack(fill="x", pady=(0, 12))
        self._date_selectors(controls, show_month_arrows=True)

def main():
    ensure_data_files()   # data/ 폴더와 CSV(헤더 포함) 없으면 자동 생성
    root = tk.Tk()
    CalendarApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
