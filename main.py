import tkinter as tk

class MainApplication(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("종합 기록 시스템 (메인)")
        self.geometry("600x650")
        self.resizable(False, False)

        # UI 기본 뼈대 구성 초기화
        self.create_base_widgets()

    def create_base_widgets(self):
        # 상단 타이틀 영역
        title_frame = tk.Frame(self, pady=10)
        title_frame.pack(fill="x")
        
        lbl_title = tk.Label(title_frame, text="종합 건강 기록 시스템", font=("맑은 고딕", 16, "bold"))
        lbl_title.pack()

        # [공통 레이아웃] 캘린더나 기능들이 배치될 상단 영역 프레임
        self.cal_container = tk.Frame(self, padx=20, pady=10)
        self.cal_container.pack(fill="both", expand=True)

        # [공통 레이아웃] 하단 상태 및 서브 모듈 연동 영역 프레임
        self.sub_container = tk.Frame(self, pady=15, padx=20)
        self.sub_container.pack(fill="x")

if __name__ == "__main__":
    app = MainApplication()
    app.mainloop()