# Alembic 마이그레이션 환경

이 디렉토리는 Alembic 기반 DB 마이그레이션 스크립트와 환경설정을 담습니다.

- alembic.ini: 최상위에 위치, Alembic 전체 설정 파일
- env.py: Alembic 환경설정, DB URL 및 metadata 관리
- versions/: 실제 migration 스크립트 저장 위치

초기 세팅 및 사용법은 아래와 같습니다.

1. 초기 셋팅
   - pip install alembic
   - alembic init {name}
2. 리비전 생성
   - alembic revision --autogenerate -m "message"
3. 실행
   - alembic upgrade head
 