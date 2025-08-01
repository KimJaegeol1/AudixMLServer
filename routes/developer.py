"""
개발자용 라우터
오디오 분석, 부품 목록 등 개발/테스트에 필요한 엔드포인트들
"""
import os
import tempfile
import shutil
from typing import List, Optional
from datetime import datetime

from fastapi import APIRouter, File, UploadFile, HTTPException, Form, BackgroundTasks
from fastapi.responses import FileResponse
from pydantic import BaseModel

from service import get_audio_service
from service.device_redis_repository import update_device_normal_score
from service.redis_pubsub import publish_low_normal_score_alert

# 라우터 생성
router = APIRouter(
    prefix="/developer", 
    tags=["Developer Tools"]
)

# Pydantic 모델
class AnalysisResponse(BaseModel):
    """분석 응답 모델"""
    status: str
    pipeline_info: Optional[dict] = None
    analysis_results: Optional[dict] = None
    error_message: Optional[str] = None
    timestamp: str


@router.get("/parts", summary="분석 가능한 부품 목록")
async def get_available_parts():
    """분석 가능한 부품 목록을 반환합니다."""
    service = get_audio_service()
    parts = service.get_available_parts()
    return {
        "available_parts": parts,
        "total_count": len(parts),
        "description": "현재 시스템에서 분석 가능한 기계 부품들의 목록입니다."
    }


@router.post("/device/analyze", response_model=AnalysisResponse, summary="오디오 파일 분석")
async def analyze_audio(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(..., description="분석할 WAV 파일"),
    target_parts: Optional[str] = Form(None, description="분석할 부품들 (콤마로 구분, 예: fan,pump,slider)"),
    device_id: int = Form(..., description="장치 ID")
):
    """
    WAV 파일을 업로드하여 이상 감지 분석을 수행합니다.
    
    - **file**: 분석할 WAV 파일 (10초, 44.1kHz, mono 권장)
    - **target_parts**: 분석할 부품들 (콤마로 구분, 빈 값이면 모든 부품 분석)
    - **device_id**: 장치 ID (숫자)

    normalScore가 0.5 미만인 경우 Redis Pub/Sub으로 알림이 발행됩니다.
    """
    
    # 파일 형식 확인
    if not file.filename.lower().endswith('.wav'):
        raise HTTPException(status_code=400, detail="WAV 파일만 업로드 가능합니다.")
    
    # target_parts 파싱
    parsed_target_parts = None
    if target_parts:
        parsed_target_parts = [part.strip() for part in target_parts.split(',')]
    
    # 임시 파일로 저장
    temp_file_path = None
    try:
        # 임시 파일 생성
        with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_file:
            temp_file_path = temp_file.name
            # 업로드된 파일을 임시 파일에 복사
            shutil.copyfileobj(file.file, temp_file)
        
        print(f"📁 임시 파일 생성: {temp_file_path}")
        print(f"📊 파일 크기: {os.path.getsize(temp_file_path)} bytes")
        
        # 오디오 분석 서비스 호출
        service = get_audio_service()
        result = service.analyze_audio_file(
            wav_file_path=temp_file_path,
            target_parts=parsed_target_parts,
            device_name=f"device_{device_id}"
        )
        
        # 원본 파일명 정보 추가
        result["pipeline_info"]["original_filename"] = file.filename
        
        # normalScore 계산 및 Redis 업데이트
        if result["status"] == "success":
            analysis_results = result["analysis_results"]
            total_parts = analysis_results["total_parts"]
            
            # 각 부품의 이상 확률을 가중 평균으로 계산 (1/n 가중치)
            total_anomaly_score = 0.0
            for part_result in analysis_results["results"]:
                total_anomaly_score += part_result["anomaly_probability"]
            
            # normalScore: 0~1 사이 값 (이상도가 높을수록 낮은 점수)
            avg_anomaly_probability = total_anomaly_score / total_parts if total_parts > 0 else 0.0
            normal_score = 1.0 - avg_anomaly_probability  # 이상도를 정상도로 변환
            
            # Redis에 normalScore만 업데이트
            try:
                update_device_normal_score(device_id, normal_score)
                
                # 결과에 normalScore 추가 (Redis와 동일한 키명 사용)
                result["analysis_results"]["normalScore"] = normal_score
                print(f"📊 normalScore 계산: {normal_score:.3f} (평균 이상확률: {avg_anomaly_probability:.3f})")
                
                # normalScore가 0.5 이하면 Pub/Sub 알림 발행
                publish_low_normal_score_alert(device_id, normal_score)
                
            except Exception as redis_error:
                print(f"⚠️ Redis 업데이트 실패: {redis_error}")
                # Redis 실패해도 분석 결과는 반환
                result["analysis_results"]["normalScore"] = normal_score
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"분석 중 오류가 발생했습니다: {str(e)}")
    
    finally:
        # 임시 파일 정리
        if temp_file_path and os.path.exists(temp_file_path):
            try:
                os.unlink(temp_file_path)
                print(f"🗑️ 임시 파일 삭제: {temp_file_path}")
            except Exception as e:
                print(f"⚠️ 임시 파일 삭제 실패: {e}")


@router.post("/batch/analyze", summary="배치 분석 (여러 파일)")
async def analyze_batch(
    background_tasks: BackgroundTasks,
    files: List[UploadFile] = File(..., description="분석할 WAV 파일들"),
    device_id: int = Form(..., description="장치 ID")
):
    """
    여러 WAV 파일을 동시에 분석합니다.
    """
    if len(files) > 10:  # 최대 10개 파일로 제한
        raise HTTPException(status_code=400, detail="최대 10개 파일까지만 업로드 가능합니다.")
    
    batch_results = {
        "status": "success",
        "total_files": len(files),
        "results": [],
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    service = get_audio_service()
    
    for i, file in enumerate(files):
        if not file.filename.lower().endswith('.wav'):
            batch_results["results"].append({
                "filename": file.filename,
                "status": "error",
                "error_message": "WAV 파일이 아닙니다."
            })
            continue
        
        temp_file_path = None
        try:
            # 임시 파일 생성
            with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_file:
                temp_file_path = temp_file.name
                shutil.copyfileobj(file.file, temp_file)
            
            # 분석 수행
            result = service.analyze_audio_file(
                wav_file_path=temp_file_path,
                device_name=f"device_{device_id}_file_{i+1}"
            )
            
            result["pipeline_info"]["original_filename"] = file.filename
            batch_results["results"].append(result)
        
        except Exception as e:
            batch_results["results"].append({
                "filename": file.filename,
                "status": "error",
                "error_message": str(e)
            })
        
        finally:
            # 임시 파일 정리
            if temp_file_path and os.path.exists(temp_file_path):
                try:
                    os.unlink(temp_file_path)
                except Exception:
                    pass
    
    return batch_results


@router.get("/results/{filename}", summary="결과 파일 다운로드")
async def download_result_file(filename: str):
    """저장된 결과 파일을 다운로드합니다."""
    file_path = f"./{filename}"
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="파일을 찾을 수 없습니다.")
    
    return FileResponse(
        path=file_path,
        filename=filename,
        media_type='application/json'
    )
