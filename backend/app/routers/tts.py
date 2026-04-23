from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException

from ..schemas import ClipOut, TTSGenerateRequest, VoiceOut
from ..services.soundboard_service import soundboard_service
from ..services.tts_service import tts_service
from ..ws.handler import manager

router = APIRouter()


@router.get("/voices", response_model=list[VoiceOut])
async def list_voices():
    voices = await tts_service.get_voices()
    return [VoiceOut(**v) for v in voices]


@router.post("/generate", response_model=ClipOut)
async def generate_speech(body: TTSGenerateRequest):
    if not body.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty")

    result = await tts_service.generate_speech(body.text, body.voice_id)

    clip = {
        **result,
        "created_at": datetime.now(timezone.utc),
        "source": "generated",
        "duration": None,
    }
    soundboard_service.add_session_clip(clip)

    await manager.broadcast(
        {
            "type": "clip_ready",
            "payload": {
                "clip_id": clip["id"],
                "label": clip["label"],
                "voice_name": clip["voice_name"],
                "pinned": False,
            },
        }
    )

    return ClipOut(**clip)
