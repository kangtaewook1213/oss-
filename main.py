import tkinter as tk
from tkcalendar import Calendar
from datetime import datetime

class MainApplication(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("종합 기록 시스템 (메인 캘린더)")
        self.geometry("600x650")
        self.resizable(False, False)

        # [공통 상태 관리] 선택된 날짜 (YYYY-MM-DD 형식)
        self.selected_date = tk.StringVar(value=datetime.today().strftime('%Y-%m-%d'))

        # UI 구성 초기화
        self.create_widgets()
        
        # 샘플 기록 표시 (추후 DB나 파일 연동으로 대체 가능)
        self.load_record_markers()

    def create_widgets(self):
        # 상단 타이틀 영역
        title_frame = tk.Frame(self, pady=10)
        title_frame.pack(fill="x")
        
        lbl_title = tk.Label(title_frame, text="메인 화면 및 날짜 선택", font=("맑은 고딕", 16, "bold"))
        lbl_title.pack()

        # 캘린더 위젯 (연/월 이동 기본 지원)
        cal_frame = tk.Frame(self, padx=20, pady=10)
        cal_frame.pack(fill="both", expand=True)

        self.cal = Calendar(
            cal_frame,
            selectmode='day',
            date_pattern='yyyy-mm-dd',
            locale='ko_KR',
            font=("맑은 고딕", 11),

            background='#2c3e50',         # 달력 전체 배경색 (어두운톤 등)
            foreground='white',           # 기본 글자색
            selectbackground='#3498db',   # 사용자가 날짜를 선택했을 때의 배경색
            selectforeground='white',     # 선택한 날짜의 글자색
            normalbackground='white',     # 평일 날짜 칸 배경색
            normalforeground='black',     # 평일 날짜 칸 글자색
            weekendbackground='#ecf0f1',  # 주말 배경색
            weekendforeground='#e74c3c',  # 주말 글자색 (예: 빨간색)
            headersbackground='#bdc3c7',  # 요일(월, 화, 수...) 헤더 배경색
            headersforeground='black'     # 요일 헤더 글자색
        )
        self.cal.pack(fill="both", expand=True)

        # 날짜 선택 이벤트 바인딩
        self.cal.bind("<<CalendarSelected>>", self.handle_date_selection)

        # 하단 상태 및 데이터 파이프라인 연동 영역
        status_frame = tk.Frame(self, pady=15, padx=20)
        status_frame.pack(fill="x")

        self.lbl_status = tk.Label(
            status_frame, 
            text=f"현재 선택된 날짜: {self.selected_date.get()}", 
            font=("맑은 고딕", 12),
            fg="#1a73e8"
        )
        self.lbl_status.pack(anchor="w")

        # 서브 기능 영역 (팀원들이 개발한 기능을 이곳이나 파이프라인을 통해 연결)
        sub_feature_frame = tk.LabelFrame(self, text=" 연동된 서브 모듈 뷰 ", font=("맑은 고딕", 10), padx=10, pady=10)
        sub_feature_frame.pack(fill="both", expand=True, padx=20, pady=10)

        self.lbl_sub_info = tk.Label(sub_feature_frame, text="날짜를 선택하면 해당 날짜의 데이터가 파이프라인을 통해 전달됩니다.", font=("맑은 고딕", 10), fg="gray")
        self.lbl_sub_info.pack(anchor="w", pady=5)

    def handle_date_selection(self, event):
        """날짜가 선택될 때 호출되는 이벤트 핸들러"""
        chosen_date = self.cal.get_date()
        self.selected_date.set(chosen_date)
        self.lbl_status.config(text=f"현재 선택된 날짜: {chosen_date}")
        
        # 캐스팅 파이프라인 호출 (다른 기능 모듈로 데이터 전달)
        self.dispatch_data_pipeline(chosen_date)

    def dispatch_data_pipeline(self, date_str):
        """
        [캐스팅 파이프라인] 
        선택된 날짜 정보를 시스템 전역 또는 다른 기능(칼로리, daily-todo, 소수 추적기 등)에 전달합니다.
        """
        print(f"[파이프라인 작동] 날짜 데이터 전파 ➔ {date_str}")
        
        #코드를 합칠 때 이 부분에 각 기능 모듈 함수를 연결.
        # 예시:
        # calorie_module.update_view(date_str)
        # todo_module.load_todos(date_str)
        
        self.lbl_sub_info.config(text=f"[{date_str}] 데이터가 각 모듈로 전달되었습니다.")

    def load_record_markers(self):
        """캘린더 날짜별 기록 존재 여부 표시 (점 또는 색상 처리)"""
        # 예시 데이터 (식단/운동 등 기록이 있는 날짜)
        sample_recorded_dates = ['2026-10-01', '2026-10-05', '2026-10-10']
        
        for date_str in sample_recorded_dates:
            try:
                dt = datetime.strptime(date_str, '%Y-%m-%d').date()
                self.cal.calevent_create(dt, '기록있음', 'has_record')
            except Exception:
                pass
        
        # 태그 스타일 설정 (배경색 변경)
        self.cal.tag_config('has_record', background='#e8f0fe', foreground='black')

if __name__ == "__main__":
    app = MainApplication()
    app.mainloop()