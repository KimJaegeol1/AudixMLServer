"""
ML 모델 서비스 클래스
오디오 분석 파이프라인을 캡슐화하여 API에서 쉽게 사용할 수 있도록 합니다.
"""

import os
import sys
import json
from datetime import datetime
from typing import List, Dict, Optional

# src 패키지의 모듈들을 import
from src.audio_preprocessing import process_wav_file, load_model
from src.resample import init_resampler
from src.integrated_analysis import process_pt_files_with_classification


class AudioAnalysisService:
    """오디오 분석 서비스 클래스"""
    
    def __init__(self, onnx_model_base_path: str = "models/onnx"):
        """
        서비스 초기화
        
        Args:
            onnx_model_base_path: ONNX 모델들이 저장된 폴더 경로
        """
        self.onnx_model_base_path = onnx_model_base_path
        self.model = None
        self.source_names = None
        self._initialize_models()
    
    def _initialize_models(self):
        """Demucs 모델을 초기화합니다."""
        try:
            print("🔧 Demucs 모델 로딩 중...")
            self.model, self.source_names = load_model()
            init_resampler(self.model.samplerate)
            print("✅ Demucs 모델 로딩 완료")
        except Exception as e:
            print(f"❌ 모델 로딩 실패: {e}")
            raise
    
    def analyze_audio_file(
        self, 
        wav_file_path: str, 
        target_parts: List[str] = None,
        device_name: str = "machine_001"
    ) -> Dict:
        """
        WAV 파일을 분석하여 이상 감지 결과를 반환합니다.
        
        Args:
            wav_file_path: 입력 WAV 파일 경로
            target_parts: 분석할 부품 리스트
            device_name: 장치명
        
        Returns:
            dict: 분석 결과
        """
        if target_parts is None:
            target_parts = ["fan", "pump", "slider", "gearbox", "bearing"]
        
        try:
            print(f"🚀 오디오 분석 시작: {wav_file_path}")
            print(f"🎯 대상 부품: {target_parts}")
            
            # === 1단계: .pt 파일 생성 ===
            print("📋 1단계: WAV 파일에서 .pt 파일 생성")
            generated_files = process_wav_file(
                self.model, 
                self.source_names, 
                wav_file_path, 
                target_parts=target_parts
            )
            
            if not generated_files:
                raise ValueError("❌ .pt 파일이 생성되지 않았습니다.")
            
            print(f"✅ 1단계 완료: {len(generated_files)}개 .pt 파일 생성")
            
            # === 2단계: .pt 파일 분석 ===
            print("📋 2단계: 각 부품별 전용 ONNX 모델로 분류 분석")
            analysis_results = process_pt_files_with_classification(
                pt_files=generated_files,
                onnx_model_base_path=self.onnx_model_base_path,
                device_name=device_name
            )
            
            print(f"✅ 2단계 완료: {analysis_results['total_parts']}개 부품 분석")
            
            # === 최종 결과 통합 ===
            final_result = {
                "status": "success",
                "pipeline_info": {
                    "input_wav_file": wav_file_path,
                    "target_parts": target_parts,
                    "generated_pt_files": generated_files,
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                },
                "analysis_results": analysis_results,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            return final_result
            
        except Exception as e:
            print(f"❌ 분석 실행 중 오류 발생: {e}")
            return {
                "status": "error",
                "error_message": str(e),
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
    
    def get_health_status(self) -> Dict:
        """서비스 상태를 확인합니다."""
        try:
            model_status = "ready" if self.model is not None else "not_loaded"
            onnx_models_exist = os.path.exists(self.onnx_model_base_path)
            
            return {
                "status": "healthy",
                "demucs_model": model_status,
                "onnx_models_path": self.onnx_model_base_path,
                "onnx_models_available": onnx_models_exist,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
    
    def get_available_parts(self) -> List[str]:
        """분석 가능한 부품 목록을 반환합니다."""
        return ["fan", "pump", "slider", "gearbox", "bearing"]
    
    def save_result_to_file(self, result: Dict, output_filename: Optional[str] = None) -> str:
        """결과를 JSON 파일로 저장합니다."""
        if output_filename is None:
            device_name = result.get("analysis_results", {}).get("device_name", "unknown")
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename = f"api_result_{device_name}_{timestamp}.json"
        
        with open(output_filename, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        print(f"💾 결과가 {output_filename}에 저장되었습니다.")
        return output_filename


# 전역 서비스 인스턴스
audio_service = None

def get_audio_service() -> AudioAnalysisService:
    """전역 오디오 분석 서비스 인스턴스를 반환합니다."""
    global audio_service
    if audio_service is None:
        audio_service = AudioAnalysisService()
    return audio_service
