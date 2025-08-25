# """
# 사용자 인증 관련 모델 정의
# """
# from typing import Optional
# from pydantic import BaseModel, EmailStr
#
# class UserProfile(BaseModel):
#     """사용자 프로필 정보"""
#     uid: str
#     email: str
#     display_name: Optional[str] = None
#     photo_url: Optional[str] = None
#
# class SignInRequest(BaseModel):
#     """로그인 요청 모델"""
#     id_token: str
#
# class SignInResponse(BaseModel):
#     """로그인 응답 모델"""
#     access_token: str
#     user: UserProfile
#
# class UserCreateRequest(BaseModel):
#     """사용자 생성 요청 모델"""
#     email: EmailStr
#     password: str
#     display_name: Optional[str] = None
