# """
# 인증 미들웨어 구현
# """
# from typing import Optional
# from fastapi import Request, HTTPException
# from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
# from starlette.middleware.base import BaseHTTPMiddleware
# from core.util.log_util import logger
# from .auth_service import AuthService
#
# security = HTTPBearer()
#
# class FirebaseAuthMiddleware(BaseHTTPMiddleware):
#     """
#     Firebase 인증 미들웨어
#     모든 요청에 대해 Firebase ID 토큰을 검증합니다.
#     """
#     def __init__(self, app, auth_service: AuthService):
#         super().__init__(app)
#         self.auth_service = auth_service
#         # 인증이 필요없는 경로 목록
#         self.public_paths = {
#             "/",
#             "/api/auth/sign-in",
#             "/api/auth/sign-up",
#             "/docs",
#             "/openapi.json"
#         }
#
#     async def dispatch(self, request: Request, call_next):
#         """
#         요청 처리 및 인증 검증
#
#         Args:
#             request: FastAPI 요청 객체
#             call_next: 다음 미들웨어 호출 함수
#
#         Returns:
#             처리된 응답
#
#         Raises:
#             HTTPException: 인증 실패 시
#         """
#         if request.url.path in self.public_paths:
#             return await call_next(request)
#
#         try:
#             credentials: Optional[HTTPAuthorizationCredentials] = await security(request)
#             if not credentials:
#                 raise HTTPException(status_code=403, detail="No credentials provided")
#
#             token = credentials.credentials
#             user = await self.auth_service.verify_id_token(token)
#
#             # 검증된 사용자 정보를 요청 상태에 저장
#             request.state.user = user
#
#             return await call_next(request)
#
#         except HTTPException as he:
#             raise he
#         except Exception as e:
#             logger.e(f"Authentication failed: {str(e)}")
#             raise HTTPException(
#                 status_code=403,
#                 detail="Invalid authentication credentials"
#             )
