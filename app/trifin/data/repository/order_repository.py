"""
order_repository.py

Order 모델을 이용한 주문 데이터의 삽입, 조회 기능 제공

- 의존성: SQLAlchemy
- 사용법:
    from repository.order_repository import insert_order, get_order_by_id, get_orders_by_account_id, get_orders_by_user_id
- 버전: 1.0.0
- 작성일: 2025-06-07
- 작성자: 사용자 요청 기반

참고: 트랜잭션/세션 관리는 외부에서 주입
"""

from typing import List, Optional

from sqlalchemy.exc import SQLAlchemyError

from app.trifin.data.repository.models.account_table import Account
from app.trifin.data.repository.models.order_table import Order
from core.config.db import get_db
from core.util.log_util import logger


def insert_order(order_obj: Order) -> Order:
    """
    단일 Order 객체를 DB에 저장합니다.
    Args:
        order_obj (Order): 저장할 Order 객체
    Returns:
        Order: 저장된 Order 객체
    Raises:
        SQLAlchemyError: DB 삽입 중 오류 발생 시
    예시:
        >>> order = Order(type=OrderType.buy, symbol='AAPL', account_id=1, date=datetime.utcnow(), size=10, price=100.0)
        >>> insert_order(order)
    """
    with get_db() as session:
        try:
            session.add(order_obj)
            session.commit()
            session.refresh(order_obj)
            logger.info(f"Order 데이터 저장 성공: {order_obj}")
            return order_obj
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"Order 데이터 저장 실패: {e}")
            raise


def get_order_by_id(order_id: int) -> Optional[Order]:
    """
    ID로 단일 주문(Order) 데이터를 조회합니다.
    Args:
        order_id (int): Order ID
    Returns:
        Optional[Order]: Order 객체 또는 None
    """
    with get_db() as session:
        return session.query(Order).filter(Order.id == order_id).first()


def get_orders_by_account_id(account_id: int, limit: int = 100) -> List[Order]:
    """
    특정 계좌의 주문(Order) 목록을 조회합니다.
    Args:
        account_id (int): 계좌 ID
        limit (int): 최대 반환 개수
    Returns:
        List[Order]: Order 객체 리스트
    """
    with get_db() as session:
        return (
            session.query(Order)
            .filter(Order.account_id == account_id)
            .order_by(Order.date.desc())
            .limit(limit)
            .all()
        )


def get_orders_by_user_id(user_id: int, limit: int = 100) -> List[Order]:
    """
    특정 유저가 소유한 모든 계좌의 주문(Order) 목록을 조회합니다.
    Args:
        user_id (int): 유저 ID
        limit (int): 최대 반환 개수
    Returns:
        List[Order]: Order 객체 리스트
    """
    with get_db() as session:
        return (
            session.query(Order)
            .join(Account, Order.account_id == Account.id)
            .filter(Account.user_id == user_id)
            .order_by(Order.date.desc())
            .limit(limit)
            .all()
        )
