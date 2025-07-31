"""
서버 관련 라우터
기본 정보, 헬스체크 등 서버 운영에 필요한 엔드포인트들
"""
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

from service import get_audio_service

# 라우터 생성
router = APIRouter(
    prefix="/server",
    tags=["Server Management"]
)

# Pydantic 모델
class HealthResponse(BaseModel):
    """헬스체크 응답 모델"""
    status: str
    demucs_model: str
    onnx_models_path: str
    onnx_models_available: bool
    timestamp: str


@router.get("/info", summary="API 정보")
async def get_server_info():
    """API 서버 정보를 반환합니다."""
    return {
        "message": "오디오 이상 감지 API",
        "version": "1.0.0",
        "service": "Audix ML Server",
        "endpoints": {
            "health": "/health",
            "server_info": "/server/info",
            "parts": "/developer/parts",
            "analyze": "/developer/device/analyze",
            "batch_analyze": "/analyze/batch",
            "docs": "/docs"
        }
    }


@router.get("/health", response_model=HealthResponse, summary="헬스체크")
async def health_check():
    """서비스 상태를 확인합니다."""
    service = get_audio_service()
    health_status = service.get_health_status()
    return health_status
