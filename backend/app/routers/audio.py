from fastapi import APIRouter

from ..schemas import RouteToggle, RoutingMatrixOut
from ..services.audio_router import audio_router

router = APIRouter()


@router.get("/routing", response_model=RoutingMatrixOut)
async def get_routing():
    return RoutingMatrixOut(
        routes=audio_router.get_routes(),
        mic_muted=audio_router.mic_muted,
    )


@router.post("/routing")
async def set_route(body: RouteToggle):
    audio_router.set_route(body.source, body.line_id, body.enabled)
    await audio_router.broadcast_state()
    return {"ok": True}


@router.post("/mic/mute")
async def mute_mic():
    audio_router.set_mic_muted(True)
    await audio_router.broadcast_state()
    return {"mic_muted": True}


@router.post("/mic/unmute")
async def unmute_mic():
    audio_router.set_mic_muted(False)
    await audio_router.broadcast_state()
    return {"mic_muted": False}


@router.post("/mic/toggle")
async def toggle_mic():
    muted = audio_router.toggle_mic_mute()
    await audio_router.broadcast_state()
    return {"mic_muted": muted}
