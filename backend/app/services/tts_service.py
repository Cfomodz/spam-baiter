import time
import uuid
from pathlib import Path

import httpx

from ..config import settings


class TTSNotConfiguredError(Exception):
    """Raised when no ElevenLabs API key is configured."""


class TTSService:
    def __init__(self) -> None:
        self._voices_cache: list[dict] | None = None
        self._cache_time: float = 0

    def _require_api_key(self) -> None:
        if not settings.elevenlabs_api_key:
            raise TTSNotConfiguredError(
                "ElevenLabs TTS is not configured. "
                "Set ELEVENLABS_API_KEY in your .env to enable TTS."
            )

    async def get_voices(self) -> list[dict]:
        self._require_api_key()
        if self._voices_cache and (time.time() - self._cache_time) < 300:
            return self._voices_cache

        async with httpx.AsyncClient() as client:
            resp = await client.get(
                "https://api.elevenlabs.io/v1/voices",
                headers={"xi-api-key": settings.elevenlabs_api_key},
                timeout=30,
            )
            resp.raise_for_status()
            data = resp.json()

        self._voices_cache = [
            {
                "voice_id": v["voice_id"],
                "name": v["name"],
                "preview_url": v.get("preview_url"),
            }
            for v in data.get("voices", [])
        ]
        self._cache_time = time.time()
        return self._voices_cache

    async def synthesize(self, text: str, voice_id: str) -> bytes:
        """Generate speech audio (mp3 bytes) for a single line of text."""
        self._require_api_key()
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}",
                headers={
                    "xi-api-key": settings.elevenlabs_api_key,
                    "Content-Type": "application/json",
                    "Accept": "audio/mpeg",
                },
                json={
                    "text": text,
                    "model_id": "eleven_monolingual_v1",
                },
                timeout=60,
            )
            resp.raise_for_status()
        return resp.content

    async def get_voice_name(self, voice_id: str) -> str | None:
        """Best-effort voice name lookup; never raises."""
        try:
            for v in await self.get_voices():
                if v["voice_id"] == voice_id:
                    return v["name"]
        except Exception:
            pass
        return None

    async def generate_speech(
        self, text: str, voice_id: str
    ) -> dict:
        self._require_api_key()
        voice_name = await self.get_voice_name(voice_id)
        content = await self.synthesize(text, voice_id)

        clip_id = str(uuid.uuid4())[:12]
        filename = f"{clip_id}.mp3"
        filepath = Path(settings.audio_files_dir) / filename
        filepath.write_bytes(content)

        return {
            "id": clip_id,
            "label": text,
            "voice_id": voice_id,
            "voice_name": voice_name,
            "file_path": filename,
            "pinned": False,
        }


tts_service = TTSService()
