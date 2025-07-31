# Docker 빌드 및 실행 가이드

## 🐳 ML Server Docker 빌드 및 실행

### 1. ML Server 이미지 빌드
```bash
docker build -t audix-ml-server .
```

### 2. ML Server 컨테이너 실행 (기존 네트워크에 연결)
```bash
# 환경변수 직접 설정하여 실행
docker run -d --name ml-server \
  --network app-network \
  -p 8000:8000 \
  -e REDIS_HOST=redis-server \
  -e REDIS_PORT=6379 \
  -e REDIS_DB=0 \
  -e SERVER_HOST=0.0.0.0 \
  -e SERVER_PORT=8000 \
  -e ENV=production \
  audix-ml-server

# 또는 .env 파일 사용 (Docker 환경에 맞게 값 조정 필요)
docker run -d --name ml-server \
  --network app-network \
  -p 8000:8000 \
  --env-file .env \
  audix-ml-server
```

### 3. 로그 확인
```bash
# 실시간 로그 확인
docker logs -f ml-server

# 최근 로그 확인
docker logs ml-server
```

### 4. 컨테이너 상태 확인
```bash
# 실행 중인 컨테이너 확인
docker ps

# ML Server API 테스트
curl http://localhost:8000/server/health
```

### 5. 컨테이너 중지 및 제거
```bash
# 컨테이너 중지
docker stop ml-server

# 컨테이너 제거
docker rm ml-server

# 이미지 제거 (필요시)
docker rmi audix-ml-server
```

## 🔧 환경변수 설정

### .env 파일 설정
```env
# Redis 설정
# 로컬 개발: localhost, Docker: redis-server  
REDIS_HOST=redis-server
REDIS_PORT=6379
REDIS_DB=0

# 서버 설정
SERVER_HOST=0.0.0.0
SERVER_PORT=8000

# 환경 설정
ENV=development
```

| 변수명 | 기본값 | 설명 |
|--------|--------|------|
| REDIS_HOST | redis-server | Redis 서버 호스트명 |
| REDIS_PORT | 6379 | Redis 포트 |
| REDIS_DB | 0 | Redis 데이터베이스 번호 |
| SERVER_HOST | 0.0.0.0 | 서버 바인딩 주소 |
| SERVER_PORT | 8000 | 서버 포트 |
| ENV | development | 환경 (development/production) |

## 🏃 로컬 개발 실행

### 개발 환경에서 실행
```bash
# 로컬 개발을 위해 .env 파일의 REDIS_HOST를 localhost로 변경
# REDIS_HOST=localhost

# 서버 실행
python main.py
```

### Redis 연결 설정
- **로컬 개발**: `.env`에서 `REDIS_HOST=localhost`로 설정
- **Docker**: `.env`에서 `REDIS_HOST=redis-server`로 설정 (또는 환경변수로 오버라이드)

```
app-network
├── redis-server (Redis 컨테이너)
│   └── 포트: 6379
└── ml-server (ML API 서버)
    └── 포트: 8000
```

## 🧪 API 테스트

ML Server가 실행되면 다음 엔드포인트에서 테스트할 수 있습니다:

- **API 문서**: http://localhost:8000/docs
- **헬스체크**: http://localhost:8000/server/health  
- **부품 목록**: http://localhost:8000/developer/parts
- **오디오 분석**: http://localhost:8000/developer/device/analyze
