"""
profit_repository.py

Profit 모델을 이용한 수익률 데이터의 삽입, 조회 기능 제공

- 의존성: SQLAlchemy
- 사용법:
    from repository.profit_repository import insert_profit, get_profit_by_id, get_profits_by_user_id, get_profits_by_account_id
- 버전: 1.0.0
- 작성일: 2025-06-07
- 작성자: 사용자 요청 기반

참고: 트랜잭션/세션 관리는 외부에서 주입
"""

import logging
from typing import List, Optional

from sqlalchemy.exc import SQLAlchemyError

from app.trifin.data.repository.models.profit_table import Profit
from core.config.db import get_db

logger = logging.getLogger(__name__)


def insert_profit(profit_obj: Profit) -> Profit:
    """
    단일 Profit 객체를 DB에 저장합니다.
    Args:
        profit_obj (Profit): 저장할 Profit 객체
    Returns:
        Profit: 저장된 Profit 객체
    Raises:
        SQLAlchemyError: DB 삽입 중 오류 발생 시
    예시:
        >>> profit = Profit(user_id=1, account_id=1, profit=0.15)
        >>> insert_profit(profit)
    """
    with get_db() as session:
        try:
            session.add(profit_obj)
            session.commit()
            session.refresh(profit_obj)
            logger.info(f"Profit 데이터 저장 성공: {profit_obj}")
            return profit_obj
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"Profit 데이터 저장 실패: {e}")
            raise


def get_profit_by_id(profit_id: int) -> Optional[Profit]:
    """
    ID로 단일 수익률(Profit) 데이터를 조회합니다.
    Args:
        profit_id (int): Profit ID
    Returns:
        Optional[Profit]: Profit 객체 또는 None
    """
    with get_db() as session:
        return session.query(Profit).filter(Profit.id == profit_id).first()


def get_profits_by_user_id(user_id: int, limit: int = 100) -> List[Profit]:
    """
    특정 유저의 수익률(Profit) 목록을 조회합니다.
    Args:
        user_id (int): 유저 ID
        limit (int): 최대 반환 개수
    Returns:
        List[Profit]: Profit 객체 리스트
    """
    with get_db() as session:
        return (
            session.query(Profit)
            .filter(Profit.user_id == user_id)
            .order_by(Profit.id.desc())
            .limit(limit)
            .all()
        )


def get_profits_by_account_id(account_id: int, limit: int = 100) -> List[Profit]:
    """
    특정 계좌의 수익률(Profit) 목록을 조회합니다.
    Args:
        account_id (int): 계좌 ID
        limit (int): 최대 반환 개수
    Returns:
        List[Profit]: Profit 객체 리스트
    """
    with get_db() as session:
        return (
            session.query(Profit)
            .filter(Profit.account_id == account_id)
            .order_by(Profit.id.desc())
            .limit(limit)
            .all()
        )
