from tkinter import ttk

def setup_styles():
    style = ttk.Style()
    
    # 기본 버튼 스타일
    style.configure("TButton", 
                   padding=5, 
                   font=("Helvetica", 10))
    
    # 시작 버튼 스타일
    style.configure("Start.TButton",
                   padding=(20, 10),
                   font=("Helvetica", 11, "bold"))
    
    # 중단 버튼 스타일
    style.configure("Cancel.TButton",
                   padding=(20, 10),
                   font=("Helvetica", 11, "bold"))
    
    # 기본 레이블 스타일
    style.configure("TLabel", 
                   padding=5, 
                   font=("Helvetica", 10))
    
    # 헤더 레이블 스타일
    style.configure("Header.TLabel", 
                   font=("Helvetica", 12, "bold"))
    
    # 파일명 레이블 스타일
    style.configure("File.TLabel", 
                   font=("Helvetica", 9))
    
    # 프로그레스 바 스타일
    style.configure("Horizontal.TProgressbar",
                   troughcolor='#E0E0E0',
                   background='#4CAF50',
                   thickness=25)
    
    return style 