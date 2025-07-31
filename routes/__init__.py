"""
Routes 패키지
FastAPI 라우터들을 모듈별로 관리합니다.

사용 가능한 라우터들:
- server: 서버 관리 관련 엔드포인트
- developer: 개발자 도구 관련 엔드포인트
"""

from .server import router as server_router
from .developer import router as developer_router

# 패키지에서 외부로 노출할 것들
__all__ = [
    "server_router",
    "developer_router"
]
