# 🎵 Audix ML Server

FastAPI 기반의 기계 부품 오디오 이상 감지 ML 서버입니다.

## 📋 개요

Audix ML Server는 기계 부품(팬, 펌프, 슬라이더, 기어박스, 베어링)의 오디오 신호를 분석하여 이상 상태를 감지하는 머신러닝 서비스입니다.

### 🏗️ 시스템 구성

```
🌐 Frontend (React)
    ↕️
🚀 App Server (NestJS) :3000
    ↕️
🤖 ML Server (FastAPI) :8000  ← 이 프로젝트
    ↕️
📊 Redis :6379
```

## 🚀 빠른 시작

### 1. 전체 시스템 실행

```bash
# 네트워크 생성
docker network create app-network

# Redis 서버 실행
docker run -d --name redis-server --network app-network -p 6379:6379 redis:7.2.5-alpine3.20

# App Server 실행 (NestJS)
docker run -d --name nestjs-app --network app-network -p 3000:3000 audix-app-server

# ML Server 빌드 & 실행
docker build -t audix-ml-server .
docker run -d --name audix-ml-server --network app-network -p 8000:8000 audix-ml-server
```

### 2. API 접근

- **ML Server API**: http://localhost:8000
- **API 문서 (Swagger)**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 📁 프로젝트 구조

```
ml-server/
├── main.py                 # FastAPI 메인 애플리케이션
├── routes/                 # API 라우터
│   ├── server.py          # 서버 관리 API
│   └── developer.py       # 개발자 도구 API
├── service/               # 비즈니스 로직
│   ├── redis_config.py    # Redis 연결 설정
│   └── device_redis_repository.py
├── ml/                    # ML 관련 모든 코드
│   ├── models/           # 모델 파일들 (.th, .onnx)
│   ├── pipeline/         # ML 파이프라인 코드
│   └── services/         # ML 서비스 클래스
├── test_wav/             # 테스트용 오디오 파일
├── Dockerfile            # Docker 설정
├── requirements.txt      # Python 의존성
└── .env                  # 환경 변수
```

## 🔧 주요 API 엔드포인트

### 서버 관리
- `GET /server/health` - 헬스체크
- `GET /server/info` - 서버 정보

### 개발자 도구
- `GET /developer/parts` - 분석 가능한 부품 목록
- `POST /developer/device/analyze` - 오디오 파일 분석
- `POST /developer/batch/analyze` - 배치 분석

## 📊 사용 예시

### 단일 파일 분석

```bash
curl -X POST "http://localhost:8000/developer/device/analyze" \
  -F "file=@test_wav/mixture.wav" \
  -F "target_parts=fan,pump" \
  -F "device_id=1001"
```

### 응답 예시

```json
{
  "status": "success",
  "analysis_results": {
    "device_name": "device_1001",
    "total_parts": 2,
    "normal_score": 0.847,
    "results": [
      {
        "part_name": "fan",
        "anomaly_probability": 0.123,
        "status": "normal"
      },
      {
        "part_name": "pump", 
        "anomaly_probability": 0.089,
        "status": "normal"
      }
    ]
  }
}
```

## 🤖 ML 파이프라인

1. **오디오 전처리**: WAV 파일 로드 및 정규화
2. **소스 분리**: Demucs 모델로 각 부품별 신호 분리
3. **특징 추출**: 멜 스펙트로그램 생성
4. **이상 감지**: ONNX ResNet18 모델로 각 부품 분석
5. **결과 통합**: normalScore 계산 및 Redis 업데이트

## 🗄️ Redis 연동

분석 결과는 자동으로 Redis에 저장됩니다:

```python
# Redis 키 패턴: device:{device_id}
{
  "deviceId": "1001",
  "normalScore": "0.847",  # 0~1 사이 값 (높을수록 정상)
  "status": "active"
}
```

## 🐳 Docker 환경

### 환경 변수 (.env)

```env
# Redis 설정
REDIS_HOST=redis-server
REDIS_PORT=6379
REDIS_DB=0

# 서버 설정  
SERVER_HOST=0.0.0.0
SERVER_PORT=8000
```

### 컨테이너 관리

```bash
# 로그 확인
docker logs -f audix-ml-server

# 컨테이너 재시작
docker restart audix-ml-server

# 컨테이너 중지
docker stop audix-ml-server
```

## 📋 분석 가능한 부품

- **fan**: 팬 모터
- **pump**: 펌프
- **slider**: 슬라이더
- **gearbox**: 기어박스  
- **bearing**: 베어링

## 🔬 개발 & 테스트

### 로컬 개발 환경

```bash
# 가상환경 생성
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt

# 서버 실행 (Redis 연결 필요)
python main.py
```

### 테스트

```bash
# API 테스트
python test_client.py

# 헬스체크
curl http://localhost:8000/server/health
```

## 📝 라이센스

이 프로젝트는 MIT 라이센스 하에 배포됩니다.

## 🤝 기여

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

**Made with ❤️ for Audix Project**