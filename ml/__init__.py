"""
ML Package
기계학습 모델과 오디오 처리 파이프라인을 제공합니다.

주요 모듈:
- pipeline: 오디오 처리 및 분석 파이프라인
- services: 서비스 레이어 (API와 ML 연결)
- models: 학습된 모델 파일들 저장
"""

# 편의를 위해 주요 기능들을 상위 패키지에서 바로 접근 가능하도록 노출
from .services import get_audio_service

__all__ = [
    "get_audio_service",
]
