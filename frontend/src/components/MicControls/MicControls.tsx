import { useStore } from "../../store";
import RouteToggle from "../AudioRouter/RouteToggle";

export default function MicControls() {
  const routing = useStore((s) => s.routing);
  const lines = useStore((s) => s.lines);

  const activeLines = Object.values(lines).filter(
    (l) => l.status === "active" || l.status === "merged",
  );

  const toggleMic = async () => {
    await fetch("/api/audio/mic/toggle", { method: "POST" });
  };

  const toggleMicLine = async (lineId: string) => {
    const current = routing.routes?.["mic"]?.[lineId] ?? false;
    await fetch("/api/audio/routing", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        source: "mic",
        line_id: lineId,
        enabled: !current,
      }),
    });
  };

  return (
    <div className="flex items-center gap-4 px-4 py-3 border-t border-gray-700 bg-surface-light">
      <button
        onClick={toggleMic}
        className={`flex items-center gap-2 px-4 py-2 rounded-lg font-semibold text-sm transition-all ${
          routing.mic_muted
            ? "bg-gray-700 text-gray-400 hover:bg-gray-600"
            : "bg-accent-red text-white animate-pulse shadow-lg shadow-red-500/30"
        }`}
      >
        <svg
          xmlns="http://www.w3.org/2000/svg"
          viewBox="0 0 24 24"
          fill="currentColor"
          className="w-5 h-5"
        >
          {routing.mic_muted ? (
            <path d="M19 11h-1.7c0 .74-.16 1.43-.43 2.05l1.23 1.23c.56-.98.9-2.09.9-3.28zm-4.02.17c0-.06.02-.11.02-.17V5c0-1.66-1.34-3-3-3S9 3.34 9 5v.18l5.98 5.99zM4.27 3L3 4.27l6.01 6.01V11c0 1.66 1.33 3 2.99 3 .22 0 .44-.03.65-.08l1.66 1.66c-.71.33-1.5.52-2.31.52-2.76 0-5.3-2.1-5.3-5.1H5c0 3.41 2.72 6.23 6 6.72V21h2v-3.28c.91-.13 1.77-.45 2.55-.9l4.17 4.18L21 19.73 4.27 3z" />
          ) : (
            <path d="M12 14c1.66 0 2.99-1.34 2.99-3L15 5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 1.66 1.34 3 3 3zm5.3-3c0 3-2.54 5.1-5.3 5.1S6.7 14 6.7 11H5c0 3.41 2.72 6.23 6 6.72V21h2v-3.28c3.28-.48 6-3.3 6-6.72h-1.7z" />
          )}
        </svg>
        {routing.mic_muted ? "MIC MUTED" : "MIC LIVE"}
      </button>

      {!routing.mic_muted && activeLines.length > 0 && (
        <div className="flex items-center gap-3">
          <span className="text-xs text-gray-400">Route to:</span>
          {activeLines.map((line) => (
            <RouteToggle
              key={line.line_id}
              label={line.number}
              enabled={routing.routes?.["mic"]?.[line.line_id] ?? false}
              onToggle={() => toggleMicLine(line.line_id)}
            />
          ))}
        </div>
      )}

      {routing.mic_muted && activeLines.length > 0 && (
        <span className="text-xs text-gray-500">
          Unmute mic to see line routing options
        </span>
      )}
    </div>
  );
}
