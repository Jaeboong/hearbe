"""
AI_next 서버 메인 진입점

MCP WebSocket 연결 + ASR + TTS + OCR
(LLM/NLU/Flow 제거 — 새 커맨드 생성 로직은 별도 구현)
"""

import asyncio
import logging
import signal
import sys
import uuid
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware

from core.config import get_config, setup_logging
from core.event_bus import event_bus, EventType, publish

from services.asr import ASRService
from services.tts import TTSService
from services.ocr import OCRService
from services.session import SessionManager
from services.nlu import IntentClassifier
from services.sites import SiteManager
from services.intent_router import IntentRouter

from api.websocket import WebSocketHandler, connection_manager

logger = logging.getLogger(__name__)


class AIServer:
    """AI 서버 애플리케이션 (경량 버전)"""

    def __init__(self):
        self.config = get_config()
        setup_logging(self.config)

        self.asr_service: ASRService = None
        self.tts_service: TTSService = None
        self.ocr_service: OCRService = None
        self.session_manager: SessionManager = None
        self.classifier: IntentClassifier = None
        self.site_manager: SiteManager = None
        self.intent_router: IntentRouter = None

        self.ws_handler: WebSocketHandler = None
        self.app: FastAPI = None

        logger.info("AIServer instance created")

    async def initialize_services(self):
        """모든 서비스 초기화"""
        logger.info("Initializing services...")

        self.session_manager = SessionManager()
        self.asr_service = ASRService()
        self.tts_service = TTSService()
        self.ocr_service = OCRService()

        await self.session_manager.initialize()

        try:
            await self.asr_service.initialize()
        except Exception as e:
            logger.warning(f"ASR service initialization skipped: {e}")

        try:
            await self.tts_service.initialize()
        except Exception as e:
            logger.warning(f"TTS service initialization skipped: {e}")

        try:
            await self.ocr_service.initialize()
        except Exception as e:
            logger.warning(f"OCR service initialization skipped: {e}")

        # NLU + SiteManager + IntentRouter
        self.site_manager = SiteManager()
        self.classifier = IntentClassifier()
        try:
            await self.classifier.initialize()
            self.intent_router = IntentRouter(self.classifier, self.site_manager)
            logger.info("IntentRouter initialized (sites: %s)", self.site_manager.list_sites())
        except Exception as e:
            logger.warning(f"IntentRouter initialization failed: {e}")
            self.intent_router = None

        self.ws_handler = WebSocketHandler(
            asr_service=self.asr_service,
            tts_service=self.tts_service,
            session_manager=self.session_manager,
            intent_router=self.intent_router,
        )

        logger.info("All services initialized")

    async def shutdown_services(self):
        """모든 서비스 종료"""
        logger.info("Shutting down services...")

        if self.asr_service:
            await self.asr_service.shutdown()
        if self.tts_service:
            await self.tts_service.shutdown()
        if self.ocr_service:
            await self.ocr_service.shutdown()
        if self.session_manager:
            await self.session_manager.shutdown()

        logger.info("All services shut down")

    def create_app(self) -> FastAPI:
        """FastAPI 앱 생성"""

        @asynccontextmanager
        async def lifespan(app: FastAPI):
            await event_bus.start()
            await self.initialize_services()

            app.state.asr_service = self.asr_service
            app.state.tts_service = self.tts_service
            app.state.ocr_service = self.ocr_service

            await publish(EventType.SERVER_STARTED, source="main")
            logger.info("AI Server started")

            yield

            await publish(EventType.SERVER_SHUTDOWN, source="main")
            await self.shutdown_services()
            await event_bus.stop()
            logger.info("AI Server stopped")

        self.app = FastAPI(
            title="AI_next Server",
            description="MCP WebSocket + ASR + TTS + OCR",
            version="2.0.0",
            lifespan=lifespan,
            debug=self.config.server.debug,
        )

        origins = [
            origin.strip()
            for origin in self.config.server.cors_origins.split(",")
            if origin.strip()
        ] or ["*"]
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        @self.app.websocket("/ws")
        async def websocket_endpoint(websocket: WebSocket):
            session_id = websocket.query_params.get("session_id", str(uuid.uuid4()))
            await self.ws_handler.handle_connection(websocket, session_id)

        @self.app.websocket("/ws/{session_id}")
        async def websocket_endpoint_with_session(websocket: WebSocket, session_id: str):
            await self.ws_handler.handle_connection(websocket, session_id)

        @self.app.get("/")
        async def root():
            ws_url = self.config.server.public_ws_url
            if not ws_url:
                base_url = self.config.server.public_base_url
                if base_url:
                    if base_url.startswith("https://"):
                        ws_url = "wss://" + base_url[len("https://"):]
                    elif base_url.startswith("http://"):
                        ws_url = "ws://" + base_url[len("http://"):]
                    else:
                        ws_url = base_url
                    ws_url = ws_url.rstrip("/") + self.config.server.ws_path
                else:
                    ws_url = f"ws://localhost:{self.config.server.port}{self.config.server.ws_path}"
            return {
                "name": "AI_next Server",
                "version": "2.0.0",
                "status": "running",
                "websocket": ws_url,
            }

        return self.app

    def run(self):
        """서버 실행"""
        app = self.create_app()

        def signal_handler(sig, frame):
            logger.info(f"Received signal {sig}, shutting down...")
            sys.exit(0)

        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

        uvicorn.run(
            app,
            host=self.config.server.host,
            port=self.config.server.port,
            log_level="info" if not self.config.server.debug else "debug",
        )


def main():
    server = AIServer()
    server.run()


_server = AIServer()
app = _server.create_app()


if __name__ == "__main__":
    main()
