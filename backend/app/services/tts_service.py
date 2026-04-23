import time
import uuid
from pathlib import Path

import httpx

from ..config import settings


class TTSService:
    def __init__(self) -> None:
        self._voices_cache: list[dict] | None = None
        self._cache_time: float = 0

    async def get_voices(self) -> list[dict]:
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

    async def generate_speech(
        self, text: str, voice_id: str
    ) -> dict:
        voice_name = None
        voices = await self.get_voices()
        for v in voices:
            if v["voice_id"] == voice_id:
                voice_name = v["name"]
                break

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

        clip_id = str(uuid.uuid4())[:12]
        filename = f"{clip_id}.mp3"
        filepath = Path(settings.audio_files_dir) / filename
        filepath.write_bytes(resp.content)

        return {
            "id": clip_id,
            "label": text,
            "voice_id": voice_id,
            "voice_name": voice_name,
            "file_path": filename,
            "pinned": False,
        }


tts_service = TTSService()
