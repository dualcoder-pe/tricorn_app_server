"""
db.py

DB 연결, 세션 생성, 의존성 관리를 위한 공통 모듈

- 의존성: SQLAlchemy, python-dotenv
- 환경변수 파일(.env)에서 DB_URL 관리
- get_engine(), get_sessionmaker(), get_db() 함수 제공
- 버전: 1.0.0
- 작성일: 2025-05-17
- 작성자: 사용자 요청 기반
- 변경이력:
    - v1.0.0: 최초 작성

예시 .env 파일:
    DB_URL=mysql+pymysql://user:password@localhost:3306/yourdb

예시 사용법:
    from config.db import get_db
    with get_db() as session:
        ...
"""

import os
from typing import Any, Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager
from dotenv import load_dotenv
import logging

# .env 파일 로드
load_dotenv()

DB_URL = os.getenv("DB_URL")

if not DB_URL:
    raise RuntimeError(
        "DB_URL 환경변수가 설정되어 있지 않습니다. .env 파일을 확인하세요."
    )

engine = create_engine(DB_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

logger = logging.getLogger(__name__)


@contextmanager
def get_db() -> Generator[Session, Any, None]:
    """
    SQLAlchemy 세션을 생성하고, 사용 후 안전하게 반환하는 컨텍스트 매니저

    예시:
        with get_db() as session:
            ...
    """
    session = SessionLocal()
    try:
        yield session
    except Exception as e:
        session.rollback()
        logger.error(f"DB 세션 에러: {e}")
        raise
    finally:
        session.close()


# get_engine, get_sessionmaker 등 필요시 추가 확장 가능
