from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db
from ..models import LegacyClip, SoundboardClip
from ..schemas import ClipOut, LegacyClipOut
from ..services.soundboard_service import soundboard_service

router = APIRouter()


@router.get("/clips", response_model=list[ClipOut])
async def list_clips(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(SoundboardClip)
        .where(SoundboardClip.pinned == True)
        .order_by(SoundboardClip.created_at.desc())
    )
    pinned = result.scalars().all()

    clips: list[ClipOut] = []
    for p in pinned:
        clips.append(
            ClipOut(
                id=str(p.id),
                label=p.label,
                voice_id=p.voice_id,
                voice_name=p.voice_name,
                file_path=p.file_path,
                pinned=True,
                created_at=p.created_at,
                source="generated",
            )
        )

    for sc in soundboard_service.get_session_clips():
        if not any(c.id == sc["id"] for c in clips):
            clips.append(
                ClipOut(
                    id=sc["id"],
                    label=sc["label"],
                    voice_id=sc["voice_id"],
                    voice_name=sc.get("voice_name"),
                    file_path=sc["file_path"],
                    pinned=False,
                    created_at=sc.get("created_at"),
                    source="generated",
                )
            )

    return clips


@router.post("/clips/{clip_id}/pin", response_model=ClipOut)
async def pin_clip(clip_id: str, db: AsyncSession = Depends(get_db)):
    clip = soundboard_service.get_session_clip(clip_id)
    if not clip:
        raise HTTPException(status_code=404, detail="Clip not found")

    db_clip = SoundboardClip(
        label=clip["label"],
        voice_id=clip["voice_id"],
        voice_name=clip.get("voice_name"),
        file_path=clip["file_path"],
        pinned=True,
    )
    db.add(db_clip)
    await db.commit()
    await db.refresh(db_clip)

    soundboard_service.remove_session_clip(clip_id)

    return ClipOut(
        id=str(db_clip.id),
        label=db_clip.label,
        voice_id=db_clip.voice_id,
        voice_name=db_clip.voice_name,
        file_path=db_clip.file_path,
        pinned=True,
        created_at=db_clip.created_at,
        source="generated",
    )


@router.post("/clips/{clip_id}/unpin", response_model=ClipOut)
async def unpin_clip(clip_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(SoundboardClip).where(SoundboardClip.id == int(clip_id))
    )
    db_clip = result.scalar_one_or_none()
    if not db_clip:
        raise HTTPException(status_code=404, detail="Clip not found")

    session_clip = {
        "id": str(db_clip.id),
        "label": db_clip.label,
        "voice_id": db_clip.voice_id,
        "voice_name": db_clip.voice_name,
        "file_path": db_clip.file_path,
        "pinned": False,
        "created_at": datetime.now(timezone.utc),
        "source": "generated",
    }
    soundboard_service.add_session_clip(session_clip)

    await db.delete(db_clip)
    await db.commit()

    return ClipOut(**session_clip)


@router.delete("/clips/{clip_id}")
async def delete_clip(clip_id: str, db: AsyncSession = Depends(get_db)):
    soundboard_service.remove_session_clip(clip_id)
    try:
        result = await db.execute(
            select(SoundboardClip).where(SoundboardClip.id == int(clip_id))
        )
        db_clip = result.scalar_one_or_none()
        if db_clip:
            await db.delete(db_clip)
            await db.commit()
    except ValueError:
        pass
    return {"ok": True}


@router.get("/legacy", response_model=list[LegacyClipOut])
async def list_legacy_clips(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(LegacyClip).order_by(LegacyClip.display_order)
    )
    return result.scalars().all()
