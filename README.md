# 🎵 Audix ML Server

**FastAPI 기반 오디오 이상 감지 분석 서버**

WAV 파일을 업로드하여 기계 부품의 이상 감지를 수행하는 REST API 서버입니다.

## 🚀 주요 기능

- **오디오 분석**: WAV 파일을 Demucs 모델로 소스 분리 후 이상 감지
- **부품별 분석**: fan, pump, slider, bearing, gearbox 5개 부품 개별 분석  
- **Redis 연동**: 분석 결과를 Redis에 자동 저장
- **Docker 지원**: 컨테이너 기반 배포 및 실행
- **실시간 API**: FastAPI 기반 비동기 처리

## 📁 프로젝트 구조

```
ml-server/
├── main.py                 # FastAPI 메인 애플리케이션
├── routes/                 # API 라우터
│   ├── server.py          # 서버 관리 엔드포인트  
│   └── developer.py       # 개발자 도구 엔드포인트
├── service/               # 비즈니스 로직
│   ├── audio_service.py   # ML 서비스 클래스
│   ├── redis_config.py    # Redis 연결 설정
│   └── device_redis_repository.py # Redis 업데이트
├── ml_models/             # ML 관련 코드
├── model/                 # Demucs 모델 파일
├── ResNet18_onnx/        # ONNX 모델 파일
├── test_wav/             # 테스트 오디오 파일
├── Dockerfile            # Docker 설정
└── requirements.txt      # Python 의존성
```

## 🎯 주요 API 엔드포인트

### 1. 헬스체크
```http
GET /server/health
```

### 2. 부품 목록 조회
```http
GET /developer/parts
```

### 3. 오디오 파일 분석 ⭐
```http
POST /developer/device/analyze
```

**요청 파라미터:**
- `file`: WAV 파일 (multipart/form-data)
- `target_parts`: 분석할 부품들 (콤마 구분, 예: "fan,pump")
- `device_id`: 장치 ID (숫자)

**응답 예시:**
```json
{
  "status": "success",
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

## 🐳 Docker 실행

### 1. 이미지 빌드
```bash
docker build -t audix-ml-server .
```

### 2. 컨테이너 실행
```bash
# Redis와 같은 네트워크에서 실행
docker run -d --name audix-ml-server --network app-network -p 8000:8000 audix-ml-server
```

### 3. 한 번에 재빌드 & 재시작
```bash
docker stop audix-ml-server; docker rm audix-ml-server; docker build -t audix-ml-server .; docker run -d --name audix-ml-server --network app-network -p 8000:8000 audix-ml-server
```

## 🔧 환경 설정

`.env` 파일에서 설정을 관리합니다:

```env
# Redis 설정
REDIS_HOST=redis-server  # Docker: redis-server, 로컬: localhost
REDIS_PORT=6379
REDIS_DB=0

# 서버 설정
SERVER_HOST=0.0.0.0
SERVER_PORT=8000
ENV=development
```

## 🧪 테스트 방법

### 1. API 문서 확인
서버 실행 후 http://localhost:8000/docs 에서 interactive API 문서 확인

### 2. curl 테스트
```bash
# 헬스체크
curl http://localhost:8000/server/health

# 파일 분석
curl -X POST "http://localhost:8000/developer/device/analyze" \
  -F "file=@test_wav/mixture.wav" \
  -F "target_parts=fan,pump" \
  -F "device_id=1001"
```

### 3. 테스트 클라이언트
```bash
python test_client.py
```

## 🔄 분석 파이프라인

```
📁 WAV 파일 업로드
    ↓
🔧 전처리 (10초, 44.1kHz, mono)
    ↓
🎵 Demucs 소스 분리 (6개 → 5개 부품)
    ↓
🖼️ Mel Spectrogram 변환
    ↓
🤖 ONNX 이상 감지 모델
    ↓
📊 normalScore 계산 & Redis 업데이트
    ↓
✅ JSON 결과 반환
```

## 📊 normalScore 계산

```python
# 각 부품의 이상 확률 평균
avg_anomaly_probability = sum(anomaly_probabilities) / total_parts

# normalScore: 높을수록 정상 (0~1)
normal_score = 1.0 - avg_anomaly_probability
```

- **높은 normalScore (0.8~1.0)**: 정상 상태
- **낮은 normalScore (0.0~0.3)**: 이상 상태

## 🚀 배포 및 운영

서버가 실행되면 다음 URL에서 접근 가능합니다:

- **API 문서**: http://localhost:8000/docs
- **헬스체크**: http://localhost:8000/server/health
- **부품 목록**: http://localhost:8000/developer/parts
- **분석 API**: http://localhost:8000/developer/device/analyze

Redis 연결이 실패해도 분석은 정상 동작하며, normalScore는 응답에 포함됩니다.

---

**🎉 이제 ML 모델이 독립된 서비스로 분리되어, 깔끔한 REST API를 통해 제공됩니다!**