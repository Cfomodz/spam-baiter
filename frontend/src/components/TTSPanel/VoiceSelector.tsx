import type { Voice } from "../../types";

interface Props {
  voices: Voice[];
  selected: string;
  onSelect: (voiceId: string) => void;
}

export default function VoiceSelector({ voices, selected, onSelect }: Props) {
  return (
    <select
      value={selected}
      onChange={(e) => onSelect(e.target.value)}
      className="w-full bg-surface-lighter border border-gray-600 rounded px-3 py-2 text-sm text-gray-100 focus:outline-none focus:border-accent-blue"
    >
      <option value="">Select a voice...</option>
      {voices.map((v) => (
        <option key={v.voice_id} value={v.voice_id}>
          {v.name}
        </option>
      ))}
    </select>
  );
}
