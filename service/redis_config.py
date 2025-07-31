"""
Redis 연결 설정
"""
import os
import redis
from typing import Optional
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# Redis 설정 (.env 파일에서 읽기)
REDIS_HOST = os.getenv("REDIS_HOST", "redis-server")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
REDIS_DB = int(os.getenv("REDIS_DB", "0"))

# Redis 클라이언트 인스턴스
_redis_client: Optional[redis.Redis] = None

def get_redis_client() -> redis.Redis:
    """Redis 클라이언트를 반환합니다."""
    global _redis_client
    
    if _redis_client is None:
        try:
            _redis_client = redis.Redis(
                host=REDIS_HOST,
                port=REDIS_PORT,
                db=REDIS_DB,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5
            )
            # 연결 테스트
            _redis_client.ping()
            print(f"✅ Redis 연결 성공: {REDIS_HOST}:{REDIS_PORT}")
        except Exception as e:
            print(f"⚠️ Redis 연결 실패: {e}")
            print("💡 Redis 없이 계속 진행합니다.")
            _redis_client = None
    
    return _redis_client

def is_redis_available() -> bool:
    """Redis가 사용 가능한지 확인합니다."""
    try:
        client = get_redis_client()
        return client is not None and client.ping()
    except:
        return False
