"""
Alembic 환경설정 파일 (env.py)
- DB URL을 환경변수 또는 config.db에서 동적으로 주입
- models import를 통해 자동으로 테이블/메타데이터 인식
- 커스텀 마이그레이션 로직, 한글 주석 포함
"""

import os
import sys
from logging.config import fileConfig

from alembic import context
from dotenv import load_dotenv
from sqlalchemy import engine_from_config, pool

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# 모델 import (여기에 프로젝트 내 모든 Base import)
from src.repository.models.base import Base
from src.repository.models.index_table import Index
from src.repository.models.price_table import Price
from src.repository.models.user_table import User
from src.repository.models.account_table import Account
from src.repository.models.order_table import Order
from src.repository.models.profit_table import Profit

load_dotenv()

# Alembic Config 객체
config = context.config

# 로그 설정
if config.config_file_name is None:
    raise RuntimeError(
        "config_file_name이 None입니다. Alembic 설정 파일 경로를 확인하세요."
    )
fileConfig(config.config_file_name)


def get_url() -> str:
    """
    환경변수 또는 config.db에서 DB URL을 동적으로 가져옴
    Returns:
        str: DB URL
    Raises:
        RuntimeError: 환경변수에 DB_URL이 없을 때
    """
    url = os.getenv("DB_URL")
    if url is None:
        raise RuntimeError("환경변수 DB_URL이 설정되어 있지 않습니다.")
    return url


# 메타데이터 집합 (여기에 모든 Base.metadata 추가)
# print("테이블 목록:", Base.metadata.tables.keys())
target_metadata = Base.metadata


def run_migrations_offline():
    """offline 모드: DB 연결 없이 SQL만 생성"""
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """online 모드: 실제 DB에 직접 적용"""
    configuration = config.get_section(config.config_ini_section)
    if configuration is None:
        raise RuntimeError("Alembic config의 section 정보를 가져올 수 없습니다.")
    configuration["sqlalchemy.url"] = get_url()
    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
