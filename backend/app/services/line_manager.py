import asyncio

from ..config import settings
from ..ws.handler import manager
from .call_provider import LineState, PhoneBridge
from .mock_bridge import MockBridge


class LineManager:
    def __init__(self) -> None:
        self._bridge: PhoneBridge | None = None

    async def initialize(self) -> None:
        if settings.phone_bridge == "bluetooth":
            from .bluetooth_bridge import BluetoothBridge
            self._bridge = BluetoothBridge()
        else:
            self._bridge = MockBridge()

        self._bridge.set_status_callback(self._on_status_change)
        await self._bridge.initialize()

    async def shutdown(self) -> None:
        if self._bridge:
            await self._bridge.shutdown()

    @property
    def bridge(self) -> PhoneBridge:
        assert self._bridge is not None
        return self._bridge

    async def dial(self, number: str) -> str:
        return await self.bridge.dial(number)

    async def hangup(self, line_id: str) -> None:
        await self.bridge.hangup(line_id)

    async def hold(self, line_id: str) -> None:
        await self.bridge.hold(line_id)

    async def unhold(self, line_id: str) -> None:
        await self.bridge.unhold(line_id)

    async def merge(self, line_ids: list[str]) -> str:
        return await self.bridge.merge(line_ids)

    async def get_lines(self) -> list[LineState]:
        return await self.bridge.get_lines()

    def _on_status_change(self, state: LineState) -> None:
        asyncio.create_task(
            manager.broadcast(
                {
                    "type": "line_update",
                    "payload": {
                        "line_id": state.line_id,
                        "status": state.status.value,
                        "number": state.number,
                        "started_at": state.started_at,
                        "merged_with": state.merged_with,
                    },
                }
            )
        )


line_manager = LineManager()
