"""
user_table.py

유저(User) 테이블에 대응하는 SQLAlchemy ORM 모델 파일.

- 의존성: SQLAlchemy
- 용도: 사용자 정보 저장 및 ORM 매핑
- 사용법:
    from user_table import User
- 버전: 1.0.0
- 작성일: 2025-06-07
- 작성자: 사용자 요청 기반
- 변경이력:
    - v1.0.0: 최초 작성

"""

from sqlalchemy import Column, BigInteger, String

from app.trifin.data.repository.models.base import Base


class User(Base):
    """
    User(유저) 테이블에 대응하는 SQLAlchemy ORM 모델 클래스.

    Attributes:
        id (int): 고유 식별자, 기본키, 자동 증가
        name (str): 사용자 이름

    예시:
        >>> user = User(uid='gdhong', name='홍길동')
    """
    __tablename__ = "user"
    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="고유 식별자")
    uid = Column(String(64), unique=True, nullable=False, comment="외부 시스템 연동용 유저 식별자")
    name = Column(String(50), nullable=False, comment="사용자 이름")

    def __repr__(self) -> str:
        """
        User 객체의 문자열 표현 반환.
        """
        return f"<User(id={self.id}, uid={self.uid}, name={self.name})>"
