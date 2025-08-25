"""
main.py - FastAPI 애플리케이션 엔트리포인트

- 목적: FastAPI 기반 백엔드 서버 실행
- 의존성: fastapi, uvicorn
- 실행 예시: uvicorn python.src.main:app --reload
- 엔드포인트:
    - GET /ping: 서버 헬스체크
    - 기타 엔드포인트는 필요에 따라 확장
- 에러 핸들링: 전역 예외 처리 포함
- 보안: production 환경에서는 CORS, 인증 등 추가 필요

작성일: 2025-06-03
버전: 1.0.0
변경이력: 최초 작성
"""

from fastapi import APIRouter

from app.trifin.domain.account.account_router import account_router
from app.trifin.domain.order.order_router import order_router
from app.trifin.domain.profit.profit_router import profit_router
from app.trifin.domain.user.user_router import user_router

trifin_router = APIRouter(prefix="/trifin", tags=["trifin"])

trifin_router.include_router(user_router)
trifin_router.include_router(account_router)
trifin_router.include_router(order_router)
trifin_router.include_router(profit_router)
