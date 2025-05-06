from tkinter import messagebox

def validate_inputs(monthly_file, vendor_file, template_file, output_dir):
    """입력값 검증"""
    if not monthly_file.get():
        messagebox.showerror("오류", "월별 올바로 거래 엑셀 파일을 선택해주세요.")
        return False
        
    if not vendor_file.get():
        messagebox.showerror("오류", "거래처 엑셀 파일을 선택해주세요.")
        return False
        
    if not template_file.get():
        messagebox.showerror("오류", "거래명세표 템플릿 엑셀 파일을 선택해주세요.")
        return False
        
    if not output_dir.get():
        messagebox.showerror("오류", "결과물 저장 디렉토리를 선택해주세요.")
        return False
        
    return True 