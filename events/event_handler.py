import os
import subprocess
import threading
from typing import Callable, Optional
from tkinter import messagebox

from resources.messages import Success, Error, Cancel, Progress
from state.app_state import AppState

class EventHandler:
    def __init__(self, state: AppState, progress_callback: Callable[[int, str], None]):
        self.state = state
        self.progress_callback = progress_callback
        self.process_button = None  # 시작 버튼 참조를 저장할 변수
        self.excel_processor = None  # 엑셀 프로세서 참조를 저장할 변수
        self.cancel_thread = None    # 취소 처리를 위한 스레드
        
    def set_process_button(self, button):
        """시작 버튼 참조를 설정합니다."""
        self.process_button = button
        
    def set_excel_processor(self, processor):
        """엑셀 프로세서 참조를 설정합니다."""
        self.excel_processor = processor
        
    def on_input_change(self, *args):
        """입력 필드가 변경되었을 때 호출되는 콜백 함수입니다."""
        if self.state.is_processing:
            return
            
        if self.state.has_paths_changed():
            self.state.update_last_paths()
            self.progress_callback(0, "")
            
    def on_start_processing(self):
        """작업 시작 이벤트를 처리합니다."""
        if not self.validate_inputs():
            return False
            
        # 취소 상태 초기화
        self.state.was_cancelled = False
        self.state.can_restart = False
        self.state.is_processing = True
        self.progress_callback(0, Progress.PREPARING)
        if self.process_button:
            self.process_button.config(state="disabled")
        return True
        
    def _handle_cancel(self):
        """취소 처리를 수행하는 내부 메서드입니다."""
        # 취소 상태 설정
        self.state.is_processing = False
        self.state.was_cancelled = True
        
        # 진행 상태 업데이트
        self.progress_callback(0, "취소 중입니다...")
        
        # 작업 스레드가 존재하고 실행 중인 경우에만 처리
        if self.state.progress_thread and self.state.progress_thread.is_alive():
            # 스레드가 완전히 종료될 때까지 대기
            while self.state.progress_thread.is_alive():
                self.state.progress_thread.join(timeout=0.1)  # 0.1초마다 체크
            self.state.progress_thread = None
        
        # 데이터 초기화
        if self.excel_processor:
            self.excel_processor.reset_data()
            
        # 재시작 가능 상태로 설정
        self.state.can_restart = True
        self.progress_callback(0, "다시 시작할 준비가 되었습니다.")
        
        # 시작 버튼 활성화
        if self.process_button:
            self.process_button.config(state='normal')
            
        self.cancel_thread = None
        
    def on_cancel_processing(self):
        """처리를 취소합니다."""
        # 이미 취소 중이면 무시
        if self.cancel_thread and self.cancel_thread.is_alive():
            return
            
        # 시작 버튼 비활성화
        if self.process_button:
            self.process_button.config(state="disabled")
            
        # 취소 처리를 별도의 스레드에서 실행
        self.cancel_thread = threading.Thread(target=self._handle_cancel)
        self.cancel_thread.daemon = True
        self.cancel_thread.start()
        
    def on_processing_complete(self):
        """작업 완료 이벤트를 처리합니다."""
        self.state.is_processing = False
        
        # 취소된 경우 완료 처리를 하지 않음
        if self.state.was_cancelled:
            self.state.was_cancelled = False
            return
            
        self.progress_callback(100, Progress.COMPLETE)
        messagebox.showinfo(
            Success.TITLE,
            Success.CONTENT.format(self.state.output_dir.get())
        )
        self.open_output_directory()
        
        # 시작 버튼 활성화
        if self.process_button:
            self.process_button.config(state="normal")
        
    def on_processing_error(self):
        """작업 오류 이벤트를 처리합니다."""
        self.state.is_processing = False
        
        # 취소된 경우 오류 처리를 하지 않음
        if self.state.was_cancelled:
            self.state.was_cancelled = False
            return
            
        self.progress_callback(0, Progress.FAILED)
        messagebox.showerror(Error.TITLE, Error.CONTENT)
        
        # 시작 버튼 활성화
        if self.process_button:
            self.process_button.config(state="normal")
        
    def validate_inputs(self) -> bool:
        """입력값의 유효성을 검사합니다."""
        paths = self.state.get_current_paths()
        
        # 월별 거래명세서 파일 검증
        if not paths.monthly_file:
            messagebox.showerror(
                "입력 오류",
                "월별 거래명세서 파일을 선택해주세요."
            )
            return False
        if not os.path.exists(paths.monthly_file):
            messagebox.showerror(
                "파일 오류",
                "선택한 월별 거래명세서 파일이 존재하지 않습니다."
            )
            return False
            
        # 거래처별 거래명세서 파일 검증
        if not paths.vendor_file:
            messagebox.showerror(
                "입력 오류",
                "거래처별 거래명세서 파일을 선택해주세요."
            )
            return False
        if not os.path.exists(paths.vendor_file):
            messagebox.showerror(
                "파일 오류",
                "선택한 거래처별 거래명세서 파일이 존재하지 않습니다."
            )
            return False
            
        # 템플릿 파일 검증
        if not paths.template_file:
            messagebox.showerror(
                "입력 오류",
                "템플릿 파일을 선택해주세요."
            )
            return False
        if not os.path.exists(paths.template_file):
            messagebox.showerror(
                "파일 오류",
                "선택한 템플릿 파일이 존재하지 않습니다."
            )
            return False
            
        # 출력 디렉토리 검증
        if not paths.output_dir:
            messagebox.showerror(
                "입력 오류",
                "결과물이 저장될 디렉토리를 선택해주세요."
            )
            return False
        if not os.path.exists(paths.output_dir):
            messagebox.showerror(
                "디렉토리 오류",
                "선택한 출력 디렉토리가 존재하지 않습니다."
            )
            return False
            
        return True
        
    def open_output_directory(self):
        """결과물이 저장된 디렉토리를 파일 탐색기에서 엽니다."""
        output_path = self.state.output_dir.get()
        if os.path.exists(output_path):
            try:
                if os.name == 'nt':  # Windows
                    os.startfile(output_path)
                elif os.name == 'posix':  # macOS, Linux
                    if os.path.exists('/usr/bin/open'):  # macOS
                        subprocess.run(['open', output_path])
                    else:  # Linux
                        subprocess.run(['xdg-open', output_path])
            except Exception as e:
                print(f"디렉토리를 여는 중 오류 발생: {e}") 