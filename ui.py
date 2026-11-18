"""공통 화면 요소: 색, 글꼴, 테마와 직접 그린 위젯(카드, 통계 타일, 차트 등).

화면 코드는 색이나 글꼴 값을 직접 적지 않고 이 파일에서 가져다 쓴다.

    import ui

    ui.enable_hidpi()             # Tk() 만들기 전에 한 번 (선명한 글자)
    root = tk.Tk()
    ui.setup_theme(root)          # Tk() 만든 직후에 한 번

    outer, body = ui.card(parent, "제목")
    ui.label(body, "내용").pack()
    ui.button(body, "저장", on_save).pack()
"""
import tkinter as tk
import tkinter.font as tkfont
from datetime import date, timedelta
from tkinter import ttk

# ---------------------------------------------------------------
# 색
# ---------------------------------------------------------------
COLOR_BG = "#f3f5f9"            # 창 배경
COLOR_SURFACE = "#ffffff"       # 카드, 입력란
COLOR_BORDER = "#e3e8ef"
COLOR_TRACK = "#e9edf3"         # 진행 막대의 빈 부분, 눈금선
COLOR_HOVER = "#f1f4f9"
COLOR_TEXT = "#17212b"
COLOR_MUTED = "#6c7a89"
COLOR_FAINT = "#b6c0cc"

COLOR_PRIMARY = "#4f46e5"       # 강조 (주요 버튼, 선택 표시)
COLOR_PRIMARY_SOFT = "#eef0ff"
COLOR_DANGER = "#ef4444"

COLOR_INTAKE = "#f59e0b"        # 섭취 칼로리
COLOR_BURN = "#0ea5e9"          # 소모 칼로리
COLOR_TODO = "#10b981"          # 할 일
COLOR_BODY = "#8b5cf6"          # 인바디

COLOR_SIDEBAR = "#111827"
COLOR_SIDEBAR_ACTIVE = "#1f2937"
COLOR_SIDEBAR_TEXT = "#aeb9c7"

# ---------------------------------------------------------------
# 글꼴
# ---------------------------------------------------------------
FONT_FAMILY = "맑은 고딕"
FONTS = {
    "display": (FONT_FAMILY, 19, "bold"),   # 화면 제목
    "title": (FONT_FAMILY, 14, "bold"),
    "h2": (FONT_FAMILY, 11, "bold"),        # 카드 제목
    "body": (FONT_FAMILY, 10),
    "arrow": (FONT_FAMILY, 13),             # ‹ › 이동 버튼
    "day": (FONT_FAMILY, 11),               # 달력 날짜
    "day_bold": (FONT_FAMILY, 11, "bold"),
    "bold": (FONT_FAMILY, 10, "bold"),
    "muted": (FONT_FAMILY, 10),
    "small": (FONT_FAMILY, 9),
    "num": (FONT_FAMILY, 20, "bold"),       # 통계 숫자
}
_MUTED_KINDS = ("muted", "small")

SCALE = 1.0     # 화면 배율(100% = 1.0). setup_theme에서 정해진다.


def px(value):
    """픽셀 값을 화면 배율에 맞게 바꾼다. 창 크기, 캔버스 좌표에 사용한다."""
    return int(round(value * SCALE))


# ---------------------------------------------------------------
# 테마
# ---------------------------------------------------------------
def enable_hidpi():
    """Windows 고해상도 화면에서 글자가 흐려지지 않게 한다. Tk()보다 먼저 불러야 한다."""
    try:
        import ctypes
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except (ImportError, AttributeError, OSError):
        pass    # Windows가 아니거나 지원하지 않는 버전이면 그냥 넘어간다.


def setup_theme(root):
    """프로그램 전체의 기본 스타일을 정한다. 여러 번 불러도 한 번만 적용된다."""
    global SCALE
    master = root.nametowidget(".")
    if getattr(master, "_ui_theme_ready", False):
        return
    master._ui_theme_ready = True
    SCALE = max(master.winfo_fpixels("1i") / 96, 1.0)

    family = FONT_FAMILY if FONT_FAMILY in tkfont.families(master) else None
    for name in ("TkDefaultFont", "TkTextFont", "TkMenuFont", "TkHeadingFont"):
        font = tkfont.nametofont(name, root=master)
        if family:
            font.configure(family=family)
        font.configure(size=FONTS["body"][1])

    # 우선순위를 낮게(widgetDefault) 주어, 코드에서 직접 지정한 값이 항상 이긴다.
    defaults = {
        "*Background": COLOR_BG,
        "*Foreground": COLOR_TEXT,
        "*Button.Background": COLOR_TRACK,
        "*Button.activeBackground": COLOR_BORDER,
        "*Button.relief": "flat",
        "*Button.borderWidth": 0,
        "*Button.padX": 12,
        "*Button.padY": 4,
        "*Button.cursor": "hand2",
        "*Entry.Background": COLOR_SURFACE,
        "*Entry.relief": "flat",
        "*Entry.highlightThickness": 1,
        "*Entry.highlightBackground": COLOR_BORDER,
        "*Entry.highlightColor": COLOR_PRIMARY,
        "*Entry.insertBackground": COLOR_TEXT,
        "*Listbox.Background": COLOR_SURFACE,
        "*Listbox.relief": "flat",
        "*Listbox.highlightThickness": 1,
        "*Listbox.highlightBackground": COLOR_BORDER,
        "*Checkbutton.activeBackground": COLOR_BG,
        "*Checkbutton.selectColor": COLOR_SURFACE,
    }
    for pattern, value in defaults.items():
        master.option_add(pattern, value, "widgetDefault")
    master.configure(bg=COLOR_BG)

    _setup_ttk(master)
    _setup_button_hover(master)


def _setup_ttk(master):
    style = ttk.Style(master)
    style.theme_use("clam")
    style.configure(".", background=COLOR_BG, foreground=COLOR_TEXT, bordercolor=COLOR_BORDER,
                    lightcolor=COLOR_SURFACE, darkcolor=COLOR_SURFACE)

    style.configure("Treeview", background=COLOR_SURFACE, fieldbackground=COLOR_SURFACE,
                    rowheight=px(30), borderwidth=0, relief="flat")
    style.configure("Treeview.Heading", background=COLOR_SURFACE, foreground=COLOR_MUTED,
                    relief="flat", font=FONTS["small"], padding=(8, 6))
    style.map("Treeview", background=[("selected", COLOR_PRIMARY_SOFT)],
              foreground=[("selected", COLOR_TEXT)])
    style.map("Treeview.Heading", background=[("active", COLOR_SURFACE)])
    style.layout("Treeview", [("Treeview.treearea", {"sticky": "nswe"})])   # 바깥 테두리 제거

    style.configure("Vertical.TScrollbar", background=COLOR_FAINT, troughcolor=COLOR_SURFACE,
                    borderwidth=0, arrowsize=1, width=px(8), relief="flat")
    style.map("Vertical.TScrollbar", background=[("active", COLOR_MUTED)])

    style.configure("TNotebook", background=COLOR_BG, borderwidth=0)
    style.configure("TNotebook.Tab", background=COLOR_TRACK, padding=(14, 6))
    style.map("TNotebook.Tab", background=[("selected", COLOR_SURFACE)])
    style.configure("Horizontal.TProgressbar", background=COLOR_PRIMARY,
                    troughcolor=COLOR_TRACK, borderwidth=0, lightcolor=COLOR_PRIMARY,
                    darkcolor=COLOR_PRIMARY)


def _setup_button_hover(master):
    """모든 tk.Button에 마우스를 올리면 살짝 어두워지는 효과를 준다."""
    def on_enter(event):
        button = event.widget
        if not isinstance(button, tk.Button) or str(button["state"]) == "disabled":
            return
        button._ui_normal_bg = button["bg"]
        button.configure(bg=shade(button, button["bg"], 0.93))

    def on_leave(event):
        button = event.widget
        normal = getattr(button, "_ui_normal_bg", None)
        if normal is not None:
            button.configure(bg=normal)
            button._ui_normal_bg = None

    master.bind_class("Button", "<Enter>", on_enter, add="+")
    master.bind_class("Button", "<Leave>", on_leave, add="+")


def shade(widget, color, amount):
    """색을 어둡게(amount < 1) 만든다."""
    r, g, b = (min(int(value / 257 * amount), 255) for value in widget.winfo_rgb(color))
    return f"#{r:02x}{g:02x}{b:02x}"


def style_widgets(win):
    """이미 만들어진 화면에 공통 색을 입힌다. 직접 지정한 색은 그대로 둔다."""
    setup_theme(win)
    wanted = {"Toplevel": {"bg": COLOR_BG}, "Frame": {"bg": COLOR_BG},
              "Label": {"bg": COLOR_BG, "fg": COLOR_TEXT},
              "Button": {"bg": COLOR_TRACK, "relief": "flat", "borderwidth": 0},
              "Entry": {"bg": COLOR_SURFACE, "relief": "flat", "highlightthickness": 1,
                        "highlightbackground": COLOR_BORDER}}

    def apply(widget):
        for option, value in wanted.get(widget.winfo_class(), {}).items():
            info = widget.configure(option)
            if len(info) == 5 and str(info[3]) == str(info[4]):   # 기본값일 때만 바꾼다
                widget.configure(**{option: value})
        for child in widget.winfo_children():
            apply(child)

    apply(win)


# ---------------------------------------------------------------
# 기본 위젯
# ---------------------------------------------------------------
def frame(parent, bg=None, **options):
    """부모와 같은 배경색의 프레임"""
    return tk.Frame(parent, bg=bg or parent["bg"], **options)


def label(parent, text="", kind="body", color=None, **options):
    """글자 라벨. kind: display / title / h2 / body / bold / muted / small / num"""
    if color is None:
        color = COLOR_MUTED if kind in _MUTED_KINDS else COLOR_TEXT
    return tk.Label(parent, text=text, font=FONTS[kind], fg=color, bg=parent["bg"], **options)


def button(parent, text, command, kind="primary", **options):
    """버튼. kind: primary(주요 동작) / soft(보조) / ghost(배경 없음) / danger(삭제)"""
    colors = {
        "primary": (COLOR_PRIMARY, "#ffffff"),
        "soft": (COLOR_TRACK, COLOR_TEXT),
        "ghost": (parent["bg"], COLOR_MUTED),
        "danger": (parent["bg"], COLOR_DANGER),
    }
    bg, fg = colors[kind]
    bg, fg = options.pop("bg", bg), options.pop("fg", fg)
    options.setdefault("padx", 14)
    options.setdefault("pady", 6)
    options.setdefault("font", FONTS["bold"] if kind == "primary" else FONTS["body"])
    return tk.Button(parent, text=text, command=command, bg=bg, fg=fg,
                     activebackground=bg, activeforeground=fg, relief="flat",
                     borderwidth=0, cursor="hand2", **options)


def link(parent, text, command):
    """글자만 있는 링크 (예: '열기 ›')"""
    widget = tk.Label(parent, text=text, font=FONTS["small"], fg=COLOR_PRIMARY,
                      bg=parent["bg"], cursor="hand2")
    widget.bind("<Button-1>", lambda event: command())
    return widget


def entry(parent, textvariable=None, **options):
    """입력란. 배치할 때 ipady=6 정도를 주면 보기 좋다."""
    return tk.Entry(parent, textvariable=textvariable, font=FONTS["body"], relief="flat",
                    bg=COLOR_SURFACE, highlightthickness=1, highlightbackground=COLOR_BORDER,
                    highlightcolor=COLOR_PRIMARY, **options)


def center_window(win, width, height):
    """창 크기를 정하고 화면 가운데에 띄운다. 화면보다 크면 화면에 맞춘다."""
    width = min(px(width), win.winfo_screenwidth() - px(40))
    height = min(px(height), win.winfo_screenheight() - px(80))
    x = (win.winfo_screenwidth() - width) // 2
    y = max((win.winfo_screenheight() - height) // 2 - px(20), 0)
    win.geometry(f"{width}x{height}+{x}+{y}")


def divider(parent):
    return tk.Frame(parent, bg=COLOR_BORDER, height=1)


def box(parent):
    """테두리가 있는 흰 상자. 안쪽에 커서가 있어도 테두리 색이 바뀌지 않게 한다."""
    return tk.Frame(parent, bg=COLOR_SURFACE, highlightthickness=1,
                    highlightbackground=COLOR_BORDER, highlightcolor=COLOR_BORDER)


def card(parent, title=None, action=None, on_action=None, pad=16):
    """흰 카드. (바깥 프레임, 내용 프레임)을 돌려준다. 바깥 프레임을 pack/grid 한다."""
    outer = box(parent)
    body = tk.Frame(outer, bg=COLOR_SURFACE)
    body.pack(fill="both", expand=True, padx=pad, pady=pad)
    if title:
        head = frame(body)
        head.pack(fill="x", pady=(0, 10))
        label(head, title, "h2").pack(side="left")
        if action:
            link(head, action, on_action).pack(side="right")
    return outer, body


def stat_tile(parent, title, value, unit="", color=COLOR_PRIMARY, note=""):
    """큰 숫자 하나를 보여주는 통계 타일"""
    outer = box(parent)
    tk.Frame(outer, bg=color, width=px(4)).pack(side="left", fill="y")
    body = tk.Frame(outer, bg=COLOR_SURFACE)
    body.pack(side="left", fill="both", expand=True, padx=14, pady=10)
    label(body, title, "small").pack(anchor="w")
    row = frame(body)
    row.pack(anchor="w")
    label(row, value, "num").pack(side="left")
    if unit:
        label(row, unit, "small").pack(side="left", padx=(4, 0), pady=(8, 0))
    label(body, note or " ", "small").pack(anchor="w")
    return outer


def segmented(parent, options, variable, command=None):
    """둘 중 하나를 고르는 선택 막대. options: [(값, 표시 글자), ...]"""
    box = tk.Frame(parent, bg=COLOR_TRACK, padx=3, pady=3)
    labels = {}

    def refresh():
        for value, widget in labels.items():
            active = variable.get() == value
            widget.config(bg=COLOR_SURFACE if active else COLOR_TRACK,
                          fg=COLOR_TEXT if active else COLOR_MUTED,
                          font=FONTS["bold"] if active else FONTS["body"])

    def choose(value):
        variable.set(value)
        refresh()
        if command:
            command()

    for value, text in options:
        widget = tk.Label(box, text=text, padx=12, pady=5, cursor="hand2")
        widget.pack(side="left", fill="x", expand=True)
        widget.bind("<Button-1>", lambda event, v=value: choose(v))
        labels[value] = widget
    box.refresh = refresh
    refresh()
    return box


def toast(widget, text, kind="ok"):
    """창 아래쪽에 잠깐 나타났다 사라지는 알림"""
    root = widget.winfo_toplevel()
    old = getattr(root, "_ui_toast", None)
    if old is not None and old.winfo_exists():
        old.destroy()
    message = tk.Label(root, text=text, bg=COLOR_DANGER if kind == "error" else COLOR_TEXT,
                       fg="#ffffff", font=FONTS["body"], padx=18, pady=9)
    message.place(relx=0.5, rely=1.0, y=-px(26), anchor="s")
    root._ui_toast = message
    root.after(2600, lambda: message.winfo_exists() and message.destroy())


class ScrollFrame(tk.Frame):
    """세로로 스크롤되는 영역. 내용은 .body 안에 넣는다. 내용이 짧으면 스크롤바를 숨긴다."""

    def __init__(self, parent):
        super().__init__(parent, bg=parent["bg"])
        self.canvas = tk.Canvas(self, bg=parent["bg"], highlightthickness=0)
        self.bar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.bar.set)
        self.canvas.pack(side="left", fill="both", expand=True)
        self.body = tk.Frame(self.canvas, bg=parent["bg"])
        self.window = self.canvas.create_window(0, 0, anchor="nw", window=self.body)
        self.body.bind("<Configure>", self._update)
        self.canvas.bind("<Configure>", self._update)
        self.bind("<Enter>", lambda event: self.bind_all("<MouseWheel>", self._wheel))
        self.bind("<Leave>", lambda event: self.unbind_all("<MouseWheel>"))
        self.bind("<Destroy>", self._on_destroy)

    def _on_destroy(self, event):
        if event.widget is self:
            self.unbind_all("<MouseWheel>")

    def _update(self, event=None):
        self.canvas.itemconfigure(self.window, width=self.canvas.winfo_width())
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        needed = self.body.winfo_reqheight() > self.canvas.winfo_height()
        if needed and not self.bar.winfo_ismapped():
            self.bar.pack(side="right", fill="y")
        elif not needed and self.bar.winfo_ismapped():
            self.bar.pack_forget()
            self.canvas.yview_moveto(0)

    def _wheel(self, event):
        if self.bar.winfo_ismapped():
            self.canvas.yview_scroll(-1 if event.delta > 0 else 1, "units")


# ---------------------------------------------------------------
# 캔버스에 직접 그리는 요소
# ---------------------------------------------------------------
def round_rect(canvas, x1, y1, x2, y2, radius, **options):
    """모서리가 둥근 사각형"""
    r = max(min(radius, (x2 - x1) / 2, (y2 - y1) / 2), 0)
    # 각 꼭짓점 앞뒤 점을 두 번씩 넣어야 변이 곧게 그려진다.
    points = [x1 + r, y1, x1 + r, y1, x2 - r, y1, x2 - r, y1, x2, y1,
              x2, y1 + r, x2, y1 + r, x2, y2 - r, x2, y2 - r, x2, y2,
              x2 - r, y2, x2 - r, y2, x1 + r, y2, x1 + r, y2, x1, y2,
              x1, y2 - r, x1, y2 - r, x1, y1 + r, x1, y1 + r, x1, y1]
    return canvas.create_polygon(points, smooth=True, **options)


def ring(parent, percent, size=64, color=COLOR_PRIMARY, width=7, text=None):
    """원형 진행률 표시"""
    side, stroke = px(size), px(width)
    canvas = tk.Canvas(parent, width=side, height=side, bg=parent["bg"], highlightthickness=0)
    edge = stroke / 2 + 1
    box = (edge, edge, side - edge, side - edge)
    canvas.create_oval(*box, outline=COLOR_TRACK, width=stroke)
    if percent > 0:
        canvas.create_arc(*box, start=90, extent=-min(percent, 99.99) * 3.6, style="arc",
                          outline=color, width=stroke)
    canvas.create_text(side / 2, side / 2, text=f"{percent}%" if text is None else text,
                       font=(FONT_FAMILY, max(size // 6, 8), "bold"), fill=COLOR_TEXT)
    return canvas


def check(parent, checked, command, color=COLOR_TODO, size=20):
    """둥근 체크 상자"""
    side = px(size)
    canvas = tk.Canvas(parent, width=side, height=side, bg=parent["bg"], highlightthickness=0,
                       cursor="hand2")
    if checked:
        round_rect(canvas, 1, 1, side - 1, side - 1, px(6), fill=color, outline=color)
        canvas.create_line(side * 0.27, side * 0.52, side * 0.44, side * 0.69,
                           side * 0.75, side * 0.33, fill="#ffffff", width=px(2),
                           capstyle="round", joinstyle="round")
    else:
        round_rect(canvas, 1, 1, side - 1, side - 1, px(6), fill=COLOR_SURFACE,
                   outline=COLOR_FAINT, width=px(1.5))
    canvas.bind("<Button-1>", lambda event: command())
    return canvas


def _nice_max(value):
    """차트 세로축의 최댓값을 보기 좋은 숫자로 올린다."""
    if value <= 0:
        return 100
    magnitude = 10 ** (len(str(int(value))) - 1)
    for step in (1, 2, 4, 5, 8, 10):
        if value <= step * magnitude:
            return step * magnitude
    return value


class BarChart(tk.Canvas):
    """묶음 막대 차트. series: [(이름, 색, 값 목록), ...]"""

    def __init__(self, parent, labels, series, height=230, highlight=None):
        super().__init__(parent, bg=parent["bg"], highlightthickness=0, height=px(height))
        self.labels, self.series, self.highlight = labels, series, highlight
        self.bind("<Configure>", lambda event: self.draw())

    def draw(self):
        self.delete("all")
        width, height = self.winfo_width(), self.winfo_height()
        if width < px(120):
            return
        left, right, top, bottom = px(52), px(8), px(34), px(28)
        plot_h = height - top - bottom
        base = top + plot_h
        peak = _nice_max(max([v for _, _, values in self.series for v in values] + [0]))

        x = left
        for name, color, _ in self.series:      # 범례
            round_rect(self, x, px(6), x + px(10), px(16), px(3), fill=color, outline=color)
            item = self.create_text(x + px(16), px(11), text=name, anchor="w",
                                    font=FONTS["small"], fill=COLOR_MUTED)
            x = self.bbox(item)[2] + px(16)

        group = (width - left - right) / max(len(self.labels), 1)
        if self.highlight is not None:          # 강조할 묶음의 배경
            center = left + group * (self.highlight + 0.5)
            round_rect(self, center - group / 2 + px(4), top - px(6),
                       center + group / 2 - px(4), height - px(2), px(8),
                       fill=COLOR_HOVER, outline=COLOR_HOVER)

        for i in range(5):                      # 가로 눈금선
            y = top + plot_h * (1 - i / 4)
            self.create_line(left, y, width - right, y, fill=COLOR_TRACK)
            self.create_text(left - px(8), y, text=f"{int(peak * i / 4):,}", anchor="e",
                             font=FONTS["small"], fill=COLOR_FAINT)

        bar = min(px(26), group * 0.3)
        gap = px(4)
        count = len(self.series)
        for i, text in enumerate(self.labels):
            center = left + group * (i + 0.5)
            for j, (_, color, values) in enumerate(self.series):
                value = values[i]
                x0 = center + (j - count / 2) * (bar + gap) + gap / 2
                if value <= 0:
                    continue
                y0 = base - plot_h * value / peak
                if base - y0 > px(8):           # 위쪽만 둥글게: 둥근 사각형 + 아래쪽 사각형
                    round_rect(self, x0, y0, x0 + bar, base, px(5), fill=color, outline=color)
                    self.create_rectangle(x0, base - px(5), x0 + bar, base, fill=color,
                                          outline=color)
                else:
                    self.create_rectangle(x0, y0, x0 + bar, base, fill=color, outline=color)
                self.create_text(x0 + bar / 2, y0 - px(8), text=f"{value:,}",
                                 font=(FONT_FAMILY, 8), fill=COLOR_MUTED)
            highlighted = i == self.highlight
            self.create_text(center, height - px(13), text=text,
                             font=FONTS["bold"] if highlighted else FONTS["small"],
                             fill=COLOR_TEXT if highlighted else COLOR_MUTED)
        self.create_line(left, base, width - right, base, fill=COLOR_BORDER)


class LineChart(tk.Canvas):
    """꺾은선 차트. points: [(라벨, 값), ...]"""

    def __init__(self, parent, points, color=COLOR_PRIMARY, unit="", height=170):
        super().__init__(parent, bg=parent["bg"], highlightthickness=0, height=px(height))
        self.points, self.color, self.unit = points, color, unit
        self.bind("<Configure>", lambda event: self.draw())

    def draw(self):
        self.delete("all")
        width, height = self.winfo_width(), self.winfo_height()
        if width < px(120) or not self.points:
            return
        left, right, top, bottom = px(48), px(30), px(26), px(26)
        values = [value for _, value in self.points]
        low, high = min(values), max(values)
        margin = max((high - low) * 0.25, 1)
        low, high = low - margin, high + margin
        plot_w, plot_h = width - left - right, height - top - bottom

        for i in range(3):
            y = top + plot_h * i / 2
            self.create_line(left, y, width - right, y, fill=COLOR_TRACK)
            self.create_text(left - px(8), y, text=f"{high - (high - low) * i / 2:.1f}",
                             anchor="e", font=FONTS["small"], fill=COLOR_FAINT)

        step = plot_w / max(len(self.points) - 1, 1)
        coords = []
        for i, (text, value) in enumerate(self.points):
            x = left + step * i if len(self.points) > 1 else left + plot_w / 2
            y = top + plot_h * (1 - (value - low) / (high - low))
            coords.append((x, y))
            self.create_text(x, height - px(12), text=text, font=FONTS["small"], fill=COLOR_MUTED)
        if len(coords) > 1:
            self.create_line(*[n for point in coords for n in point], fill=self.color,
                             width=px(2.5), capstyle="round", joinstyle="round")
        for i, (x, y) in enumerate(coords):
            last = i == len(coords) - 1
            radius = px(5) if last else px(3.5)
            self.create_oval(x - radius, y - radius, x + radius, y + radius,
                             fill=self.color if last else COLOR_SURFACE, outline=self.color,
                             width=px(2))
        x, y = coords[-1]
        self.create_text(x, y - px(15), text=f"{values[-1]:g}{self.unit}", font=FONTS["bold"],
                         fill=COLOR_TEXT)


class ScaleBar(tk.Canvas):
    """구간이 나뉜 가로 눈금 위에 현재 값을 표시한다. segments: [(끝값, 색, 이름), ...]"""

    def __init__(self, parent, value, start, segments):
        super().__init__(parent, bg=parent["bg"], highlightthickness=0, height=px(58))
        self.value, self.start, self.segments = value, start, segments
        self.bind("<Configure>", lambda event: self.draw())

    def draw(self):
        self.delete("all")
        width = self.winfo_width()
        if width < px(120):
            return
        left, right, y0, y1 = px(6), px(6), px(22), px(32)
        end = self.segments[-1][0]

        def to_x(number):
            ratio = (min(max(number, self.start), end) - self.start) / (end - self.start)
            return left + (width - left - right) * ratio

        previous = self.start
        for limit, color, name in self.segments:
            x0, x1 = to_x(previous), to_x(limit)
            round_rect(self, x0 + 1, y0, x1 - 1, y1, px(4), fill=color, outline=color)
            self.create_text((x0 + x1) / 2, y1 + px(13), text=name, font=FONTS["small"],
                             fill=COLOR_MUTED)
            previous = limit
        if self.value is not None:
            x = to_x(self.value)
            self.create_polygon(x - px(6), y0 - px(11), x + px(6), y0 - px(11), x, y0 - px(2),
                                fill=COLOR_TEXT, outline=COLOR_TEXT)


# ---------------------------------------------------------------
# 여러 화면이 같이 쓰는 화면 도우미
# ---------------------------------------------------------------
WEEKDAYS = ["월", "화", "수", "목", "금", "토", "일"]        # date.weekday() 순서


def format_day(day):
    """date를 '11월 15일 일요일' 형식으로 바꾼다."""
    return f"{day.month}월 {day.day}일 {WEEKDAYS[day.weekday()]}요일"


def page_header(app, parent, title, subtitle="", step=None, week_range=None):
    """화면 제목 줄. step이 1이면 하루씩, 7이면 한 주씩 이동하는 버튼을 오른쪽에 둔다.

    step=7일 때는 week_range(날짜) -> (시작일, 종료일) 함수를 함께 넘긴다.
    """
    bar = frame(parent)
    bar.pack(fill="x", pady=(0, 16))
    left = frame(bar)
    left.pack(side="left")
    label(left, title, "display").pack(anchor="w")
    if subtitle:
        label(left, subtitle, "muted").pack(anchor="w")
    if step:
        date_navigator(app, bar, step, week_range).pack(side="right")
    return bar


def date_navigator(app, parent, step, week_range=None):
    """'‹ 날짜 › | 오늘' 이동 상자. app.selected를 기준으로 app.select()를 부른다."""
    day = app.selected
    nav = box(parent)
    today = date.today()
    if step == 7:
        start, end = week_range(day)
        text = f"{start.month}월 {start.day}일 ~ {end.month}월 {end.day}일"
        before, after, now = "‹  지난주", "다음주  ›", "이번 주"
        is_now = week_range(day) == week_range(today)
        arrow = {}
    else:
        text = f"{day.year}. {day.month}. {day.day}. ({WEEKDAYS[day.weekday()]})"
        before, after, now = "‹", "›", "오늘"
        is_now = day == today
        arrow = {"font": FONTS["arrow"], "pady": 2}
    button(nav, before, lambda: app.select(day - timedelta(days=step)), "ghost",
           **arrow).pack(side="left")
    label(nav, text, "bold", width=20 if step == 7 else 16).pack(side="left")
    button(nav, after, lambda: app.select(day + timedelta(days=step)), "ghost",
           **arrow).pack(side="left")
    tk.Frame(nav, bg=COLOR_BORDER, width=1).pack(side="left", fill="y", pady=6)
    button(nav, now, lambda: app.select(today), "ghost",
           fg=COLOR_FAINT if is_now else COLOR_PRIMARY).pack(side="left")
    return nav


def tile_row(parent, tiles):
    """통계 타일을 같은 너비로 한 줄에 놓는다. tiles: stat_tile 인자(dict) 목록"""
    row = frame(parent)
    for column, options in enumerate(tiles):
        tile = stat_tile(row, **options)
        tile.grid(row=0, column=column, sticky="nsew", padx=(0 if column == 0 else 12, 0))
        row.columnconfigure(column, weight=1, uniform="tile")
    return row


def empty_state(parent, title, hint=""):
    """기록이 없을 때 보여주는 안내. 배치는 호출한 쪽에서 한다."""
    holder = frame(parent)
    label(holder, title, "bold", color=COLOR_MUTED).pack()
    if hint:
        label(holder, hint, "small", color=COLOR_FAINT).pack(pady=(2, 0))
    return holder
