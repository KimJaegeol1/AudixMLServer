# Python 3.9 slim 이미지 사용 (더 가벼움)
FROM python:3.9-slim

# 작업 디렉토리 설정
WORKDIR /app

# 시스템 패키지 업데이트 및 필수 도구 설치
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libsndfile1 \
    ffmpeg \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Python 패키지 의존성 파일 복사
COPY requirements.txt .

# Python 패키지 설치
RUN pip install --no-cache-dir -r requirements.txt

# Demucs와 Dora 패키지를 Git에서 직접 설치 (최신 버전)
RUN pip install git+https://github.com/facebookresearch/demucs.git --no-deps && \
    pip install git+https://github.com/facebookresearch/dora.git --no-deps

# 애플리케이션 코드 복사
COPY . .

# ML 모델 파일들이 제대로 복사되었는지 확인
RUN echo "🔍 Checking ML model files..." && \
    ls -la ml/models/ && \
    ls -la ml/models/demucs/ && \
    ls -la ml/models/onnx/ && \
    echo "✅ Model files verification complete"

# 포트 8000 노출
EXPOSE 8000

# 환경변수 설정
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# 애플리케이션 실행
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
