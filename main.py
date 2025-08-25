from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.requests import Request
from fastapi.responses import JSONResponse

from app.bagtionary.app import bagtionary_router
from app.trifin.app import trifin_router
from core.common.middleware.logger_middleware import LoggerMiddleware
from core.db.mongo import mongo
from core.util.logger import get_logger
from version import __version__

logger = get_logger("Tricorn Server")
logger.debug("start app")


def create_app() -> FastAPI:
    # FastAPI 앱 생성
    app = FastAPI(
        version=__version__,
        title="Tricorn Integrated API",
        description="Tricorn Integrated API for several services",
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
    app.add_middleware(LoggerMiddleware)

    # Firebase 인증 미들웨어 설정
    # auth_service = AuthService()
    # app.add_middleware(FirebaseAuthMiddleware, auth_service=auth_service)

    # 라우터 설정
    # app.include_router(auth_router)
    app.include_router(bagtionary_router)
    app.include_router(trifin_router)

    return app


app = create_app()


@app.get("/", tags=["Common"])
async def root():
    """
    루트 엔드포인트: 기본 HTML 페이지 반환
    Returns:
        HTMLResponse: 간단한 환영 메시지를 담은 HTML 페이지
    Example:
        curl http://localhost:8000/
    """
    from fastapi.responses import HTMLResponse

    html_content = """
    <!DOCTYPE html>
    <html lang=\"ko\">
    <head>
        <meta charset=\"UTF-8\">
        <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">
        <title>Tricorn API</title>
        <style>
            body { font-family: 'Segoe UI', Arial, sans-serif; background: #f9f9f9; margin: 0; padding: 0; }
            .container { max-width: 600px; margin: 80px auto; background: #fff; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.07); padding: 40px; text-align: center; }
            h1 { color: #2d3a4b; }
            p { color: #4a5568; }
            .version { margin-top: 24px; color: #888; font-size: 0.95em; }
        </style>
    </head>
    <body>
        <div class=\"container\">
            <h1>Tricorn API 서버에 오신 것을 환영합니다!</h1>
            <p>이 서버는 여러 서비스를 통합 제공하는 API입니다.<br>API 문서는 <a href=\"/docs\">/docs</a>에서 확인할 수 있습니다.</p>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content, status_code=200)


@app.get("/ping", summary="Health Check", tags=["Common"])
def ping():
    """서버 정상동작 확인용 엔드포인트"""
    return {"message": "pong"}


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """예상치 못한 에러에 대한 전역 핸들러"""
    # TODO: 운영환경에서는 로깅 및 보안 강화 필요
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": f"서버 내부 오류: {str(exc)}"},
    )


@app.on_event("startup")
async def startup_event():
    mongo.connect()


@app.on_event("shutdown")
def shutdown_event():
    mongo.close()
    # with open("log.txt", mode="a") as log:
    #     log.write("Application shutdown")
