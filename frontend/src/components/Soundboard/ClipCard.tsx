import { useStore } from "../../store";
import { pinClip, unpinClip, deleteClip } from "../../api/soundboard";
import type { SoundboardClip } from "../../types";

interface Props {
  clip: SoundboardClip;
  onRefresh: () => void;
}

export default function ClipCard({ clip, onRefresh }: Props) {
  const playingClipId = useStore((s) => s.playingClipId);
  const setPlayingClipId = useStore((s) => s.setPlayingClipId);
  const isPlaying = playingClipId === clip.id;

  const handlePlay = () => {
    if (isPlaying) {
      setPlayingClipId(null);
      return;
    }
    const audio = new Audio(`/audio/${clip.file_path}`);
    audio.onended = () => setPlayingClipId(null);
    audio.play();
    setPlayingClipId(clip.id);
  };

  const handlePin = async () => {
    if (clip.pinned) {
      await unpinClip(clip.id);
    } else {
      await pinClip(clip.id);
    }
    onRefresh();
  };

  const handleDelete = async () => {
    await deleteClip(clip.id);
    onRefresh();
  };

  return (
    <div
      className={`bg-surface-lighter border rounded-lg p-2 flex flex-col gap-1 ${
        isPlaying ? "border-accent-green" : "border-gray-700"
      }`}
    >
      <div className="text-xs text-gray-300 truncate" title={clip.label}>
        {clip.label}
      </div>
      {clip.voice_name && (
        <div className="text-xs text-gray-500 truncate">{clip.voice_name}</div>
      )}
      <div className="flex items-center gap-1 mt-1">
        <button
          onClick={handlePlay}
          className={`flex-1 px-2 py-1 text-xs rounded transition-colors ${
            isPlaying
              ? "bg-accent-green text-black"
              : "bg-surface-light hover:bg-gray-600"
          }`}
        >
          {isPlaying ? "Stop" : "Play"}
        </button>
        <button
          onClick={handlePin}
          className={`px-2 py-1 text-xs rounded transition-colors ${
            clip.pinned
              ? "bg-accent-yellow/20 text-accent-yellow"
              : "bg-surface-light hover:bg-gray-600 text-gray-400"
          }`}
          title={clip.pinned ? "Unpin" : "Pin"}
        >
          {clip.pinned ? "Pinned" : "Pin"}
        </button>
        <button
          onClick={handleDelete}
          className="px-2 py-1 text-xs bg-surface-light hover:bg-gray-600 text-gray-400 rounded transition-colors"
          title="Delete"
        >
          x
        </button>
      </div>
    </div>
  );
}
