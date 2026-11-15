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
