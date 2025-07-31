"""
Service 패키지
비즈니스 로직과 서비스 클래스들을 관리합니다.

사용 가능한 서비스들:
- ML 서비스는 ml.services 패키지에서 관리
"""

from ml.services import get_audio_service

# 패키지에서 외부로 노출할 것들
__all__ = [
    "get_audio_service"
]
