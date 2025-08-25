"""
account_repository.py

Account 모델을 이용한 계좌 데이터의 삽입, 조회 기능 제공

- 의존성: SQLAlchemy
- 사용법:
    from repository.account_repository import insert_account, get_account_by_id, get_accounts_by_user_id
- 버전: 1.0.0
- 작성일: 2025-06-07
- 작성자: 사용자 요청 기반

참고: 트랜잭션/세션 관리는 외부에서 주입
"""

from typing import List, Optional

from sqlalchemy.exc import SQLAlchemyError

from app.trifin.data.repository.models.account_table import Account
from core.config.db import get_db
from core.util.log_util import logger


def insert_account(account_obj: Account) -> Account:
    """
    단일 Account 객체를 DB에 저장합니다.
    Args:
        account_obj (Account): 저장할 Account 객체
    Returns:
        Account: 저장된 Account 객체
    Raises:
        SQLAlchemyError: DB 삽입 중 오류 발생 시
    예시:
        >>> account = Account(user_id=1, name='주식계좌', balance=100000.0)
        >>> insert_account(account)
    """
    with get_db() as session:
        try:
            session.add(account_obj)
            session.commit()
            session.refresh(account_obj)
            logger.info(f"Account 데이터 저장 성공: {account_obj}")
            return account_obj
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"Account 데이터 저장 실패: {e}")
            raise


def get_account_by_id(account_id: int) -> Optional[Account]:
    """
    ID로 단일 계좌(Account) 데이터를 조회합니다.
    Args:
        account_id (int): Account ID
    Returns:
        Optional[Account]: Account 객체 또는 None
    """
    with get_db() as session:
        return session.query(Account).filter(Account.id == account_id).first()


def get_accounts_by_user_id(user_id: int, limit: int = 100) -> List[Account]:
    """
    특정 유저의 계좌 목록을 조회합니다.
    Args:
        user_id (int): 유저 ID
        limit (int): 최대 반환 개수
    Returns:
        List[Account]: Account 객체 리스트
    """
    with get_db() as session:
        return (
            session.query(Account)
            .filter(Account.user_id == user_id)
            .order_by(Account.id.desc())
            .limit(limit)
            .all()
        )
