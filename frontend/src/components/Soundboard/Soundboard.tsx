import { useEffect, useState } from "react";
import { getClips, getLegacyClips } from "../../api/soundboard";
import { useStore } from "../../store";
import type { LegacyClip } from "../../types";
import ClipCard from "./ClipCard";

export default function Soundboard() {
  const clips = useStore((s) => s.clips);
  const setClips = useStore((s) => s.setClips);
  const legacyClips = useStore((s) => s.legacyClips);
  const setLegacyClips = useStore((s) => s.setLegacyClips);
  const setPlayingClipId = useStore((s) => s.setPlayingClipId);
  const playingClipId = useStore((s) => s.playingClipId);

  const [tab, setTab] = useState<"generated" | "legacy">("generated");

  const refresh = () => {
    getClips().then(setClips).catch(() => {});
  };

  useEffect(() => {
    refresh();
    getLegacyClips().then(setLegacyClips).catch(() => {});
  }, []);

  const pinned = clips.filter((c) => c.pinned);
  const session = clips.filter((c) => !c.pinned);

  return (
    <div className="flex flex-col h-full">
      <div className="p-3 border-b border-gray-700">
        <h2 className="text-sm font-semibold text-gray-300 uppercase tracking-wider mb-2">
          Soundboard
        </h2>
        <div className="flex gap-1">
          <button
            onClick={() => setTab("generated")}
            className={`px-3 py-1 text-xs rounded transition-colors ${
              tab === "generated"
                ? "bg-accent-blue text-white"
                : "bg-surface-lighter text-gray-400 hover:text-gray-200"
            }`}
          >
            Generated ({clips.length})
          </button>
          <button
            onClick={() => setTab("legacy")}
            className={`px-3 py-1 text-xs rounded transition-colors ${
              tab === "legacy"
                ? "bg-accent-blue text-white"
                : "bg-surface-lighter text-gray-400 hover:text-gray-200"
            }`}
          >
            Legacy ({legacyClips.length})
          </button>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto p-3">
        {tab === "generated" && (
          <div className="space-y-3">
            {pinned.length > 0 && (
              <div>
                <h3 className="text-xs font-semibold text-accent-yellow mb-2 uppercase">
                  Pinned
                </h3>
                <div className="grid grid-cols-2 gap-2">
                  {pinned.map((c) => (
                    <ClipCard key={c.id} clip={c} onRefresh={refresh} />
                  ))}
                </div>
              </div>
            )}
            {session.length > 0 && (
              <div>
                <h3 className="text-xs font-semibold text-gray-400 mb-2 uppercase">
                  Session
                </h3>
                <div className="grid grid-cols-2 gap-2">
                  {session.map((c) => (
                    <ClipCard key={c.id} clip={c} onRefresh={refresh} />
                  ))}
                </div>
              </div>
            )}
            {clips.length === 0 && (
              <div className="text-center text-gray-500 text-sm py-8">
                Generate speech to populate the soundboard
              </div>
            )}
          </div>
        )}

        {tab === "legacy" && (
          <div className="space-y-3">
            <LegacySection
              title="Main Responses"
              clips={legacyClips.filter((c) => c.category === "main")}
              playingId={playingClipId}
              onPlay={setPlayingClipId}
            />
            <LegacySection
              title="Tier 1 - Quick Acks"
              clips={legacyClips.filter((c) => c.category === "tier_1")}
              playingId={playingClipId}
              onPlay={setPlayingClipId}
            />
            <LegacySection
              title="Tier 2 - Deference"
              clips={legacyClips.filter((c) => c.category === "tier_2")}
              playingId={playingClipId}
              onPlay={setPlayingClipId}
            />
            <LegacySection
              title="Tier 3 - Stalling"
              clips={legacyClips.filter((c) => c.category === "tier_3")}
              playingId={playingClipId}
              onPlay={setPlayingClipId}
            />
          </div>
        )}
      </div>
    </div>
  );
}

function LegacySection({
  title,
  clips,
  playingId,
  onPlay,
}: {
  title: string;
  clips: LegacyClip[];
  playingId: string | null;
  onPlay: (id: string | null) => void;
}) {
  if (clips.length === 0) return null;

  const handlePlay = (clip: LegacyClip) => {
    const legacyId = `legacy-${clip.id}`;
    if (playingId === legacyId) {
      onPlay(null);
      return;
    }
    const audio = new Audio(`/soundboard-files/${clip.file_path}`);
    audio.onended = () => onPlay(null);
    audio.play();
    onPlay(legacyId);
  };

  return (
    <div>
      <h3 className="text-xs font-semibold text-gray-400 mb-2 uppercase">
        {title}
      </h3>
      <div className="grid grid-cols-2 gap-1">
        {clips.map((clip) => {
          const legacyId = `legacy-${clip.id}`;
          const isPlaying = playingId === legacyId;
          return (
            <button
              key={clip.id}
              onClick={() => handlePlay(clip)}
              className={`px-2 py-2 text-xs rounded text-left truncate transition-colors ${
                isPlaying
                  ? "bg-accent-green text-black"
                  : "bg-surface-lighter hover:bg-gray-600 text-gray-300"
              }`}
              title={clip.label}
            >
              {clip.label}
            </button>
          );
        })}
      </div>
    </div>
  );
}
