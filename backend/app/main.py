import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .config import settings
from .database import engine
from .models import Base
from .routers import audio, contacts, lines, soundboard, tts
from .services.line_manager import line_manager
from .services.soundboard_service import soundboard_service
from .ws.handler import manager


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    os.makedirs(settings.audio_files_dir, exist_ok=True)
    await soundboard_service.scan_legacy_clips()
    await line_manager.initialize()

    yield

    await line_manager.shutdown()


app = FastAPI(title="Spam Baiter Dashboard", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

audio_dir = Path(settings.audio_files_dir)
audio_dir.mkdir(parents=True, exist_ok=True)
app.mount("/audio", StaticFiles(directory=str(audio_dir)), name="audio")

soundboard_dir = Path(settings.soundboard_dir)
if soundboard_dir.exists():
    app.mount(
        "/soundboard-files",
        StaticFiles(directory=str(soundboard_dir)),
        name="soundboard-files",
    )

app.include_router(contacts.router, prefix="/api/contacts", tags=["contacts"])
app.include_router(lines.router, prefix="/api/lines", tags=["lines"])
app.include_router(tts.router, prefix="/api/tts", tags=["tts"])
app.include_router(soundboard.router, prefix="/api/soundboard", tags=["soundboard"])
app.include_router(audio.router, prefix="/api/audio", tags=["audio"])


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.handle_connection(websocket)


@app.get("/api/health")
async def health():
    return {"status": "ok"}
