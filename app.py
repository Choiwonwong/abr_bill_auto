import tkinter as tk
from tkinter import ttk
import threading

from ui.styles import setup_styles
from ui.widgets import FileSelectionFrame, DirectorySelectionFrame, ProgressFrame
from resources.window import WindowConfig
from resources.labels import Labels
from resources.buttons import Buttons
from state.app_state import AppState
from events.event_handler import EventHandler
from services.excel_processor import ExcelProcessor
from resources.file_types import FileTypes

class ExcelProcessorApp:
    def __init__(self, root):
        self.root = root
        self.root.title(WindowConfig.TITLE)
        self.root.geometry(WindowConfig.GEOMETRY)
        self.root.minsize(WindowConfig.WIDTH, WindowConfig.HEIGHT)  # 최소 크기 설정
        
        # 스타일 설정
        setup_styles()
        
        # 메인 프레임
        self.main_frame = ttk.Frame(root, padding="20")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 그리드 가중치 설정
        root.grid_rowconfigure(0, weight=1)
        root.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(1, weight=1)  # 입력 프레임이 확장되도록 설정
        
        # 상태 관리
        self.state = AppState()
        
        # 진행 상태 표시 프레임 생성
        self.progress_frame = ProgressFrame(self.main_frame)
        
        # 이벤트 핸들러
        self.event_handler = EventHandler(
            self.state,
            self.progress_frame.update_progress
        )
        
        # 엑셀 처리 서비스
        self.excel_processor = ExcelProcessor(
            self.state,
            self.progress_frame.update_progress
        )
        
        # UI 구성
        self.create_widgets()
        
        # 이벤트 핸들러에 시작 버튼 참조 전달
        self.event_handler.set_process_button(self.process_button)
        
        # 이벤트 핸들러에 엑셀 프로세서 참조 전달
        self.event_handler.set_excel_processor(self.excel_processor)
        
        # 입력 변경 감지 설정
        self.setup_input_traces()
        
    def setup_input_traces(self):
        """입력 필드의 변경을 감지하는 트레이스를 설정합니다."""
        self.state.monthly_file.trace_add("write", self.event_handler.on_input_change)
        self.state.vendor_file.trace_add("write", self.event_handler.on_input_change)
        self.state.template_file.trace_add("write", self.event_handler.on_input_change)
        self.state.output_dir.trace_add("write", self.event_handler.on_input_change)
        
    def create_widgets(self):
        """위젯들을 생성합니다."""
        # 제목
        title_label = ttk.Label(self.main_frame, text=Labels.TITLE, style="Header.TLabel")
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 10))
        
        # 입력 프레임
        self.input_frame = ttk.LabelFrame(self.main_frame, text="입력 파일 선택", padding=10)
        self.input_frame.grid(row=1, column=0, columnspan=3, sticky="nsew", padx=22, pady=5)
        self.input_frame.grid_columnconfigure(0, weight=1)
        
        # 입력 프레임의 최소 크기 설정
        self.input_frame.configure(height=400)  # 최소 높이 설정
        
        # 월별 거래명세서 파일 선택
        self.monthly_frame = FileSelectionFrame(
            self.input_frame,
            "월별 거래명세서 파일",
            self.state.monthly_file,
            FileTypes.EXCEL
        )
        self.monthly_frame.pack(fill="x", expand=True, pady=(0, 10))
        
        # 거래처별 거래명세서 파일 선택
        self.vendor_frame = FileSelectionFrame(
            self.input_frame,
            "거래처별 거래명세서 파일",
            self.state.vendor_file,
            FileTypes.EXCEL
        )
        self.vendor_frame.pack(fill="x", expand=True, pady=(0, 10))
        
        # 템플릿 파일 선택
        self.template_frame = FileSelectionFrame(
            self.input_frame,
            "템플릿 파일",
            self.state.template_file,
            FileTypes.EXCEL
        )
        self.template_frame.pack(fill="x", expand=True, pady=(0, 10))
        
        # 출력 디렉토리 선택
        self.output_frame = FileSelectionFrame(
            self.input_frame,
            "결과물 저장 위치",
            self.state.output_dir,
            None,
            is_dir=True
        )
        self.output_frame.pack(fill="x", expand=True)
        
        # 진행 상태 표시
        self.progress_frame.grid(row=2, column=0, columnspan=3, sticky="ew", pady=10)
        
        # 버튼 프레임
        button_frame = ttk.Frame(self.main_frame)
        button_frame.grid(row=3, column=0, columnspan=3, pady=10)
        
        # 전체 거래처 선택 체크박스
        self.process_all_checkbox = ttk.Checkbutton(
            button_frame,
            text="전체 거래처",
            variable=self.state.process_all_vendors
        )
        self.process_all_checkbox.grid(row=0, column=0, padx=(0, 20))
        
        # 시작 버튼
        self.process_button = ttk.Button(
            button_frame,
            text=Buttons.CONFIRM,
            command=self.start_processing,
            style="Start.TButton"
        )
        self.process_button.grid(row=0, column=1, padx=5)
        
        # 취소 버튼
        self.cancel_button = ttk.Button(
            button_frame,
            text=Buttons.CANCEL,
            command=self.event_handler.on_cancel_processing,
            style="Cancel.TButton"
        )
        self.cancel_button.grid(row=0, column=2, padx=5)
        
    def start_processing(self):
        """작업을 시작합니다."""
        if not self.event_handler.on_start_processing():
            return
            
        # 진행 상태 업데이트 스레드 시작
        self.state.progress_thread = threading.Thread(target=self.process_files)
        self.state.progress_thread.start()
        
    def process_files(self):
        """엑셀 파일들을 처리합니다."""
        try:
            if self.excel_processor.process_files():
                self.root.after(0, self.event_handler.on_processing_complete)
            else:
                self.root.after(0, self.event_handler.on_processing_error)
        except Exception as e:
            print(f"작업 처리 중 오류 발생: {e}")
            self.root.after(0, self.event_handler.on_processing_error)
        
    def select_file(self, string_var):
        """파일 선택 다이얼로그를 표시합니다."""
        from tkinter import filedialog
        filename = filedialog.askopenfilename(
            title="파일 선택",
            filetypes=[
                ("Excel 파일", "*.xlsx"),
                ("모든 파일", "*.*")
            ]
        )
        if filename:
            string_var.set(filename)
            
    def select_directory(self):
        """디렉토리 선택 다이얼로그를 표시합니다."""
        from tkinter import filedialog
        directory = filedialog.askdirectory(
            title="결과물 저장 디렉토리 선택"
        )
        if directory:
            self.state.output_dir.set(directory) 