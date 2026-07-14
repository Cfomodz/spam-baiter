import { useEffect, useRef } from "react";
import type { WSMessage } from "../types";
import { useStore } from "../store";

export function useWebSocket() {
  const wsRef = useRef<WebSocket | null>(null);
  const {
    setLine,
    removeLine,
    setRouting,
    addClip,
    setPlayingClipId,
    setGenerationProgress,
  } = useStore();

  useEffect(() => {
    let reconnectTimer: ReturnType<typeof setTimeout>;
    let alive = true;

    function connect() {
      const proto = window.location.protocol === "https:" ? "wss:" : "ws:";
      const ws = new WebSocket(`${proto}//${window.location.host}/ws`);
      wsRef.current = ws;

      ws.onmessage = (ev) => {
        const msg: WSMessage = JSON.parse(ev.data);
        switch (msg.type) {
          case "line_update":
            setLine(msg.payload);
            break;
          case "line_removed":
            removeLine(msg.payload.line_id);
            break;
          case "routing_update":
            setRouting(msg.payload);
            break;
          case "clip_ready":
            addClip({
              id: msg.payload.clip_id,
              label: msg.payload.label,
              voice_id: "",
              voice_name: msg.payload.voice_name,
              file_path: "",
              pinned: msg.payload.pinned,
              source: "generated",
            });
            break;
          case "playback_state":
            setPlayingClipId(
              msg.payload.state === "playing" ? msg.payload.clip_id : null,
            );
            break;
          case "module_generation":
            setGenerationProgress(msg.payload);
            break;
        }
      };

      ws.onclose = () => {
        if (alive) reconnectTimer = setTimeout(connect, 2000);
      };
    }

    connect();

    return () => {
      alive = false;
      clearTimeout(reconnectTimer);
      wsRef.current?.close();
    };
  }, [
    setLine,
    removeLine,
    setRouting,
    addClip,
    setPlayingClipId,
    setGenerationProgress,
  ]);
}
