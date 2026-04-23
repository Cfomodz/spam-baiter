import os
from pathlib import Path

from sqlalchemy import select

from ..config import settings
from ..database import async_session
from ..models import LegacyClip, SoundboardClip


class SoundboardService:
    def __init__(self) -> None:
        self._session_clips: dict[str, dict] = {}

    def add_session_clip(self, clip: dict) -> None:
        self._session_clips[clip["id"]] = clip

    def get_session_clips(self) -> list[dict]:
        return list(self._session_clips.values())

    def get_session_clip(self, clip_id: str) -> dict | None:
        return self._session_clips.get(clip_id)

    def remove_session_clip(self, clip_id: str) -> None:
        self._session_clips.pop(clip_id, None)

    async def scan_legacy_clips(self) -> None:
        soundboard_dir = Path(settings.soundboard_dir)
        if not soundboard_dir.exists():
            return

        async with async_session() as session:
            result = await session.execute(select(LegacyClip.id).limit(1))
            if result.scalar() is not None:
                return

            order = 0
            for persona_dir in sorted(soundboard_dir.iterdir()):
                if not persona_dir.is_dir():
                    continue
                persona = persona_dir.name

                for wav_file in sorted(persona_dir.glob("*.wav")):
                    label = wav_file.stem
                    rel_path = str(wav_file.relative_to(soundboard_dir))
                    session.add(
                        LegacyClip(
                            persona=persona,
                            label=label,
                            file_path=rel_path,
                            category="main",
                            display_order=order,
                        )
                    )
                    order += 1

                early_dir = persona_dir / "early_question_responses"
                if early_dir.exists():
                    for tier_dir in sorted(early_dir.iterdir()):
                        if not tier_dir.is_dir():
                            continue
                        category = tier_dir.name
                        for wav_file in sorted(tier_dir.glob("*.wav")):
                            label = wav_file.stem
                            rel_path = str(wav_file.relative_to(soundboard_dir))
                            session.add(
                                LegacyClip(
                                    persona=persona,
                                    label=label,
                                    file_path=rel_path,
                                    category=category,
                                    display_order=order,
                                )
                            )
                            order += 1

            await session.commit()


soundboard_service = SoundboardService()
