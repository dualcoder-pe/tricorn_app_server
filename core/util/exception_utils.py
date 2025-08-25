"""
exception_utils.py
------------------
공통 예외 상세 출력 유틸리티

- print_exception_detail(e):
    예외 발생 시 함수명, 파일명, 라인 정보를 출력

사용 예시:
    from lib.exception_utils import print_exception_detail
    ...
    try:
        ...
    except Exception as e:
        print_exception_detail(e)

2025-05-24 최초 작성
"""
import traceback

def print_exception_detail(e):
    """
    예외 발생 시 함수명, 파일명, 라인 정보를 출력합니다.
    Args:
        e (Exception): 예외 객체
    """
    print(f"[에러] {e.__class__.__name__}: {e}")
    tb = traceback.extract_tb(e.__traceback__)
    for frame in tb:
        print(f"  - 파일: {frame.filename} | 라인: {frame.lineno}")
