"""실행: python main.py. 달력에서 날짜를 선택해 각 기능을 연다."""
import calendar
import tkinter as tk
from datetime import date
from tkinter import messagebox
from config import ensure_data_files
from calorie_diary import show_calorie_page
<<<<<<< HEAD
#아직 없음 from body_tracker import show_body_tracker
=======
from body_tracker import show_body_tracker
>>>>>>> origin/conflict-practice
from weekly_summary import show_weekly_report
WEEKDAYS = ['일', '월', '화', '수', '목', '금', '토']


def open_calorie(parent, selected_date):
    show_calorie_page(parent, selected_date)


def open_todo(parent, selected_date):
    messagebox.showinfo('할 일', f'{selected_date} 할 일 입력 (구현 예정)', parent=parent)


def open_inbody(parent, selected_date):
    show_body_tracker(parent, selected_date)


def open_weekly_report(parent, selected_date):
    show_weekly_report(parent, selected_date)


def show_detail_page(root, selected_date):
    win = tk.Toplevel(root)
    win.title(f'{selected_date.isoformat()} 상세')
    win.geometry('320x300')
    tk.Label(win, text=selected_date.strftime('%Y년 %m월 %d일'), font=('맑은 고딕', 14, 'bold')).pack(pady=15)
    buttons = [('칼로리 입력', open_calorie), ('할 일 입력', open_todo), ('인바디 트래커', open_inbody), ('주간 리포트', open_weekly_report)]
    for text, handler in buttons:
        tk.Button(win, text=text, width=22, height=2, command=lambda h=handler: h(win, selected_date)).pack(pady=4)


class CalendarApp:

    def __init__(self, root):
        self.root = root
        root.title('Health Log')
        root.geometry('420x400')
        today = date.today()
        self.year, self.month = (today.year, today.month)
        self.cal = calendar.Calendar(firstweekday=6)
        header = tk.Frame(root)
        header.pack(pady=10)
        tk.Button(header, text='◀', width=3, command=self.prev_month).pack(side='left')
        self.title_label = tk.Label(header, width=14, font=('맑은 고딕', 14, 'bold'))
        self.title_label.pack(side='left', padx=5)
        tk.Button(header, text='▶', width=3, command=self.next_month).pack(side='left')
        self.grid_frame = tk.Frame(root)
        self.grid_frame.pack(padx=10, pady=5, fill='both', expand=True)
        self.draw()

    def draw(self):
        for w in self.grid_frame.winfo_children():
            w.destroy()
        self.title_label.config(text=f'{self.year}년 {self.month}월')
        for c, name in enumerate(WEEKDAYS):
            fg = 'red' if c == 0 else 'blue' if c == 6 else 'black'
            tk.Label(self.grid_frame, text=name, fg=fg).grid(row=0, column=c, sticky='nsew')
        today = date.today()
        for r, week in enumerate(self.cal.monthdayscalendar(self.year, self.month), start=1):
            for c, day in enumerate(week):
                if day == 0:
                    continue
                d = date(self.year, self.month, day)
                is_today = d == today
                tk.Button(self.grid_frame, text=str(day), width=4,
                    height=2, bg='#cde7ff' if is_today else None, command=lambda d=d: show_detail_page(self.root,
                    d)).grid(row=r, column=c, padx=1, pady=1, sticky='nsew')
        for c in range(7):
            self.grid_frame.columnconfigure(c, weight=1)

    def prev_month(self):
        self._change_month(-1)

    def next_month(self):
        self._change_month(1)

    def _change_month(self, amount):
        year, month = divmod(self.year * 12 + self.month - 1 + amount, 12)
        self.year, self.month = (year, month + 1)
        self.draw()


def main():
    ensure_data_files()
    root = tk.Tk()
    CalendarApp(root)
    root.mainloop()
if __name__ == '__main__':
    main()
