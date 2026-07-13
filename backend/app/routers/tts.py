from datetime import datetime, timezone

import httpx
from fastapi import APIRouter, HTTPException

from ..schemas import ClipOut, TTSGenerateRequest, VoiceOut
from ..services.soundboard_service import soundboard_service
from ..services.tts_service import TTSNotConfiguredError, tts_service
from ..ws.handler import manager

router = APIRouter()


@router.get("/voices", response_model=list[VoiceOut])
async def list_voices():
    try:
        voices = await tts_service.get_voices()
    except TTSNotConfiguredError as exc:
        raise HTTPException(status_code=503, detail=str(exc))
    except httpx.HTTPStatusError as exc:
        raise HTTPException(
            status_code=502,
            detail=f"ElevenLabs API error ({exc.response.status_code})",
        )
    return [VoiceOut(**v) for v in voices]


@router.post("/generate", response_model=ClipOut)
async def generate_speech(body: TTSGenerateRequest):
    if not body.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty")

    try:
        result = await tts_service.generate_speech(body.text, body.voice_id)
    except TTSNotConfiguredError as exc:
        raise HTTPException(status_code=503, detail=str(exc))
    except httpx.HTTPStatusError as exc:
        raise HTTPException(
            status_code=502,
            detail=f"ElevenLabs API error ({exc.response.status_code})",
        )

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
