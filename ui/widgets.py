import tkinter as tk
from tkinter import ttk, filedialog
import os

from resources.labels import Labels
from resources.buttons import Buttons
from resources.file_types import FileTypes

class FileSelectionFrame(ttk.LabelFrame):
    def __init__(self, parent, title, file_var, file_types, is_dir=False):
        super().__init__(parent, text=title, padding=10)
        self.file_var = file_var
        self.file_types = file_types
        self.is_dir = is_dir
        
        # 최소 크기 설정
        self.configure(height=80)  # 최소 높이 설정
        
        # 파일 선택 프레임
        self.file_frame = ttk.Frame(self)
        self.file_frame.pack(fill="x", expand=True)
        
        # 파일 경로 입력 필드
        self.file_entry = ttk.Entry(self.file_frame, textvariable=file_var)
        self.file_entry.pack(side="left", fill="x", expand=True, padx=(0, 5))
        
        # 파일 선택 버튼
        self.browse_button = ttk.Button(
            self.file_frame,
            text="찾아보기",
            command=self.browse_file
        )
        self.browse_button.pack(side="right")
        
        # 선택된 파일명 표시 레이블
        self.filename_label = ttk.Label(self, text="")
        self.filename_label.pack(fill="x", expand=True, pady=(5, 0))
        
        # 파일 경로가 변경될 때마다 파일명 업데이트
        self.file_var.trace_add("write", self.update_filename)
        
    def browse_file(self):
        """파일 선택 다이얼로그를 표시합니다."""
        if self.is_dir:
            filename = filedialog.askdirectory()
        else:
            filename = filedialog.askopenfilename(filetypes=self.file_types)
            
        if filename:
            self.file_var.set(filename)
            
    def update_filename(self, *args):
        """선택된 파일의 이름을 업데이트합니다."""
        filepath = self.file_var.get()
        if filepath:
            filename = os.path.basename(filepath)
            if self.is_dir:
                self.filename_label.config(text=f"선택된 위치: {filename}")
            else:
                self.filename_label.config(text=f"선택된 파일: {filename}")
        else:
            self.filename_label.config(text="")

class DirectorySelectionFrame(ttk.Frame):
    def __init__(self, parent, label_text, variable, row):
        super().__init__(parent)
        self.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
        
        # 그리드 가중치 설정
        self.grid_columnconfigure(1, weight=1)
        
        self.variable = variable
        
        # 레이블
        self.label = ttk.Label(self, text=label_text, width=25)
        self.label.grid(row=0, column=0, padx=5)
        
        # 입력 필드
        self.entry = ttk.Entry(self, textvariable=variable, width=50)
        self.entry.grid(row=0, column=1, padx=5, sticky=(tk.W, tk.E))
        
        # 찾아보기 버튼
        self.browse_button = ttk.Button(self, text=Buttons.BROWSE, 
                                      command=self.browse_directory)
        self.browse_button.grid(row=0, column=2, padx=5)
        
    def browse_directory(self):
        dirname = filedialog.askdirectory()
        if dirname:
            self.variable.set(dirname)

class ProgressFrame(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        
        # 그리드 가중치 설정
        self.grid_columnconfigure(0, weight=1)
        
        # 거래처 수 표시 레이블
        self.vendor_count_label = ttk.Label(self, text="")
        self.vendor_count_label.grid(row=0, column=0, pady=(0, 3), sticky=(tk.W, tk.E))
        
        # 진행 상태 레이블
        self.status_label = ttk.Label(self, text="")
        self.status_label.grid(row=1, column=0, pady=(0, 3), sticky=(tk.W, tk.E))
        
        # 진행 바
        self.progress_bar = ttk.Progressbar(
            self,
            mode='determinate'
        )
        self.progress_bar.grid(row=2, column=0, sticky=(tk.W, tk.E), padx=20, pady=(0, 3))
        
    def update_progress(self, value: int, message: str):
        """진행 상태를 업데이트합니다."""
        self.progress_bar['value'] = value
        self.status_label['text'] = message
        
    def update_vendor_count(self, count: int):
        """거래처 수를 업데이트합니다."""
        self.vendor_count_label['text'] = f"총 {count}개의 거래처에 대한 거래명세서를 생성합니다."
        
    def reset(self):
        self.progress_bar['value'] = 0
        self.status_label['text'] = "" 