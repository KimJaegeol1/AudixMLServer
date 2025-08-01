"""
Service 패키지
비즈니스 로직과 서비스 클래스들을 관리합니다.

사용 가능한 서비스들:
- ML 서비스는 ml.services 패키지에서 관리
"""

def get_audio_service():
    """오디오 서비스 인스턴스를 반환합니다."""
    try:
        # 모델 파일 존재 확인 로그
        import os
        demucs_path = "ml/models/demucs/6a76e118.th"
        onnx_path = "ml/models/onnx"
        
        print(f"🔍 모델 파일 확인:")
        print(f"   Demucs 모델: {demucs_path} -> {'✅' if os.path.exists(demucs_path) else '❌'}")
        print(f"   ONNX 모델: {onnx_path} -> {'✅' if os.path.exists(onnx_path) else '❌'}")
        
        from ml.services import get_audio_service as _get_audio_service
        service = _get_audio_service()
        print("✅ ML 서비스 로드 성공")
        return service
    except ImportError as e:
        print(f"⚠️ ML 서비스 로드 실패: {e}")
        print("💡 모델 파일이 없거나 의존성 문제일 수 있습니다.")
        # ML 모델이 없어도 기본 구조는 제공
        return None
    except Exception as e:
        print(f"⚠️ ML 서비스 초기화 실패: {e}")
        return None

# 패키지에서 외부로 노출할 것들
__all__ = [
    "get_audio_service"
]
