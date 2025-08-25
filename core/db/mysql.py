import os

from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = os.getenv("MYSQL_URL")
engine = create_engine(DATABASE_URL, pool_recycle=500)

Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

naming_convention = {
    "ix": 'ix_%(column_0_label)s',
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(column_0_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}
Base.metadata = MetaData(naming_convention=naming_convention)


def get_db():
    session = Session()
    try:
        yield session
    finally:
        session.close()
