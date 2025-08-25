"""
price_repository.py

Price 모델을 이용한 가격 데이터의 삽입, 삭제, 검색 기능 제공

- 의존성: SQLAlchemy
- 사용법:
    from repository.price_repository import insert_price, get_price_by_id, get_prices_by_symbol, delete_price_by_id
- 버전: 1.0.0
- 작성일: 2025-05-17
- 작성자: 사용자 요청 기반
- 변경이력:
    - v1.0.0: 최초 작성

참고: 트랜잭션/세션 관리는 외부에서 주입
"""

import logging
from typing import List, Optional

from sqlalchemy.exc import SQLAlchemyError

from src.config.db import get_db
from src.repository.models.price_table import Price

logger = logging.getLogger(__name__)


def insert_prices_bulk(price_objs: List[Price]) -> int:
    """
    여러 Price 객체를 bulk로 DB에 저장합니다. (세션 자동 관리)
    중복(unique key) 발생 시 에러가 발생할 수 있습니다.

    Args:
        price_objs (List[Price]): 저장할 Price 객체 리스트

    Returns:
        int: 저장된 row 개수

    Raises:
        SQLAlchemyError: DB 삽입 중 오류 발생 시

    예시:
        >>> prices = [Price(...), Price(...)]
        >>> insert_prices_bulk(prices)
    """
    with get_db() as session:
        try:
            session.bulk_save_objects(price_objs)
            session.commit()
            logger.info(f"Price {len(price_objs)}건 bulk 저장 성공")
            return len(price_objs)
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"Price bulk 저장 실패: {e}")
            raise


def insert_prices_ignore_bulk(price_objs: List[Price]) -> int:
    """
    중복(symbol+timestamp) 데이터는 무시하고 신규만 저장하는 MySQL 전용 bulk insert 함수입니다.
    (이미 존재하는 데이터는 insert하지 않고, 신규 데이터만 저장)

    Args:
        price_objs (List[Price]): 저장할 Price 객체 리스트

    Returns:
        int: 시도한 row 개수(실제 저장된 row는 DB에서 중복을 제외한 수)

    Raises:
        SQLAlchemyError: DB 삽입 중 오류 발생 시

    예시:
        >>> prices = [Price(...), Price(...)]
        >>> insert_prices_ignore_bulk(prices)

    참고:
        - MySQL에서만 동작 (prefix_with("IGNORE") 사용)
        - id(auto increment)는 제외하고 insert
    """
    from sqlalchemy.dialects.mysql import insert as mysql_insert
    from sqlalchemy import inspect

    values = [
        {c.name: getattr(obj, c.name) for c in inspect(Price).columns if c.name != "id"}
        for obj in price_objs
    ]
    with get_db() as session:
        try:
            stmt = mysql_insert(Price).values(values).prefix_with("IGNORE")
            session.execute(stmt)
            session.commit()
            logger.info(
                f"Price {len(price_objs)}건 중 중복 제외 신규만 bulk 저장 시도 완료"
            )
            return len(price_objs)
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"Price IGNORE bulk 저장 실패: {e}")
            raise


def insert_price(price_obj: Price) -> Price:
    """
    가격 데이터(Price 객체)를 DB에 삽입합니다. (세션 자동 관리)

    Args:
        price_obj (Price): 저장할 Price 객체

    Returns:
        Price: 저장된 Price 객체

    Raises:
        SQLAlchemyError: DB 삽입 중 오류 발생 시

    예시:
        >>> price = Price(symbol='SPY', open=100, high=110, low=95, close=105, volume=12345, timestamp=datetime.utcnow())
        >>> insert_price(price)
    """
    with get_db() as session:
        try:
            session.add(price_obj)
            session.commit()
            session.refresh(price_obj)
            logger.info(f"Price 데이터 저장 성공: {price_obj}")
            return price_obj
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"Price 데이터 저장 실패: {e}")
            raise


def get_price_by_id(price_id: int) -> Optional[Price]:
    """
    ID로 단일 가격 데이터를 조회합니다. (세션 자동 관리)

    Args:
        price_id (int): Price ID

    Returns:
        Optional[Price]: Price 객체 또는 None
    """
    with get_db() as session:
        return session.query(Price).filter(Price.id == price_id).first()


def get_prices_by_symbol(symbol: str, limit: int = 100) -> List[Price]:
    """
    특정 종목(symbol)의 가격 데이터 목록을 조회합니다.

    Args:
        symbol (str): 종목명(예: 'SPY')
        limit (int): 최대 반환 개수

    Returns:
        List[Price]: Price 객체 리스트
    """

    with get_db() as session:
        return (
            session.query(Price)
            .filter(Price.symbol == symbol)
            .order_by(Price.timestamp.desc())
            .limit(limit)
            .all()
        )


def delete_price_by_id(price_id: int) -> bool:
    """
    ID로 가격 데이터를 삭제합니다.

    Args:
        price_id (int): Price ID

    Returns:
        bool: 삭제 성공 여부
    """
    with get_db() as session:
        try:
            obj = session.query(Price).filter(Price.id == price_id).first()
            if obj is None:
                logger.warning(f"삭제 대상 Price 없음: id={price_id}")
                return False
            session.delete(obj)
            session.commit()
            logger.info(f"Price 데이터 삭제 성공: id={price_id}")
            return True
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"Price 데이터 삭제 실패: {e}")
            raise


# TODO: 기간/날짜별 조회, 복합 조건 검색, upsert 등 확장
# 단위 테스트 예시 (pytest 등에서 활용):
# def test_insert_and_get_price(session):
#     price = Price(symbol='SPY', open=1, high=2, low=0.5, close=1.5, volume=100, timestamp=datetime.utcnow())
#     inserted = insert_price(session, price)
#     assert inserted.id is not None
#     loaded = get_price_by_id(session, inserted.id)
#     assert loaded is not None
#     assert loaded.symbol == 'SPY'
