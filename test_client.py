"""
FastAPI 오디오 분석 서버 테스트 클라이언트
"""

import requests
import json

def test_api():
    """API 서버를 테스트합니다."""
    
    base_url = "http://localhost:8000"
    
    print("🧪 API 서버 테스트 시작")
    print("="*50)
    
    # 1. 헬스체크
    print("1. 헬스체크 테스트")
    try:
        response = requests.get(f"{base_url}/server/health")
        if response.status_code == 200:
            health_data = response.json()
            print(f"✅ 서버 상태: {health_data['status']}")
            print(f"🤖 Demucs 모델: {health_data['demucs_model']}")
            print(f"📁 ONNX 모델 경로: {health_data['onnx_models_path']}")
        else:
            print(f"❌ 헬스체크 실패: {response.status_code}")
    except Exception as e:
        print(f"❌ 헬스체크 오류: {e}")
    
    print()
    
    # 2. 사용 가능한 부품 목록 확인
    print("2. 사용 가능한 부품 목록")
    try:
        response = requests.get(f"{base_url}/developer/parts")
        if response.status_code == 200:
            parts_data = response.json()
            print(f"✅ 사용 가능한 부품: {parts_data['available_parts']}")
            print(f"📊 총 부품 수: {parts_data['total_count']}")
        else:
            print(f"❌ 부품 목록 조회 실패: {response.status_code}")
    except Exception as e:
        print(f"❌ 부품 목록 조회 오류: {e}")
    
    print()
    
    # 3. 파일 분석 테스트 (test_wav/mixture.wav 파일이 있다고 가정)
    print("3. 오디오 파일 분석 테스트")
    test_file_path = "test_wav/mixture.wav"
    
    try:
        with open(test_file_path, 'rb') as f:
            files = {'file': ('mixture.wav', f, 'audio/wav')}
            data = {
                'target_parts': 'fan,pump',
                'device_id': 1001
            }
            
            print(f"📁 테스트 파일: {test_file_path}")
            print("🔄 분석 요청 중...")
            
            response = requests.post(f"{base_url}/developer/device/analyze", files=files, data=data)
            
            if response.status_code == 200:
                result = response.json()
                print("✅ 분석 완료!")
                print(f"📊 상태: {result['status']}")
                
                if result['status'] == 'success':
                    analysis = result['analysis_results']
                    print(f"🏭 장치: {analysis['device_name']}")
                    print(f"📋 분석 부품 수: {analysis['total_parts']}")
                    print(f"⚠️ 이상 감지 부품: {analysis['anomaly_count']}")
                    
                    print("\n📋 상세 결과:")
                    for res in analysis['results']:
                        status = "🚨 이상" if res['anomaly_detected'] else "✅ 정상"
                        print(f"  {res['part_name']}: {status} (확률: {res['anomaly_probability']:.3f})")
                else:
                    print(f"❌ 분석 실패: {result.get('error_message', 'Unknown error')}")
            else:
                print(f"❌ 분석 요청 실패: {response.status_code}")
                print(f"오류 메시지: {response.text}")
                
    except FileNotFoundError:
        print(f"❌ 테스트 파일을 찾을 수 없습니다: {test_file_path}")
        print("💡 test_wav/mixture.wav 파일이 있는지 확인해주세요.")
    except Exception as e:
        print(f"❌ 분석 테스트 오류: {e}")
    
    print("\n🎉 테스트 완료!")
    print("💡 브라우저에서 http://localhost:8000/docs 를 열어 API 문서를 확인하세요.")


if __name__ == "__main__":
    test_api()
