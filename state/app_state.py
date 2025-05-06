import tkinter as tk
import threading
from dataclasses import dataclass
from typing import Optional

@dataclass
class FilePaths:
    monthly_file: str = ""
    vendor_file: str = ""
    template_file: str = ""
    output_dir: str = ""

class AppState:
    def __init__(self):
        # 파일 경로 변수들
        self.monthly_file = tk.StringVar()
        self.vendor_file = tk.StringVar()
        self.template_file = tk.StringVar()
        self.output_dir = tk.StringVar()
        
        # 전체 거래처 처리 여부
        self.process_all_vendors = tk.BooleanVar(value=False)
        
        # 이전 값 저장용 변수들
        self.last_paths = FilePaths()
        
        # 작업 상태
        self.is_processing = False
        self.progress_thread: Optional[threading.Thread] = None
        self.was_cancelled = False  # 취소 상태 추가
        self.can_restart = False    # 재시작 가능 상태 추가
        
    def get_current_paths(self) -> FilePaths:
        """현재 파일 경로들을 반환합니다."""
        return FilePaths(
            monthly_file=self.monthly_file.get(),
            vendor_file=self.vendor_file.get(),
            template_file=self.template_file.get(),
            output_dir=self.output_dir.get()
        )
        
    def has_paths_changed(self) -> bool:
        """파일 경로가 변경되었는지 확인합니다."""
        current = self.get_current_paths()
        return (current.monthly_file != self.last_paths.monthly_file or
                current.vendor_file != self.last_paths.vendor_file or
                current.template_file != self.last_paths.template_file or
                current.output_dir != self.last_paths.output_dir)
                
    def update_last_paths(self):
        """마지막 파일 경로들을 업데이트합니다."""
        self.last_paths = self.get_current_paths()
        
    def reset_processing_state(self):
        """작업 상태를 초기화합니다."""
        self.is_processing = False
        self.progress_thread = None
        self.was_cancelled = False
        self.can_restart = False 