# 🚀 FastAPI 오디오 분석 서버 사용법

## 📁 새로운 프로젝트 구조

```
project/
├── ml_models/              # ML 관련 코드들
│   ├── __init__.py
│   ├── audio_preprocessing.py
│   ├── config.py
│   ├── denoise.py
│   ├── integrated_analysis.py
│   ├── main.py
│   ├── mel.py
│   ├── model.py
│   ├── onnx.py
│   ├── resample.py
│   ├── rms_normalize.py
│   └── seperate_evaluate.py
├── main.py                 # FastAPI 메인 애플리케이션
├── routes/                # API 라우터들
│   ├── server.py          # 서버 관리 엔드포인트
│   └── developer.py       # 개발자 도구 엔드포인트
├── service/               # 비즈니스 로직 서비스들
│   └── audio_service.py   # ML 서비스 클래스
├── test_client.py          # 테스트 클라이언트
├── requirements.txt        # 패키지 의존성
├── model/                  # Demucs 모델 파일들
├── ResNet18_onnx/         # ONNX 모델 파일들
└── test_wav/              # 테스트 오디오 파일들
```

## 🎯 주요 변경사항

- **모듈화**: ML 관련 코드를 `ml_models` 패키지로 분리
- **API화**: FastAPI를 통한 REST API 제공
- **서비스화**: `AudioAnalysisService` 클래스로 ML 로직 캡슐화
- **확장성**: 여러 클라이언트가 동시에 사용 가능

## 🚀 서버 실행

```bash
# 서버 시작
python main.py

# 또는 uvicorn 직접 실행
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

서버 시작 후 다음 URL들을 사용할 수 있습니다:
- **API 문서**: http://localhost:8000/docs
- **헬스체크**: http://localhost:8000/health
- **부품 목록**: http://localhost:8000/parts

## 📡 API 엔드포인트

### 1. 헬스체크
```http
GET /health
```

**응답 예시:**
```json
{
  "status": "healthy",
  "demucs_model": "ready",
  "onnx_models_path": "ResNet18_onnx",
  "onnx_models_available": true,
  "timestamp": "2025-07-31 18:45:00"
}
```

### 2. 사용 가능한 부품 목록
```http
GET /parts
```

**응답 예시:**
```json
{
  "available_parts": ["fan", "pump", "slider", "gearbox", "bearing"],
  "total_count": 5
}
```

### 3. 오디오 파일 분석
```http
POST /analyze
```

**요청 파라미터:**
- `file`: WAV 파일 (multipart/form-data)
- `target_parts`: 분석할 부품들 (콤마로 구분, 예: "fan,pump")
- `device_id`: 장치 ID (숫자)

**응답 예시:**
```json
{
  "status": "success",
  "pipeline_info": {
    "input_wav_file": "/tmp/temp_file.wav",
    "original_filename": "mixture.wav",
    "target_parts": ["fan", "pump"],
    "generated_pt_files": ["output/2025-07-31_18-45-00_mic_1_fan.pt", "..."],
    "timestamp": "2025-07-31 18:45:00"
  },
  "analysis_results": {
    "device_name": "device_1001",
    "total_parts": 2,
    "anomaly_count": 1,
    "normal_score": 0.629,
    "results": [
      {
        "part_name": "fan",
        "anomaly_detected": true,
        "anomaly_probability": 0.942
      },
      {
        "part_name": "pump",
        "anomaly_detected": false,
        "anomaly_probability": 0.234
      }
    ]
  }
}
```

### 4. 배치 분석 (여러 파일)
```http
POST /analyze/batch
```

**요청 파라미터:**
- `files`: 여러 WAV 파일들 (최대 10개)
- `device_id`: 장치 ID

## 🧪 테스트 방법

### 1. 테스트 클라이언트 실행
```bash
python test_client.py
```

### 2. curl을 이용한 테스트
```bash
# 헬스체크
curl http://localhost:8000/health

# 부품 목록 조회
curl http://localhost:8000/parts

# 파일 분석
curl -X POST "http://localhost:8000/developer/device/analyze" \
  -F "file=@test_wav/mixture.wav" \
  -F "target_parts=fan,pump" \
  -F "device_id=1001"
```

### 3. Python requests를 이용한 테스트
```python
import requests

# 파일 분석
with open('test_wav/mixture.wav', 'rb') as f:
    files = {'file': ('mixture.wav', f, 'audio/wav')}
    data = {
        'target_parts': 'fan,pump',
        'device_id': 1001
    }
    
    response = requests.post('http://localhost:8000/developer/device/analyze', 
                           files=files, data=data)
    result = response.json()
    print(result)
```

## 🔧 개발 모드

개발 중에는 `--reload` 옵션으로 서버를 실행하면 코드 변경 시 자동으로 서버가 재시작됩니다:

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

## 📊 성능 및 제한사항

- **동시 처리**: FastAPI의 비동기 처리로 여러 요청 동시 처리 가능
- **파일 크기**: 대용량 파일 업로드 시 timeout 설정 필요
- **메모리**: ML 모델이 메모리에 로드되므로 충분한 메모리 필요
- **배치 제한**: 배치 처리는 최대 10개 파일로 제한

## 🚀 배포 방법

### 1. 로컬 배포
```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

### 2. Docker 배포 (선택사항)
```dockerfile
FROM python:3.9

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 3. 프로덕션 배포
```bash
# Gunicorn 사용
pip install gunicorn
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

## 🛡️ 보안 고려사항

- **CORS**: 실제 운영환경에서는 특정 도메인만 허용하도록 설정
- **파일 검증**: 업로드되는 파일의 형식과 크기 검증
- **인증**: 필요시 JWT 토큰 기반 인증 추가
- **HTTPS**: 프로덕션에서는 HTTPS 사용 권장

---

이제 ML 모델이 독립된 패키지로 분리되어 있고, FastAPI를 통해 깔끔한 REST API로 제공됩니다! 🎉
