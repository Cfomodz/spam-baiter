import { useStore } from "../../store";
import RouteToggle from "./RouteToggle";

export default function AudioRouter() {
  const routing = useStore((s) => s.routing);
  const lines = useStore((s) => s.lines);

  const activeLines = Object.values(lines).filter(
    (l) => l.status === "active" || l.status === "merged",
  );

  if (activeLines.length === 0) return null;

  const sources = Object.keys(routing.routes);

  const toggle = async (source: string, lineId: string) => {
    const current = routing.routes?.[source]?.[lineId] ?? false;
    await fetch("/api/audio/routing", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        source,
        line_id: lineId,
        enabled: !current,
      }),
    });
  };

  return (
    <div className="p-3 border-t border-gray-700">
      <h3 className="text-xs font-semibold text-gray-400 mb-2 uppercase">
        Audio Routing
      </h3>
      <div className="space-y-2">
        {sources.map((source) => (
          <div key={source}>
            <div className="text-xs text-gray-500 mb-1">
              {source === "mic" ? "Microphone" : source === "tts_playback" ? "TTS / Soundboard" : source}
            </div>
            <div className="flex gap-3 flex-wrap">
              {activeLines.map((line) => (
                <RouteToggle
                  key={`${source}-${line.line_id}`}
                  label={line.number}
                  enabled={routing.routes?.[source]?.[line.line_id] ?? false}
                  onToggle={() => toggle(source, line.line_id)}
                />
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
