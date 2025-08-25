"""
logger.py

백테스팅 프로젝트 전용 로깅 유틸리티
- 모든 로그는 script/log/ 폴더 아래에 yyyyMMdd_HHmmss.log 형태로 저장
- 로그 레벨: INFO 이상
- 파일 + 콘솔 동시 출력
- 사용 예시:
    from lib.logger import get_logger
    logger = get_logger()
    logger.info("로그 메시지")

작성자: Cascade AI
버전: 1.1
변경이력:
- 최초 작성: 2025-05-29
- script/log 경로 고정, 파일+콘솔 동시 출력, 24시간제 파일명, 싱글턴 개선: 2025-05-29
"""

import logging
import os
from datetime import datetime

# 프로젝트 루트 기준 script/log 경로 고정
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
LOG_DIR = os.path.join(PROJECT_ROOT, "python", "log")
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)


# 파일명: yyyyMMdd_HHmmss.log (24시간제, 중복 방지)
LOG_FILE = os.path.join(LOG_DIR, datetime.now().strftime("%Y%m%d_%H%M%S.log"))
print("Project Root 경로:", PROJECT_ROOT)
print("LOG DIR 경로:", LOG_DIR)
print("LOG_FILE 경로:", LOG_FILE)
# 싱글턴 패턴으로 logger 재사용
_logger = None


def get_logger(name: str = "trifin") -> logging.Logger:
    """
    script/log/ 폴더에 yyyyMMdd_HHmmss.log로 저장되는 로거 반환
    여러 모듈에서 호출해도 동일 파일, 동일 포맷 사용
    파일 + 콘솔 핸들러 모두 활성화
    """
    global _logger
    if _logger is not None:
        return _logger
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(module)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    # 파일 핸들러
    fh = logging.FileHandler(LOG_FILE, encoding="utf-8")
    fh.setLevel(logging.INFO)
    fh.setFormatter(formatter)
    logger.addHandler(fh)
    # 콘솔 핸들러
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    logger.propagate = False
    _logger = logger
    return logger
