from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware

from app.bagtionary.common.middleware.verify_middleware import VerifyMiddleware
from app.bagtionary.domain.home.home_router import home_router
from app.bagtionary.domain.product.product_router import product_router
from core.util.logger import get_logger
from version import __version__

logger = get_logger()
logger.debug("start app")


def create_app() -> FastAPI:
    # FastAPI 앱 생성
    app = FastAPI(
        version=__version__,
        title="Tricorn Integrated API",
        description="Tricorn Integrated API for several services"
    )

    # CORS 설정
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # TODO: 프로덕션에서는 실제 도메인으로 제한
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # 미들웨어 설정
    app.add_middleware(VerifyMiddleware)

    # Firebase 인증 미들웨어 설정
    # auth_service = AuthService()
    # app.add_middleware(FirebaseAuthMiddleware, auth_service=auth_service)

    # 라우터 설정
    # app.include_router(auth_router)

    return app


bagtionary_router = APIRouter(prefix="/bagtionary", tags=["bagtionary"])

bagtionary_router.include_router(product_router)
bagtionary_router.include_router(home_router)
