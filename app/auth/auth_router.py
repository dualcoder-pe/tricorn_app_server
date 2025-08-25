# """
# 인증 관련 API 라우터
# """
# from fastapi import APIRouter, Depends, HTTPException
# from core.util.log_util import logger
# from .auth_model import SignInRequest, SignInResponse, UserCreateRequest
# from .auth_service import AuthService
#
# auth_router = APIRouter(
#     prefix="/api/auth",
#     tags=["인증"]
# )
#
# @auth_router.post("/sign-in", response_model=SignInResponse)
# async def sign_in(
#     request: SignInRequest,
#     auth_service: AuthService = Depends(lambda: AuthService())
# ):
#     """
#     Firebase ID 토큰으로 로그인
#
#     Args:
#         request: 로그인 요청 정보
#         auth_service: 인증 서비스 인스턴스
#
#     Returns:
#         로그인 응답 정보
#
#     Raises:
#         HTTPException: 인증 실패 시
#     """
#     try:
#         user = await auth_service.verify_id_token(request.id_token)
#         # TODO: JWT 토큰 생성 로직 구현
#         access_token = "temporary_token"  # 임시 토큰
#
#         return SignInResponse(
#             access_token=access_token,
#             user=user
#         )
#     except ValueError as e:
#         logger.e(f"Sign in failed: {str(e)}")
#         raise HTTPException(
#             status_code=401,
#             detail="Invalid credentials"
#         )
