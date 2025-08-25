"""
index_repository.py

Index 모델을 이용한 경제지표 데이터의 삽입, 삭제, 검색 기능 제공

- 의존성: SQLAlchemy
- 사용법:
    from repository.index_repository import insert_indexes_bulk, insert_indexes_ignore_bulk, insert_index, get_index_by_id, get_indexes_by_symbol, delete_index_by_id
- 버전: 1.0.0
- 작성일: 2025-05-18
- 작성자: 사용자 요청 기반
- 변경이력:
    - v1.0.0: 최초 작성

참고: 트랜잭션/세션 관리는 외부에서 주입
"""

import logging
from typing import List, Optional

from sqlalchemy.exc import SQLAlchemyError
from src.config.db import get_db
from src.repository.models.index_table import Index

logger = logging.getLogger(__name__)


def insert_indexes_bulk(index_objs: List[Index]) -> int:
    """
    여러 Index 객체를 bulk로 DB에 저장합니다. (세션 자동 관리)
    중복(unique key) 발생 시 에러가 발생할 수 있습니다.

    Args:
        index_objs (List[Index]): 저장할 Index 객체 리스트

    Returns:
        int: 저장된 row 개수

    Raises:
        SQLAlchemyError: DB 삽입 중 오류 발생 시

    예시:
        >>> indexes = [Index(...), Index(...)]
        >>> insert_indexes_bulk(indexes)
    """
    with get_db() as session:
        try:
            session.bulk_save_objects(index_objs)
            session.commit()
            logger.info(f"Index {len(index_objs)}건 bulk 저장 성공")
            return len(index_objs)
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"Index bulk 저장 실패: {e}")
            raise


def insert_indexes_ignore_bulk(index_objs: List[Index]) -> int:
    """
    중복(symbol+date) 데이터는 무시하고 신규만 저장하는 MySQL 전용 bulk insert 함수입니다.
    (이미 존재하는 데이터는 insert하지 않고, 신규 데이터만 저장)

    Args:
        index_objs (List[Index]): 저장할 Index 객체 리스트

    Returns:
        int: 시도한 row 개수(실제 저장된 row는 DB에서 중복을 제외한 수)

    Raises:
        SQLAlchemyError: DB 삽입 중 오류 발생 시

    예시:
        >>> indexes = [Index(...), Index(...)]
        >>> insert_indexes_ignore_bulk(indexes)

    참고:
        - MySQL에서만 동작 (prefix_with("IGNORE") 사용)
        - id(auto increment)는 제외하고 insert
    """
    from sqlalchemy.dialects.mysql import insert as mysql_insert
    from sqlalchemy import inspect

    values = [
        {c.name: getattr(obj, c.name) for c in inspect(Index).columns if c.name != "id"}
        for obj in index_objs
    ]
    with get_db() as session:
        try:
            stmt = mysql_insert(Index).values(values).prefix_with("IGNORE")
            session.execute(stmt)
            session.commit()
            logger.info(
                f"Index {len(index_objs)}건 중 중복 제외 신규만 bulk 저장 시도 완료"
            )
            return len(index_objs)
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"Index IGNORE bulk 저장 실패: {e}")
            raise


def insert_index(index_obj: Index) -> Index:
    """
    단일 Index 객체를 DB에 저장합니다. (세션 자동 관리)

    Args:
        index_obj (Index): 저장할 Index 객체

    Returns:
        Index: 저장된 Index 객체

    Raises:
        SQLAlchemyError: DB 삽입 중 오류 발생 시

    예시:
        >>> idx = Index(symbol='DGS10', value=4.21, date=date(2024,1,1))
        >>> insert_index(idx)
    """
    with get_db() as session:
        try:
            session.add(index_obj)
            session.commit()
            session.refresh(index_obj)
            logger.info(f"Index 데이터 저장 성공: {index_obj}")
            return index_obj
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"Index 데이터 저장 실패: {e}")
            raise


def get_index_by_id(index_id: int) -> Optional[Index]:
    """
    ID로 단일 인덱스 데이터를 조회합니다. (세션 자동 관리)

    Args:
        index_id (int): Index ID

    Returns:
        Optional[Index]: Index 객체 또는 None
    """
    with get_db() as session:
        return session.query(Index).filter(Index.id == index_id).first()


def get_indexes_by_symbol(symbol: str, limit: int = 100) -> List[Index]:
    """
    특정 심볼(symbol)의 인덱스 데이터 목록을 조회합니다.

    Args:
        symbol (str): 인덱스 심볼(예: 'DGS10')
        limit (int): 최대 반환 개수

    Returns:
        List[Index]: Index 객체 리스트
    """
    with get_db() as session:
        return (
            session.query(Index)
            .filter(Index.symbol == symbol)
            .order_by(Index.date.desc())
            .limit(limit)
            .all()
        )


def delete_index_by_id(index_id: int) -> bool:
    """
    ID로 인덱스 데이터를 삭제합니다.

    Args:
        index_id (int): Index ID

    Returns:
        bool: 삭제 성공 여부
    """
    with get_db() as session:
        try:
            obj = session.query(Index).filter(Index.id == index_id).first()
            if obj is None:
                logger.warning(f"삭제 대상 Index 없음: id={index_id}")
                return False
            session.delete(obj)
            session.commit()
            logger.info(f"Index 데이터 삭제 성공: id={index_id}")
            return True
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"Index 데이터 삭제 실패: {e}")
            raise

# TODO: 기간/날짜별 조회, upsert, 복합조건 검색 등 확장 가능
# 단위 테스트 예시 (pytest 등에서 활용):
# def test_insert_and_get_index(session):
#     idx = Index(symbol='DGS10', value=4.21, date=date(2024,1,1))
#     inserted = insert_index(session, idx)
#     assert inserted.id is not None
#     loaded = get_index_by_id(session, inserted.id)
#     assert loaded is not None
#     assert loaded.symbol == 'DGS10'
