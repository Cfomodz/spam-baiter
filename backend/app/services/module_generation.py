"""Batch-generate a module's clips via ElevenLabs TTS.

Generation runs as a background task: the module is created immediately,
clips are appended one line at a time (sequential, to stay within
ElevenLabs concurrency limits), and progress is broadcast over the
websocket as "module_generation" messages.
"""

import asyncio
import uuid
from pathlib import Path

from sqlalchemy import select

from ..config import settings
from ..database import async_session
from ..models import BaitModule, ModuleClip
from ..ws.handler import manager
from .module_templates import TemplateLine
from .tts_service import tts_service

UPLOADS_SUBDIR = "modules"

# Keep strong references so background tasks aren't garbage-collected.
_tasks: set[asyncio.Task] = set()  # type: ignore[type-arg]


def start_generation(module_id: int, voice_id: str, lines: list[TemplateLine]) -> None:
    task = asyncio.create_task(_generate(module_id, voice_id, lines))
    _tasks.add(task)
    task.add_done_callback(_tasks.discard)


async def _broadcast(module_id: int, payload: dict) -> None:
    await manager.broadcast(
        {"type": "module_generation", "payload": {"module_id": module_id, **payload}}
    )


async def _module_exists(module_id: int) -> bool:
    async with async_session() as session:
        result = await session.execute(
            select(BaitModule.id).where(BaitModule.id == module_id)
        )
        return result.scalar() is not None


async def _generate(
    module_id: int, voice_id: str, lines: list[TemplateLine]
) -> None:
    total = len(lines)
    done = 0
    failed: list[str] = []

    uploads_dir = Path(settings.audio_files_dir) / UPLOADS_SUBDIR
    uploads_dir.mkdir(parents=True, exist_ok=True)

    # Stable positions per kind, assigned upfront so failures leave gaps
    # rather than reordering later lines.
    positions: dict[int, int] = {}
    counters = {"script": 0, "filler": 0}
    for i, line in enumerate(lines):
        positions[i] = counters[line.kind]
        counters[line.kind] += 1

    for i, line in enumerate(lines):
        # The user may delete the module mid-generation; stop quietly.
        if not await _module_exists(module_id):
            return

        try:
            audio = await tts_service.synthesize(line.text, voice_id)
        except Exception as exc:
            failed.append(line.label)
            await _broadcast(
                module_id,
                {
                    "status": "running",
                    "done": done,
                    "total": total,
                    "failed": len(failed),
                    "current": line.label,
                    "error": str(exc),
                },
            )
            continue

        filename = f"{uuid.uuid4().hex[:12]}.mp3"
        (uploads_dir / filename).write_bytes(audio)

        async with async_session() as session:
            session.add(
                ModuleClip(
                    module_id=module_id,
                    kind=line.kind,
                    label=line.label,
                    file_path=f"/audio/{UPLOADS_SUBDIR}/{filename}",
                    tier=line.tier,
                    expected_duration=line.expected_duration,
                    position=positions[i],
                )
            )
            await session.commit()

        done += 1
        await _broadcast(
            module_id,
            {
                "status": "running",
                "done": done,
                "total": total,
                "failed": len(failed),
                "current": line.label,
            },
        )

    await _broadcast(
        module_id,
        {
            "status": "complete",
            "done": done,
            "total": total,
            "failed": len(failed),
            "failed_labels": failed,
        },
    )
