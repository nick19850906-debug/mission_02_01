import functools
import sys
import time
import traceback
import logging

logging.basicConfig(
    filename='app.log', 
    level=logging.INFO, 
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

class BudgetAppError(Exception):
    def __init__(self, message, hint=""):
        self.message = message
        self.hint = hint

def with_logging(func):
    """
    실행 로그를 남기는 데코레이터
    공통 관심사(로그)를 분리하여 함수의 실행을 추적합니다.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        logging.info(f"Function {func.__name__} called.")
        return func(*args, **kwargs)
    return wrapper

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
            with open("error.log", "a", encoding="utf-8") as f:
                f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Unknown Error in {func.__name__}:\n")
                traceback.print_exc(file=f)
            print(f"[알 수 없는 오류] {e}")
            print("[힌트] 프로그램 실행 중 예상치 못한 문제가 발생했습니다. error.log를 확인하세요.")
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
