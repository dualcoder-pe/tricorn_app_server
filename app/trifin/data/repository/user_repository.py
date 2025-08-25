"""
user_repository.py

User 모델을 이용한 사용자 데이터의 삽입, 조회 기능 제공

- 의존성: SQLAlchemy
- 사용법:
    from repository.user_repository import insert_user, get_user_by_id, get_user_by_sso_id, get_users
- 버전: 1.0.0
- 작성일: 2025-06-07
- 작성자: 사용자 요청 기반

참고: 트랜잭션/세션 관리는 외부에서 주입
"""

from typing import List, Optional

from sqlalchemy.exc import SQLAlchemyError

from app.trifin.data.repository.models.user_table import User
from core.config.db import get_db
from core.util.log_util import logger


def insert_user(user_obj: User) -> User:
    """
    단일 User 객체를 DB에 저장합니다.
    Args:
        user_obj (User): 저장할 User 객체
    Returns:
        User: 저장된 User 객체
    Raises:
        SQLAlchemyError: DB 삽입 중 오류 발생 시
    예시:
        >>> user = User(name='홍길동')
        >>> insert_user(user)
    """
    with get_db() as session:
        try:
            session.add(user_obj)
            session.commit()
            session.refresh(user_obj)
            logger.info(f"User 데이터 저장 성공: {user_obj}")
            return user_obj
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"User 데이터 저장 실패: {e}")
            raise


def get_user_by_id(user_id: int) -> Optional[User]:
    """
    ID로 단일 사용자(User) 데이터를 조회합니다.
    Args:
        user_id (int): User ID
    Returns:
        Optional[User]: User 객체 또는 None
    """
    with get_db() as session:
        return session.query(User).filter(User.id == user_id).first()


def get_users(limit: int = 100) -> List[User]:
    """
    전체 사용자 리스트를 조회합니다.
    Args:
        limit (int): 최대 반환 개수
    Returns:
        List[User]: User 객체 리스트
    """
    with get_db() as session:
        return (
            session.query(User)
            .order_by(User.id.desc())
            .limit(limit)
            .all()
        )
