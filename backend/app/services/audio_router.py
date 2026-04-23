from ..ws.handler import manager


class AudioRouter:
    def __init__(self) -> None:
        self._routes: dict[str, dict[str, bool]] = {}
        self._mic_muted: bool = True

    @property
    def mic_muted(self) -> bool:
        return self._mic_muted

    def get_routes(self) -> dict[str, dict[str, bool]]:
        return self._routes

    def set_route(self, source: str, line_id: str, enabled: bool) -> None:
        if source not in self._routes:
            self._routes[source] = {}
        self._routes[source][line_id] = enabled

    def toggle_mic_mute(self) -> bool:
        self._mic_muted = not self._mic_muted
        return self._mic_muted

    def set_mic_muted(self, muted: bool) -> None:
        self._mic_muted = muted

    def add_line(self, line_id: str) -> None:
        for source in self._routes:
            if line_id not in self._routes[source]:
                self._routes[source][line_id] = False
        for default_source in ["mic", "tts_playback"]:
            if default_source not in self._routes:
                self._routes[default_source] = {}
            self._routes[default_source][line_id] = False

    def remove_line(self, line_id: str) -> None:
        for source in self._routes:
            self._routes[source].pop(line_id, None)

    def get_routed_lines(self, source: str) -> list[str]:
        if source not in self._routes:
            return []
        return [lid for lid, enabled in self._routes[source].items() if enabled]

    async def broadcast_state(self) -> None:
        await manager.broadcast(
            {
                "type": "routing_update",
                "payload": {
                    "routes": self._routes,
                    "mic_muted": self._mic_muted,
                },
            }
        )


audio_router = AudioRouter()
