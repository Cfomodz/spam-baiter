import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..config import settings
from ..database import get_db
from ..models import BaitModule, ModuleClip
from ..schemas import (
    ModuleClipOut,
    ModuleClipUpdate,
    ModuleCreate,
    ModuleGenerateOut,
    ModuleGenerateRequest,
    ModuleOut,
    ModuleReorderRequest,
    ModuleSummaryOut,
    ModuleUpdate,
    TemplateOut,
)
from ..services import module_generation
from ..services.module_templates import TEMPLATES, lines_from_module

router = APIRouter()
templates_router = APIRouter()


@templates_router.get("", response_model=list[TemplateOut])
async def list_templates():
    return [
        TemplateOut(
            key=t.key,
            name=t.name,
            description=t.description,
            script_count=sum(1 for l in t.lines if l.kind == "script"),
            filler_count=sum(1 for l in t.lines if l.kind == "filler"),
        )
        for t in TEMPLATES.values()
    ]

ALLOWED_AUDIO_EXTENSIONS = {".wav", ".mp3", ".ogg", ".m4a", ".webm"}
UPLOADS_SUBDIR = "modules"


async def _get_module(db: AsyncSession, module_id: int) -> BaitModule:
    result = await db.execute(
        select(BaitModule)
        .options(selectinload(BaitModule.clips))
        .where(BaitModule.id == module_id)
    )
    module = result.scalar_one_or_none()
    if not module:
        raise HTTPException(status_code=404, detail="Module not found")
    return module


def _uploads_dir() -> Path:
    path = Path(settings.audio_files_dir) / UPLOADS_SUBDIR
    path.mkdir(parents=True, exist_ok=True)
    return path


def _delete_uploaded_file(file_path: str) -> None:
    """Remove an uploaded clip file; never touches soundboard repo files."""
    prefix = f"/audio/{UPLOADS_SUBDIR}/"
    if not file_path.startswith(prefix):
        return
    target = (_uploads_dir() / file_path.removeprefix(prefix)).resolve()
    if target.parent == _uploads_dir().resolve() and target.is_file():
        target.unlink()


@router.get("", response_model=list[ModuleSummaryOut])
async def list_modules(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(BaitModule)
        .options(selectinload(BaitModule.clips))
        .order_by(BaitModule.name)
    )
    modules = result.scalars().all()
    return [
        ModuleSummaryOut(
            id=m.id,
            name=m.name,
            description=m.description,
            script_count=sum(1 for c in m.clips if c.kind == "script"),
            filler_count=sum(1 for c in m.clips if c.kind == "filler"),
            updated_at=m.updated_at,
        )
        for m in modules
    ]


@router.post("", response_model=ModuleOut)
async def create_module(body: ModuleCreate, db: AsyncSession = Depends(get_db)):
    name = body.name.strip()
    if not name:
        raise HTTPException(status_code=400, detail="Name cannot be empty")

    module = BaitModule(name=name, description=body.description)
    db.add(module)
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=409, detail=f"A module named '{name}' already exists"
        )
    await db.refresh(module, attribute_names=["clips"])
    return module


@router.post("/generate", response_model=ModuleGenerateOut)
async def generate_module(
    body: ModuleGenerateRequest, db: AsyncSession = Depends(get_db)
):
    """Create a module and voice all its lines via ElevenLabs.

    Lines come from a built-in template (template_key) or an existing
    module used as a template (source_module_id). Clips are generated in
    the background; progress arrives as 'module_generation' websocket
    messages.
    """
    if not settings.elevenlabs_api_key:
        raise HTTPException(
            status_code=503,
            detail="ElevenLabs TTS is not configured. Set ELEVENLABS_API_KEY "
            "in your .env to generate voiced modules.",
        )

    name = body.name.strip()
    if not name:
        raise HTTPException(status_code=400, detail="Name cannot be empty")
    voice_id = body.voice_id.strip()
    if not voice_id:
        raise HTTPException(status_code=400, detail="voice_id cannot be empty")

    if (body.template_key is None) == (body.source_module_id is None):
        raise HTTPException(
            status_code=400,
            detail="Provide exactly one of template_key or source_module_id",
        )

    if body.template_key is not None:
        template = TEMPLATES.get(body.template_key)
        if not template:
            raise HTTPException(status_code=404, detail="Template not found")
        lines = list(template.lines)
        description = f"{template.name} — voiced via ElevenLabs ({voice_id})"
    else:
        source = await _get_module(db, body.source_module_id)
        lines = lines_from_module(source)
        description = (
            f"Copy of '{source.name}' — voiced via ElevenLabs ({voice_id})"
        )

    if not lines:
        raise HTTPException(status_code=400, detail="Template has no lines")

    module = BaitModule(name=name, description=description)
    db.add(module)
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=409, detail=f"A module named '{name}' already exists"
        )
    await db.refresh(module, attribute_names=["clips"])

    module_generation.start_generation(module.id, voice_id, lines)
    return ModuleGenerateOut(module=module, total_lines=len(lines))


@router.get("/{module_id}", response_model=ModuleOut)
async def get_module(module_id: int, db: AsyncSession = Depends(get_db)):
    return await _get_module(db, module_id)


@router.put("/{module_id}", response_model=ModuleOut)
async def update_module(
    module_id: int, body: ModuleUpdate, db: AsyncSession = Depends(get_db)
):
    module = await _get_module(db, module_id)
    if body.name is not None:
        name = body.name.strip()
        if not name:
            raise HTTPException(status_code=400, detail="Name cannot be empty")
        module.name = name
    if body.description is not None:
        module.description = body.description
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=409, detail="Module name already in use")
    # updated_at is server-generated and expires on commit (see contacts.py)
    await db.refresh(module, attribute_names=["updated_at", "clips"])
    return module


@router.delete("/{module_id}")
async def delete_module(module_id: int, db: AsyncSession = Depends(get_db)):
    module = await _get_module(db, module_id)
    uploaded = [c.file_path for c in module.clips]
    await db.delete(module)
    await db.commit()
    for file_path in uploaded:
        _delete_uploaded_file(file_path)
    return {"ok": True}


@router.post("/{module_id}/clips", response_model=ModuleClipOut)
async def upload_clip(
    module_id: int,
    file: UploadFile = File(...),
    kind: str = Form("script"),
    label: str | None = Form(None),
    tier: int | None = Form(None),
    expected_duration: float | None = Form(None),
    db: AsyncSession = Depends(get_db),
):
    module = await _get_module(db, module_id)

    if kind not in ("script", "filler"):
        raise HTTPException(status_code=400, detail="kind must be script or filler")
    if kind == "filler":
        tier = tier or 1
        if not 1 <= tier <= 3:
            raise HTTPException(status_code=400, detail="tier must be 1-3")
        expected_duration = None
    else:
        tier = None

    original_name = file.filename or ""
    ext = Path(original_name).suffix.lower()
    if ext not in ALLOWED_AUDIO_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported audio type; use one of "
            f"{', '.join(sorted(ALLOWED_AUDIO_EXTENSIONS))}",
        )

    filename = f"{uuid.uuid4().hex[:12]}{ext}"
    (_uploads_dir() / filename).write_bytes(await file.read())

    same_kind = [c for c in module.clips if c.kind == kind]
    position = max((c.position for c in same_kind), default=-1) + 1

    clip = ModuleClip(
        module_id=module.id,
        kind=kind,
        label=(label or Path(original_name).stem or "Untitled").strip(),
        file_path=f"/audio/{UPLOADS_SUBDIR}/{filename}",
        tier=tier,
        expected_duration=expected_duration,
        position=position,
    )
    db.add(clip)
    await db.commit()
    await db.refresh(clip)
    return clip


@router.put("/{module_id}/clips/{clip_id}", response_model=ModuleClipOut)
async def update_clip(
    module_id: int,
    clip_id: int,
    body: ModuleClipUpdate,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(ModuleClip).where(
            ModuleClip.id == clip_id, ModuleClip.module_id == module_id
        )
    )
    clip = result.scalar_one_or_none()
    if not clip:
        raise HTTPException(status_code=404, detail="Clip not found")

    if body.label is not None:
        clip.label = body.label.strip() or clip.label
    if body.tier is not None:
        if clip.kind != "filler":
            raise HTTPException(status_code=400, detail="Only fillers have tiers")
        if not 1 <= body.tier <= 3:
            raise HTTPException(status_code=400, detail="tier must be 1-3")
        clip.tier = body.tier
    if body.expected_duration is not None:
        if clip.kind != "script":
            raise HTTPException(
                status_code=400, detail="Only script steps have expected durations"
            )
        clip.expected_duration = body.expected_duration

    await db.commit()
    await db.refresh(clip)
    return clip


@router.delete("/{module_id}/clips/{clip_id}")
async def delete_clip(
    module_id: int, clip_id: int, db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(ModuleClip).where(
            ModuleClip.id == clip_id, ModuleClip.module_id == module_id
        )
    )
    clip = result.scalar_one_or_none()
    if not clip:
        raise HTTPException(status_code=404, detail="Clip not found")

    file_path = clip.file_path
    await db.delete(clip)
    await db.commit()
    _delete_uploaded_file(file_path)
    return {"ok": True}


@router.post("/{module_id}/reorder", response_model=ModuleOut)
async def reorder_clips(
    module_id: int,
    body: ModuleReorderRequest,
    db: AsyncSession = Depends(get_db),
):
    module = await _get_module(db, module_id)
    clips_by_id = {c.id: c for c in module.clips if c.kind == body.kind}

    unknown = [cid for cid in body.clip_ids if cid not in clips_by_id]
    if unknown:
        raise HTTPException(
            status_code=400,
            detail=f"Clips not in this module's {body.kind} list: {unknown}",
        )

    for position, clip_id in enumerate(body.clip_ids):
        clips_by_id[clip_id].position = position

    await db.commit()
    # The already-loaded relationship keeps its old order; re-sort for the response.
    module.clips.sort(key=lambda c: (c.kind, c.tier or 0, c.position, c.id))
    return module
