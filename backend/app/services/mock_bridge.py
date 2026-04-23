import asyncio
import time
import uuid
from typing import Callable

from .call_provider import LineState, LineStatus, PhoneBridge


class MockBridge(PhoneBridge):
    def __init__(self) -> None:
        self._lines: dict[str, LineState] = {}
        self._audio_callback: Callable[[str, bytes], None] | None = None
        self._status_callback: Callable[[LineState], None] | None = None
        self._tasks: dict[str, asyncio.Task] = {}  # type: ignore[type-arg]

    async def initialize(self) -> None:
        pass

    async def shutdown(self) -> None:
        for task in self._tasks.values():
            task.cancel()
        self._tasks.clear()
        self._lines.clear()

    async def dial(self, number: str) -> str:
        line_id = str(uuid.uuid4())[:8]
        state = LineState(
            line_id=line_id,
            status=LineStatus.DIALING,
            number=number,
        )
        self._lines[line_id] = state
        self._notify_status(state)

        task = asyncio.create_task(self._simulate_dial(line_id))
        self._tasks[line_id] = task
        return line_id

    async def _simulate_dial(self, line_id: str) -> None:
        await asyncio.sleep(2)
        if line_id in self._lines:
            self._lines[line_id].status = LineStatus.ACTIVE
            self._lines[line_id].started_at = time.time()
            self._notify_status(self._lines[line_id])

    async def hangup(self, line_id: str) -> None:
        if line_id in self._lines:
            self._lines[line_id].status = LineStatus.DISCONNECTED
            self._notify_status(self._lines[line_id])
            if line_id in self._tasks:
                self._tasks[line_id].cancel()
                del self._tasks[line_id]
            del self._lines[line_id]

    async def hold(self, line_id: str) -> None:
        if line_id in self._lines and self._lines[line_id].status == LineStatus.ACTIVE:
            self._lines[line_id].status = LineStatus.HELD
            self._notify_status(self._lines[line_id])

    async def unhold(self, line_id: str) -> None:
        if line_id in self._lines and self._lines[line_id].status == LineStatus.HELD:
            self._lines[line_id].status = LineStatus.ACTIVE
            self._notify_status(self._lines[line_id])

    async def merge(self, line_ids: list[str]) -> str:
        merge_id = str(uuid.uuid4())[:8]
        numbers = []
        for lid in line_ids:
            if lid in self._lines:
                numbers.append(self._lines[lid].number)
                self._lines[lid].status = LineStatus.MERGED
                self._lines[lid].merged_with = [merge_id]
                self._notify_status(self._lines[lid])

        merged_state = LineState(
            line_id=merge_id,
            status=LineStatus.ACTIVE,
            number=" + ".join(numbers),
            started_at=time.time(),
            merged_with=line_ids,
        )
        self._lines[merge_id] = merged_state
        self._notify_status(merged_state)
        return merge_id

    async def send_audio(self, line_id: str, pcm_data: bytes) -> None:
        pass

    def set_audio_callback(
        self, callback: Callable[[str, bytes], None]
    ) -> None:
        self._audio_callback = callback

    def set_status_callback(
        self, callback: Callable[[LineState], None]
    ) -> None:
        self._status_callback = callback

    async def get_lines(self) -> list[LineState]:
        return list(self._lines.values())

    def _notify_status(self, state: LineState) -> None:
        if self._status_callback:
            self._status_callback(state)
