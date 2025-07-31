"""
Device Redis Repository - 간단한 normalScore 업데이트만 처리
"""
from .redis_config import get_redis_client

def update_device_normal_score(device_id: int, normal_score: float) -> None:
    """Redis에 기기의 normalScore만 업데이트합니다."""
    redis_client = get_redis_client()
    
    if not redis_client:
        print("⚠️ Redis 연결이 없어 normalScore 업데이트를 건너뜁니다.")
        return
    
    try:
        device_key = f"device:{device_id}"
        redis_client.hset(device_key, "normalScore", str(normal_score))
        print(f"✅ Redis 업데이트: device:{device_id}, normalScore: {normal_score:.3f}")
    except Exception as e:
        print(f"⚠️ Redis normalScore 업데이트 실패: {e}")
