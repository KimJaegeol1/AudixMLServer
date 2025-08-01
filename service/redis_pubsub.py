"""
Redis Pub/Sub 기능
normalScore가 임계값 이하일 때 알림 메시지를 발행합니다.
"""
import json
from .redis_config import get_redis_client

# Pub/Sub 설정
ALERT_CHANNEL = "device_alerts"
NORMAL_SCORE_THRESHOLD = 0.5

def publish_low_normal_score_alert(device_id: int, normal_score: float) -> bool:
    """
    normalScore가 임계값 이하일 때 알림을 발행합니다.
    
    Args:
        device_id: 장치 ID
        normal_score: 정상도 점수 (0~1)
    
    Returns:
        bool: 발행 성공 여부
    """
    redis_client = get_redis_client()
    
    if not redis_client:
        print("⚠️ Redis 연결이 없어 Pub/Sub 알림을 건너뜁니다.")
        return False
    
    # 임계값 확인
    if normal_score > NORMAL_SCORE_THRESHOLD:
        return True  # 정상 범위이므로 알림 필요 없음
    
    try:
        # 알림 메시지 생성
        alert_message = {
            "deviceId": device_id,
            "normalScore": normal_score
        }
        
        # JSON으로 직렬화하여 발행
        message_json = json.dumps(alert_message)
        redis_client.publish(ALERT_CHANNEL, message_json)
        
        print(f"🚨 Pub/Sub 알림 발행: device {device_id}, normalScore: {normal_score:.3f}")
        return True
        
    except Exception as e:
        print(f"⚠️ Pub/Sub 알림 발행 실패: {e}")
        return False
