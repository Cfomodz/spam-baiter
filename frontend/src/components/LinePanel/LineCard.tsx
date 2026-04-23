import { useEffect, useState } from "react";
import { hangup, hold, unhold } from "../../api/lines";
import type { Line } from "../../types";

const STATUS_COLORS: Record<string, string> = {
  dialing: "bg-accent-yellow",
  active: "bg-accent-green",
  held: "bg-accent-yellow",
  merged: "bg-accent-blue",
  disconnected: "bg-gray-500",
};

function formatDuration(seconds: number): string {
  const m = Math.floor(seconds / 60);
  const s = Math.floor(seconds % 60);
  return `${m}:${s.toString().padStart(2, "0")}`;
}

interface Props {
  line: Line;
  selected: boolean;
  onSelect: () => void;
}

export default function LineCard({ line, selected, onSelect }: Props) {
  const [elapsed, setElapsed] = useState(0);

  useEffect(() => {
    if (!line.started_at || line.status === "disconnected") return;
    const update = () =>
      setElapsed(Math.floor(Date.now() / 1000 - line.started_at!));
    update();
    const interval = setInterval(update, 1000);
    return () => clearInterval(interval);
  }, [line.started_at, line.status]);

  const isActive = line.status === "active" || line.status === "merged";

  return (
    <div
      onClick={onSelect}
      className={`p-3 rounded-lg border cursor-pointer transition-colors ${
        selected
          ? "border-accent-blue bg-surface-lighter"
          : "border-gray-700 bg-surface-light hover:border-gray-600"
      }`}
    >
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center gap-2">
          <span
            className={`w-2 h-2 rounded-full ${STATUS_COLORS[line.status] ?? "bg-gray-500"}`}
          />
          <span className="text-sm font-medium">{line.number}</span>
        </div>
        <span className="text-xs text-gray-400 uppercase">{line.status}</span>
      </div>

      {line.contact_name && (
        <div className="text-xs text-gray-400 mb-2">{line.contact_name}</div>
      )}

      {line.started_at && (
        <div className="text-xs text-gray-500 mb-2">
          {formatDuration(elapsed)}
        </div>
      )}

      {line.merged_with.length > 0 && (
        <div className="text-xs text-accent-blue mb-2">
          Merged: {line.merged_with.join(", ")}
        </div>
      )}

      <div className="flex gap-2">
        {isActive && (
          <button
            onClick={(e) => {
              e.stopPropagation();
              hold(line.line_id);
            }}
            className="px-2 py-1 text-xs bg-accent-yellow/20 text-accent-yellow rounded hover:bg-accent-yellow/30 transition-colors"
          >
            Hold
          </button>
        )}
        {line.status === "held" && (
          <button
            onClick={(e) => {
              e.stopPropagation();
              unhold(line.line_id);
            }}
            className="px-2 py-1 text-xs bg-accent-green/20 text-accent-green rounded hover:bg-accent-green/30 transition-colors"
          >
            Resume
          </button>
        )}
        <button
          onClick={(e) => {
            e.stopPropagation();
            hangup(line.line_id);
          }}
          className="px-2 py-1 text-xs bg-accent-red/20 text-accent-red rounded hover:bg-accent-red/30 transition-colors"
        >
          Hang Up
        </button>
      </div>
    </div>
  );
}
