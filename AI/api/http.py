"""
HTTP API 라우터

인증, 헬스체크, 관리 API, ASR
"""

import logging
from fastapi import FastAPI, APIRouter, HTTPException, Depends, UploadFile, File, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any

from core.config import get_config

logger = logging.getLogger(__name__)

router = APIRouter()


# ============================================================================
# Request/Response 모델
# ============================================================================

class LoginRequest(BaseModel):
    """로그인 요청"""
    username: str
    password: str


class TokenResponse(BaseModel):
    """토큰 응답"""
    access_token: str
    refresh_token: str
    token_type: str = "Bearer"
    expires_in: int = 3600


class RefreshRequest(BaseModel):
    """토큰 갱신 요청"""
    refresh_token: str


class HealthResponse(BaseModel):
    """헬스체크 응답"""
    status: str
    version: str = "1.0.0"
    services: Dict[str, str]


class TTSRequest(BaseModel):
    """TTS 요청 (HTTP용)"""
    text: str
    voice_id: Optional[str] = None


class ASRResponse(BaseModel):
    """ASR 응답"""
    text: str
    confidence: float
    language: str
    duration: float


# ============================================================================
# 인증 API
# ============================================================================

@router.post("/auth/login", response_model=TokenResponse)
async def login(request: LoginRequest):
    """
    로그인 및 토큰 발급
    """
    # TODO: 실제 인증 로직 구현
    # 현재는 테스트용 더미 토큰 반환
    logger.info(f"Login attempt: {request.username}")

    return TokenResponse(
        access_token="test_access_token",
        refresh_token="test_refresh_token"
    )


@router.post("/auth/token", response_model=TokenResponse)
async def exchange_token(code: str):
    """
    Authorization code를 access token으로 교환 (OAuth)
    """
    # TODO: OAuth code → token 교환 구현
    logger.info(f"Token exchange: code={code[:10]}...")

    return TokenResponse(
        access_token="exchanged_access_token",
        refresh_token="exchanged_refresh_token"
    )


@router.post("/auth/refresh", response_model=TokenResponse)
async def refresh_token(request: RefreshRequest):
    """
    토큰 갱신
    """
    # TODO: 실제 토큰 갱신 로직
    logger.info("Token refresh requested")

    return TokenResponse(
        access_token="refreshed_access_token",
        refresh_token="new_refresh_token"
    )


@router.get("/auth/callback")
async def oauth_callback(code: str, state: Optional[str] = None):
    """
    OAuth 콜백 (로컬 앱 리다이렉트용)
    """
    # 로컬 앱으로 리다이렉트하거나 토큰 발급
    logger.info(f"OAuth callback: code={code[:10]}...")
    return {"code": code, "state": state}


# ============================================================================
# 헬스체크 API
# ============================================================================

@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    서버 상태 확인
    """
    # TODO: 각 서비스 상태 확인
    services = {
        "asr": "ready",
        "nlu": "ready",
        "llm": "ready",
        "tts": "ready",
        "ocr": "ready",
        "flow_engine": "ready",
        "session_manager": "ready"
    }

    return HealthResponse(
        status="healthy",
        services=services
    )


@router.get("/health/asr")
async def asr_health():
    """ASR 서비스 상태"""
    # TODO: ASR 서비스 상태 확인
    return {"status": "ready", "model": "large-v3-turbo"}


@router.get("/health/tts")
async def tts_health():
    """TTS 서비스 상태"""
    config = get_config().tts
    return {"status": "ready", "provider": config.provider}


# ============================================================================
# ASR API
# ============================================================================

@router.post("/asr/transcribe", response_model=ASRResponse)
async def transcribe_audio(request: Request, file: UploadFile = File(...)):
    """
    Transcribe audio file to text.

    Accepts WAV/PCM audio (16kHz mono recommended).
    Returns transcription result with confidence score.
    """
    # Get ASR service from app state (set by main.py)
    asr_service = getattr(request.app.state, "asr_service", None)

    if asr_service is None or not asr_service.is_ready():
        raise HTTPException(status_code=503, detail="ASR service not available")

    try:
        audio_data = await file.read()
        if len(audio_data) == 0:
            raise HTTPException(status_code=400, detail="Empty audio file")

        logger.info(f"ASR request: file={file.filename}, size={len(audio_data)} bytes")

        result = await asr_service.transcribe(audio_data)

        return ASRResponse(
            text=result.text,
            confidence=result.confidence,
            language=result.language,
            duration=result.duration
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"ASR transcription failed: {e}")
        raise HTTPException(status_code=500, detail=f"Transcription failed: {str(e)}")


# ============================================================================
# 관리 API
# ============================================================================

@router.get("/sessions")
async def list_sessions():
    """
    활성 세션 목록 (관리용)
    """
    # TODO: SessionManager에서 세션 목록 조회
    return {"sessions": [], "count": 0}


@router.delete("/sessions/{session_id}")
async def delete_session(session_id: str):
    """
    세션 삭제 (관리용)
    """
    # TODO: SessionManager에서 세션 삭제
    logger.info(f"Session deleted: {session_id}")
    return {"status": "deleted", "session_id": session_id}


@router.get("/config")
async def get_server_config():
    """
    서버 설정 조회 (민감 정보 제외)
    """
    config = get_config()
    return {
        "server": {
            "host": config.server.host,
            "port": config.server.port,
            "ws_path": config.server.ws_path
        },
        "asr": {
            "model": config.asr.model_name,
            "language": config.asr.language
        },
        "tts": {
            "provider": config.tts.provider
        }
    }


# ============================================================================
# FastAPI 앱 생성
# ============================================================================

def create_app() -> FastAPI:
    """FastAPI 앱 생성"""
    config = get_config()

    app = FastAPI(
        title="AI Shopping Assistant Server",
        description="시각장애인 음성 쇼핑 지원 AI 서버",
        version="1.0.0",
        debug=config.server.debug
    )

    # CORS 설정
    origins = config.server.cors_origins.split(",")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # 라우터 등록
    app.include_router(router, prefix="/api/v1")

    @app.on_event("startup")
    async def startup_event():
        logger.info("AI Server starting up...")

    @app.on_event("shutdown")
    async def shutdown_event():
        logger.info("AI Server shutting down...")

    return app