from fastapi import APIRouter

from ..schemas import DialRequest, LineOut, MergeRequest
from ..services.audio_router import audio_router
from ..services.line_manager import line_manager

router = APIRouter()


@router.get("", response_model=list[LineOut])
async def get_lines():
    states = await line_manager.get_lines()
    return [
        LineOut(
            line_id=s.line_id,
            status=s.status.value,
            number=s.number,
            started_at=s.started_at,
            merged_with=s.merged_with,
        )
        for s in states
    ]


@router.post("/dial", response_model=LineOut)
async def dial(body: DialRequest):
    line_id = await line_manager.dial(body.number)
    audio_router.add_line(line_id)
    states = await line_manager.get_lines()
    for s in states:
        if s.line_id == line_id:
            return LineOut(
                line_id=s.line_id,
                status=s.status.value,
                number=s.number,
                started_at=s.started_at,
                merged_with=s.merged_with,
            )
    return LineOut(line_id=line_id, status="dialing", number=body.number)


@router.post("/{line_id}/hangup")
async def hangup(line_id: str):
    await line_manager.hangup(line_id)
    audio_router.remove_line(line_id)
    return {"ok": True}


@router.post("/{line_id}/hold")
async def hold(line_id: str):
    await line_manager.hold(line_id)
    return {"ok": True}


@router.post("/{line_id}/unhold")
async def unhold(line_id: str):
    await line_manager.unhold(line_id)
    return {"ok": True}


@router.post("/merge", response_model=LineOut)
async def merge(body: MergeRequest):
    merged_id = await line_manager.merge(body.line_ids)
    audio_router.add_line(merged_id)
    states = await line_manager.get_lines()
    for s in states:
        if s.line_id == merged_id:
            return LineOut(
                line_id=s.line_id,
                status=s.status.value,
                number=s.number,
                started_at=s.started_at,
                merged_with=s.merged_with,
            )
    return LineOut(
        line_id=merged_id,
        status="active",
        number="merged",
        merged_with=body.line_ids,
    )
