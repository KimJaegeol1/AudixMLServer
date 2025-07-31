"""
FastAPI 오디오 분석 서버 - 메인 애플리케이션
WAV 파일을 업로드하여 기계 부품의 이상 감지를 수행하는 API 서버입니다.
"""

import os
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# .env 파일 로드
load_dotenv()

# 라우터들 import
from routes import server_router, developer_router
from service import get_audio_service

# FastAPI 앱 생성
app = FastAPI(
    title="Audix ML 오디오 이상 감지 API",
    description="WAV 파일을 업로드하여 기계 부품의 이상 감지를 수행합니다.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS 미들웨어 추가
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 실제 운영환경에서는 특정 도메인만 허용
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터들 등록
app.include_router(server_router)
app.include_router(developer_router)


@app.on_event("startup")
async def startup_event():
    """서버 시작 시 모델 초기화"""
    print("🚀 Audix ML FastAPI 서버 시작")
    print("🔧 오디오 분석 서비스 초기화 중...")
    
    # Redis 연결 확인
    try:
        from service.redis_config import is_redis_available
        if is_redis_available():
            print("✅ Redis 연결 확인됨")
        else:
            print("⚠️ Redis 연결 안됨 (선택사항)")
    except Exception as e:
        print(f"⚠️ Redis 확인 중 오류: {e}")
    
    try:
        # 서비스 초기화 (모델 로딩)
        service = get_audio_service()
        print("✅ 서버 초기화 완료")
        print("📋 등록된 라우터:")
        print("  - /server/* : 서버 관리 엔드포인트")
        print("  - /developer/* : 개발자 도구 엔드포인트")
    except Exception as e:
        print(f"❌ 서버 초기화 실패: {e}")
        raise


@app.get("/", summary="API 루트")
async def root():
    """API 루트 엔드포인트"""
    return {
        "message": "Audix ML 오디오 이상 감지 API",
        "version": "1.0.0",
        "status": "running",
        "routes": {
            "server_management": "/server/*",
            "developer_tools": "/developer/*",
            "api_docs": "/docs",
            "redoc": "/redoc"
        },
        "quick_links": {
            "health_check": "/server/health",
            "server_info": "/server/info", 
            "available_parts": "/developer/parts",
            "analyze_audio": "/developer/device/analyze"
        }
    }


if __name__ == "__main__":
    import uvicorn
    
    # .env에서 서버 설정 읽기
    host = os.getenv("SERVER_HOST", "0.0.0.0")
    port = int(os.getenv("SERVER_PORT", "8000"))
    env = os.getenv("ENV", "development")
    
    print("🚀 Audix ML FastAPI 오디오 분석 서버 시작")
    print(f"🌍 환경: {env}")
    print(f"� 서버: {host}:{port}")
    print("�📋 사용법:")
    print(f"  - API 문서: http://localhost:{port}/docs")
    print(f"  - 대체 문서: http://localhost:{port}/redoc")
    print(f"  - 헬스체크: http://localhost:{port}/server/health")
    print(f"  - 서버 정보: http://localhost:{port}/server/info")
    print(f"  - 부품 목록: http://localhost:{port}/developer/parts")
    print(f"  - 오디오 분석: http://localhost:{port}/developer/device/analyze")
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=(env == "development"),  # 개발 모드에서만 리로드
        log_level="info"
    )
