from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Callable


class LineStatus(str, Enum):
    IDLE = "idle"
    DIALING = "dialing"
    ACTIVE = "active"
    HELD = "held"
    MERGED = "merged"
    DISCONNECTED = "disconnected"


@dataclass
class LineState:
    line_id: str
    status: LineStatus
    number: str
    started_at: float | None = None
    merged_with: list[str] = field(default_factory=list)


class PhoneBridge(ABC):
    @abstractmethod
    async def initialize(self) -> None: ...

    @abstractmethod
    async def shutdown(self) -> None: ...

    @abstractmethod
    async def dial(self, number: str) -> str: ...

    @abstractmethod
    async def hangup(self, line_id: str) -> None: ...

    @abstractmethod
    async def hold(self, line_id: str) -> None: ...

    @abstractmethod
    async def unhold(self, line_id: str) -> None: ...

    @abstractmethod
    async def merge(self, line_ids: list[str]) -> str: ...

    @abstractmethod
    async def send_audio(self, line_id: str, pcm_data: bytes) -> None: ...

    @abstractmethod
    def set_audio_callback(
        self, callback: Callable[[str, bytes], None]
    ) -> None: ...

    @abstractmethod
    def set_status_callback(
        self, callback: Callable[[LineState], None]
    ) -> None: ...

    @abstractmethod
    async def get_lines(self) -> list[LineState]: ...
