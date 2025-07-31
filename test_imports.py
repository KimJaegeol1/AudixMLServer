#!/usr/bin/env python3
"""
Import 테스트 스크립트
"""

import traceback

def test_imports():
    """각 모듈을 단계별로 테스트"""
    
    print("🧪 Import 테스트 시작...")
    
    # 1. ML pipeline config 테스트
    try:
        from ml.pipeline import config
        print("✅ config 모듈 import 성공")
    except Exception as e:
        print(f"❌ config 모듈 import 실패: {e}")
        traceback.print_exc()
        return False
    
    # 2. ML pipeline model 모듈 테스트
    try:
        from ml.pipeline import model
        print("✅ model 모듈 import 성공")
    except Exception as e:
        print(f"❌ model 모듈 import 실패: {e}")
        traceback.print_exc()
        return False
    
    # 3. audio_service 테스트
    try:
        from ml.services.audio_service import get_audio_service
        print("✅ audio_service import 성공")
    except Exception as e:
        print(f"❌ audio_service import 실패: {e}")
        traceback.print_exc()
        return False
    
    # 4. service __init__ 테스트
    try:
        from service import get_audio_service
        print("✅ service import 성공")
    except Exception as e:
        print(f"❌ service import 실패: {e}")
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    success = test_imports()
    if success:
        print("\n🎉 모든 import 테스트 통과!")
    else:
        print("\n💥 import 테스트 실패")
