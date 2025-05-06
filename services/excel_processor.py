import os
import time
import pandas as pd
from datetime import datetime
from typing import Callable, Dict, List, Tuple
from state.app_state import AppState

class ExcelProcessor:
    def __init__(self, state: AppState, progress_callback: Callable[[int, str], None]):
        self.state = state
        self.progress_callback = progress_callback
        self.reset_data()
        
    def reset_data(self):
        """데이터를 초기화합니다."""
        self.monthly_data = None
        self.vendor_mapping = None
        self.template_data = None
        
    def read_input_files(self) -> bool:
        """입력 파일들을 읽어옵니다."""
        try:
            # 데이터 초기화
            self.reset_data()
            
            # 1. 월별 RAW 파일 읽기
            self.progress_callback(5, "월별 거래명세서 파일을 읽는 중...")
            self.monthly_data = pd.read_excel(self.state.monthly_file.get(), engine='openpyxl')

            # 2. 거래처별 매핑 파일 읽기
            self.progress_callback(7, "거래처별 매핑 파일을 읽는 중...")
            self.vendor_mapping = pd.read_excel(self.state.vendor_file.get(), engine='openpyxl')
            
            # 3. 템플릿 파일 읽기
            self.progress_callback(10, "템플릿 파일을 읽는 중...")
            self.template_data = pd.read_excel(self.state.template_file.get(), engine='openpyxl')
            return True
            
        except Exception as e:
            print(f"파일 읽기 오류: {e}")
            self.reset_data()  # 오류 발생 시 데이터 초기화
            return False
            
    def filter_automation_targets(self) -> bool:
        """자동화 대상 거래처만 필터링합니다."""
        try:
            # 전체 거래처 처리 여부 확인
            # if self.state.process_all_vendors.get():
            #     # 전체 거래처 처리 시 필터링 건너뛰기
            #     self.progress_callback(20, "전체 거래처에 대한 거래명세서를 생성합니다.")
            #     total_vendors = len(self.monthly_data['거래처코드'].unique())
            #     if hasattr(self.progress_callback, '__self__'):
            #         self.progress_callback.__self__.update_vendor_count(total_vendors)
            #     return True
                
            # 1. 자동화 대상 거래처 필터링
            self.progress_callback(15, "자동화 대상 거래처 필터링 중...")
            if self.state.process_all_vendors.get():
                automation_targets = self.vendor_mapping
            else:
                automation_targets = self.vendor_mapping[
                    self.vendor_mapping['자동화_대상'] == True
                ]
            
            # 2. 월별 데이터에서 자동화 대상만 필터링
            self.progress_callback(20, "월별 데이터 필터링 중...")
            self.monthly_data = self.monthly_data[
                self.monthly_data['거래처코드'].isin(automation_targets['거래처코드'])
            ]
            
            # 총 거래처 수 표시
            total_vendors = len(automation_targets)
            if hasattr(self.progress_callback, '__self__'):
                self.progress_callback.__self__.update_vendor_count(total_vendors)
            return True
            
        except Exception as e:
            print(f"데이터 필터링 오류: {e}")
            return False
            
    def generate_statements(self) -> bool:
        """거래명세서를 생성합니다."""
        try:
            # 거래처별로 데이터 그룹화
            grouped_data = self.monthly_data.groupby('거래처코드')
            total_vendors = len(grouped_data)
            
            # 출력 디렉토리 가져오기
            output_dir = self.state.output_dir.get()
            
            for idx, (vendor_code, vendor_data) in enumerate(grouped_data, 1):
                if not self.state.is_processing:
                    print("작업이 취소되었습니다.")
                    return False
                    
                # 거래처명 가져오기
                vendor_name = self.vendor_mapping[
                    self.vendor_mapping['거래처코드'] == vendor_code
                ]['거래처명'].iloc[0]
                
                # 진행률 계산 (20% ~ 90%)
                progress = 20 + (idx / total_vendors * 70)
                self.progress_callback(
                    progress,
                    f"거래명세서 생성 중... ({idx}/{total_vendors}) - {vendor_name}"
                )
                
                # 날짜순 정렬
                vendor_data = vendor_data.sort_values(['년', '월', '일'])
                
                # TODO: 실제 엑셀 파일 생성 로직 구현
                # 1. 템플릿 복사
                # 2. 데이터 매핑
                # 3. 파일 저장
                # 파일명 형식: [폐기물]2024년_05월_거래처명_거래명세표.xlsx
                # 저장 경로: output_dir/[폐기물]2024년_05월_거래처명_거래명세표.xlsx
                
                # 임시로 처리 시간 시뮬레이션
                time.sleep(2)
                
            return True
            
        except Exception as e:
            print(f"거래명세서 생성 오류: {e}")
            return False
            
    def process_files(self) -> bool:
        """엑셀 파일들을 처리합니다."""
        try:
            # 취소 상태 확인
            if not self.state.is_processing or self.state.was_cancelled:
                print("작업이 취소되었습니다.")
                return False
                
            # 1. 입력 파일 읽기
            if not self.read_input_files():
                return False
                
            # 취소 상태 확인
            if not self.state.is_processing or self.state.was_cancelled:
                print("작업이 취소되었습니다.")
                return False
                
            # 2. 자동화 대상 필터링
            if not self.filter_automation_targets():
                return False
                
            # 취소 상태 확인
            if not self.state.is_processing or self.state.was_cancelled:
                print("작업이 취소되었습니다.")
                return False
                
            # 3. 거래명세서 생성
            if not self.generate_statements():
                return False
                
            # 최종 취소 상태 확인
            if not self.state.is_processing or self.state.was_cancelled:
                print("작업이 취소되었습니다.")
                return False
                
            return True
            
        except Exception as e:
            print(f"작업 처리 중 오류 발생: {e}")
            return False 