import tkinter as tk
from tkcalendar import Calendar
from datetime import datetime

class CalendarFeature:
    def __init__(self, parent_app):
        self.app = parent_app
        
        # [공통 상태 관리] 선택된 날짜 (YYYY-MM-DD 형식)
        self.selected_date = tk.StringVar(value=datetime.today().strftime('%Y-%m-%d'))

        # 기능 1 (이슈 #10) 관련 UI 컴포넌트 생성 및 바인딩
        self.init_calendar_ui()
        self.load_record_markers()

    def init_calendar_ui(self):
        # 1. 캘린더 위젯 생성 (연/월 이동, 한국어 로케일, 디자인 적용)
        self.cal = Calendar(
            self.app.cal_container,
            selectmode='day',
            date_pattern='yyyy-mm-dd',
            locale='ko_KR',
            font=("맑은 고딕", 11),
            background='#2c3e50',
            foreground='white',
            selectbackground='#3498db',
            selectforeground='white',
            normalbackground='white',
            normalforeground='black',
            weekendbackground='#ecf0f1',
            weekendforeground='#e74c3c',
            headersbackground='#bdc3c7',
            headersforeground='black'
        )
        self.cal.pack(fill="both", expand=True)

        # 2. 날짜 선택 이벤트 바인딩
        self.cal.bind("<<CalendarSelected>>", self.handle_date_selection)

        # 3. 하단 상태 표시 레이블
        self.lbl_status = tk.Label(
            self.app.sub_container, 
            text=f"현재 선택된 날짜: {self.selected_date.get()}", 
            font=("맑은 고딕", 12),
            fg="#1a73e8"
        )
        self.lbl_status.pack(anchor="w")

        # 4. 서브 기능 연동 안내 레이블 프레임
        sub_feature_frame = tk.LabelFrame(self.app.sub_container, text=" 연동된 서브 모듈 뷰 ", font=("맑은 고딕", 10), padx=10, pady=10)
        sub_feature_frame.pack(fill="both", expand=True, pady=5)

        self.lbl_sub_info = tk.Label(sub_feature_frame, text="날짜를 선택하면 해당 날짜의 데이터가 파이프라인을 통해 전달됩니다.", font=("맑은 고딕", 10), fg="gray")
        self.lbl_sub_info.pack(anchor="w", pady=5)

    def handle_date_selection(self, event):
        """날짜가 선택될 때 호출되는 이벤트 핸들러"""
        chosen_date = self.cal.get_date()
        self.selected_date.set(chosen_date)
        self.lbl_status.config(text=f"현재 선택된 날짜: {chosen_date}")
        
        # 캐스팅 파이프라인 호출
        self.dispatch_data_pipeline(chosen_date)

    def dispatch_data_pipeline(self, date_str):
        """
        [캐스팅 파이프라인] 
        선택된 날짜 정보를 다른 기능 모듈(칼로리, 투두 등)에 전달합니다.
        """
        print(f"[파이프라인 작동] 날짜 데이터 전파 ➔ {date_str}")
        self.lbl_sub_info.config(text=f"[{date_str}] 데이터가 각 모듈로 전달되었습니다.")

    def load_record_markers(self):
        """캘린더 날짜별 기록 존재 여부 표시 (점 또는 색상 처리)"""
        sample_recorded_dates = ['2026-10-01', '2026-10-05', '2026-10-10']
        
        for date_str in sample_recorded_dates:
            try:
                dt = datetime.strptime(date_str, '%Y-%m-%d').date()
                self.cal.calevent_create(dt, '기록있음', 'has_record')
            except Exception:
                pass
        
        self.cal.tag_config('has_record', background='#e8f0fe', foreground='black')