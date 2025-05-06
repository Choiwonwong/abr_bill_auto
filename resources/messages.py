class Success:
    TITLE = "완료"
    CONTENT = "거래명세서 작성이 완료되었습니다.\n\n결과물은 여기에 저장되었어요:\n{}\n\n확인 버튼을 눌러주세요."

class Error:
    TITLE = "오류 발생"
    CONTENT = "작업 중에 문제가 생겼어요.\n\n다시 한번 시도해주시겠어요?"

class Cancel:
    TITLE = "작업 중단"
    CONTENT = "작업 중단되었습니다.\n\n다시 시작하시려면 확인 버튼을 눌러주세요."

class Progress:
    PREPARING = "처리 준비 중..."
    PROCESSING = "진행 중... {}/{}"
    COMPLETE = "처리 완료!"
    FAILED = "처리 실패!"
    CANCELLED = "처리 중단됨" 