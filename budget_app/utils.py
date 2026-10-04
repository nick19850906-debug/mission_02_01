import functools
import sys
import time

class BudgetAppError(Exception):
    def __init__(self, message, hint=""):
        self.message = message
        self.hint = hint

def handle_errors(func):
    """
    공통 예외 처리 데코레이터
    스택트레이스를 숨기고 친절한 메시지를 출력합니다.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except BudgetAppError as e:
            print(f"[오류] {e.message}")
            if e.hint:
                print(f"[힌트] {e.hint}")
            sys.exit(1)
        except Exception as e:
            print(f"[알 수 없는 오류] {e}")
            print("[힌트] 프로그램 실행 중 예상치 못한 문제가 발생했습니다.")
            sys.exit(1)
    return wrapper

def measure_time(func):
    """실행 시간 측정 데코레이터"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        # 필요 시 아래 주석을 해제하여 사용
        # print(f"[{func.__name__} 실행 시간: {end - start:.4f}초]") 
        return result
    return wrapper
