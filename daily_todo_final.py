import csv
import os
from pathlib import Path
import tempfile
import tkinter as tk
from tkinter import messagebox

# config.py에서 경로 가져오기 (규칙 1 준수)
try:
    from config import TODO_CSV_PATH
except ImportError:
    BASE_DIR = Path(__file__).resolve().parent
    TODO_CSV_PATH = BASE_DIR / "data" / "todo.csv"


def load_todos(path=TODO_CSV_PATH):
    """data/todo.csv에서 할 일 목록을 읽어온다. 파일이 없으면 빈 리스트 반환."""
    path = Path(path)
    if not path.exists():
        return []
    
    items = []
    try:
        with path.open("r", encoding="utf-8", newline="") as file:
            reader = csv.DictReader(file)
            for row in reader:
                try:
                    item_id = int(row["id"])
                except (ValueError, KeyError):
                    continue
                
                date_str = row.get("date", "")
                title = row.get("title", "")
                done_str = row.get("done", "false").strip().lower()
                done = done_str == "true"
                
                items.append({
                    "id": item_id,
                    "date": date_str,
                    "title": title,
                    "done": done
                })
    except (OSError, csv.Error):
        return []
    return items


def save_todos(items, path=TODO_CSV_PATH):
    """할 일 목록을 data/todo.csv에 안전하게 저장한다 (임시 파일 교체 방식)."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    
    temp_name = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", newline="", dir=path.parent,
            prefix=".todo_", suffix=".tmp", delete=False,
        ) as file:
            temp_name = file.name
            writer = csv.DictWriter(file, fieldnames=["id", "date", "title", "done"])
            writer.writeheader()
            for item in items:
                writer.writerow({
                    "id": item["id"],
                    "date": item["date"],
                    "title": item["title"],
                    "done": "true" if item["done"] else "false"
                })
        os.replace(temp_name, path)
        temp_name = None
    finally:
        if temp_name is not None:
            try:
                os.remove(temp_name)
            except OSError:
                pass


class TodoPage:
    """'오늘의 할 일' 서브 UI 및 관련 동작 관리 클래스"""
    def __init__(self, app, parent_container):
        self.app = app
        self.parent = parent_container
        self.render()

    def render(self):
        self.app._clear_page("todo")
        card = self.app._card(self.parent)
        card.pack(fill="both", expand=True)
        inner = tk.Frame(card, bg=self.app.COLORS["white"])
        inner.pack(fill="both", expand=True, padx=22, pady=15)

        date_area = tk.Frame(inner, bg=self.app.COLORS["white"])
        date_area.pack(fill="x")
        self.app._date_selectors(date_area)
        
        day_line = tk.Frame(date_area, bg=self.app.COLORS["white"])
        day_line.pack(pady=(7, 0))
        self.app._button(day_line, "‹", lambda: self.app._change_day(-1), bg=self.app.COLORS["blue_light"], fg=self.app.COLORS["blue"], size=15, padx=12, pady=1).pack(side="left", padx=(0, 20))
        
        date = self.app.selected_date
        date_center = tk.Frame(day_line, bg=self.app.COLORS["white"])
        date_center.pack(side="left")
        tk.Label(date_center, text=f"{date.month}월 {date.day}일 {self.app.WEEKDAYS[date.weekday()]}요일", font=self.app._font(14, "bold"), bg=self.app.COLORS["white"], fg=self.app.COLORS["ink"]).pack()
        
        import datetime as dt
        self.app._button(date_center, "오늘로", lambda: self.app.set_date(dt.date.today()), bg=self.app.COLORS["white"], fg=self.app.COLORS["green_dark"], size=9, bold=True, padx=5, pady=1).pack()
        self.app._button(day_line, "›", lambda: self.app._change_day(1), bg=self.app.COLORS["blue_light"], fg=self.app.COLORS["blue"], size=15, padx=12, pady=1).pack(side="left", padx=(20, 0))

        tk.Frame(inner, bg=self.app.COLORS["line"], height=1).pack(fill="x", pady=(14, 12))
        items = self.app._items()
        completed = sum(item["done"] for item in items)
        
        heading = tk.Frame(inner, bg=self.app.COLORS["white"])
        heading.pack(fill="x", pady=(0, 9))
        tk.Label(heading, text="할 일 목록", font=self.app._font(11, "bold"), bg=self.app.COLORS["white"], fg=self.app.COLORS["ink"]).pack(side="left")
        tk.Label(heading, text=f"총 {len(items)}개 중 {completed}개 완료", font=self.app._font(9, "bold"), bg=self.app.COLORS["white"], fg=self.app.COLORS["green_dark"]).pack(side="right")

        form = tk.Frame(inner, bg=self.app.COLORS["white"])
        form.pack(fill="x")
        add_text = "저장" if self.app.editing_id else "+ 추가"
        self.app._button(form, add_text, self.add_item, bg=self.app.COLORS["green"], fg=self.app.COLORS["white"], size=10, bold=True, padx=15, pady=8).pack(side="left", padx=(0, 7))
        if self.app.editing_id:
            self.app._button(form, "취소", self.app.cancel_edit, bg=self.app.COLORS["row"], fg=self.app.COLORS["muted"], size=9, padx=8).pack(side="right", padx=(7, 0))
        
        text_entry = tk.Entry(form, textvariable=self.app.text_var, font=self.app._font(10), relief="flat", bd=0, highlightthickness=1, highlightbackground=self.app.COLORS["line"], highlightcolor=self.app.COLORS["green"], fg=self.app.COLORS["ink"])
        text_entry.pack(side="left", fill="x", expand=True, ipady=7)
        text_entry.bind("<Return>", lambda event: self.add_item())
        tk.Label(inner, text="할 일 내용을 입력하고 추가해 주세요.", font=self.app._font(9), bg=self.app.COLORS["white"], fg=self.app.COLORS["muted"]).pack(anchor="w", pady=(7, 10))

        scroll = self.app.ScrollableFrame(inner, self.app.COLORS["white"])
        self.app.active_scroll = scroll
        scroll.pack(fill="both", expand=True)
        
        if not items:
            empty = tk.Label(scroll.content, text="아직 할 일이 없어요.\n오늘 해야 할 일을 적어 보세요.", font=self.app._font(10), bg=self.app.COLORS["row"], fg=self.app.COLORS["muted"], pady=28, justify="center")
            empty.pack(fill="x")
            scroll.enable_scroll(empty)
        else:
            for item in items:
                self._todo_row(scroll, item)

    def _todo_row(self, scroll, item):
        bg = self.app.COLORS["row"]
        row = tk.Frame(scroll.content, bg=bg)
        row.pack(fill="x", pady=(0, 7))
        
        button_text = "✓ 완료" if item["done"] else "○ 할 일"
        button_bg = self.app.COLORS["green_light"] if item["done"] else self.app.COLORS["blue_light"]
        button_fg = self.app.COLORS["green_dark"] if item["done"] else self.app.COLORS["blue"]
        flag = self.app._button(row, button_text, lambda item_id=item["id"]: self.app.toggle_item(item_id), bg=button_bg, fg=button_fg, size=9, bold=True, padx=9, pady=6)
        flag.pack(side="left", padx=(10, 8), pady=8, anchor="n")

        actions = tk.Frame(row, bg=bg)
        actions.pack(side="right", padx=(5, 8), anchor="n", pady=8)
        edit = self.app._button(actions, "수정", lambda item_id=item["id"]: self.app.start_edit(item_id), bg=bg, fg=self.app.COLORS["blue"], size=9, padx=7, pady=5)
        edit.pack(side="left")
        delete = self.app._button(actions, "삭제", lambda item_id=item["id"]: self.app.delete_item(item_id), bg=bg, fg=self.app.COLORS["red"], size=9, padx=7, pady=5)
        delete.pack(side="left")

        info = tk.Frame(row, bg=bg)
        info.pack(side="left", fill="both", expand=True, pady=8)
        styles = ("overstrike",) if item["done"] else ()
        label = tk.Label(info, text=item["title"], font=self.app._font(10, *styles), bg=bg, fg=self.app.COLORS["muted"] if item["done"] else self.app.COLORS["ink"], anchor="w", justify="left", wraplength=500)
        label.pack(fill="x")
        info.bind("<Configure>", lambda event, label=label: label.configure(wraplength=max(100, event.width - 8)))
        scroll.enable_scroll(row, flag, actions, edit, delete, info, label)

    def add_item(self):
        text = self.app.text_var.get().strip()
        if not text:
            messagebox.showwarning("내용을 입력해 주세요", "추가할 할 일을 입력해 주세요.", parent=self.app)
            return
        
        date_key = self.app.selected_date.isoformat()
        
        if self.app.editing_id:
            item = next((item for item in self.app.all_todos if item["id"] == self.app.editing_id), None)
            if item is None:
                self.app.cancel_edit()
                return
            item.update({"title": text, "date": date_key})
        else:
            max_id = max((item["id"] for item in self.app.all_todos), default=0)
            new_id = max_id + 1
            self.app.all_todos.append({
                "id": new_id,
                "date": date_key,
                "title": text,
                "done": False
            })
            
        self.app._save_data()
        self.app.editing_id = None
        self.app.text_var.set("")
        self.app._redraw()