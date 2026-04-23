import { useEffect, useState } from "react";
import { getVoices, generateSpeech } from "../../api/tts";
import { useStore } from "../../store";
import VoiceSelector from "./VoiceSelector";
import TextInput from "./TextInput";

export default function TTSPanel() {
  const voices = useStore((s) => s.voices);
  const setVoices = useStore((s) => s.setVoices);
  const addClip = useStore((s) => s.addClip);
  const lines = useStore((s) => s.lines);

  const [selectedVoice, setSelectedVoice] = useState("");
  const [text, setText] = useState("");
  const [generating, setGenerating] = useState(false);

  useEffect(() => {
    getVoices()
      .then(setVoices)
      .catch(() => {});
  }, [setVoices]);

  const handleGenerate = async () => {
    if (!text.trim() || !selectedVoice) return;
    setGenerating(true);
    try {
      const clip = await generateSpeech(text.trim(), selectedVoice);
      addClip(clip);
      setText("");
    } finally {
      setGenerating(false);
    }
  };

  const lineList = Object.values(lines).filter(
    (l) => l.status === "active" || l.status === "merged",
  );

  return (
    <div className="flex flex-col h-full">
      <div className="p-3 border-b border-gray-700">
        <h2 className="text-sm font-semibold text-gray-300 uppercase tracking-wider">
          Text to Speech
        </h2>
      </div>

      <div className="flex-1 overflow-y-auto p-3 space-y-3">
        <VoiceSelector
          voices={voices}
          selected={selectedVoice}
          onSelect={setSelectedVoice}
        />

        <TextInput
          value={text}
          onChange={setText}
          onGenerate={handleGenerate}
          generating={generating}
          disabled={!selectedVoice}
        />

        {lineList.length > 0 && (
          <div className="border-t border-gray-700 pt-3">
            <h3 className="text-xs font-semibold text-gray-400 mb-2 uppercase">
              Route TTS to Lines
            </h3>
            <div className="space-y-1">
              {lineList.map((line) => (
                <RouteToggleRow
                  key={line.line_id}
                  lineId={line.line_id}
                  label={line.number}
                />
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

function RouteToggleRow({
  lineId,
  label,
}: {
  lineId: string;
  label: string;
}) {
  const routing = useStore((s) => s.routing);
  const enabled = routing.routes?.["tts_playback"]?.[lineId] ?? false;

  const toggle = async () => {
    await fetch("/api/audio/routing", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        source: "tts_playback",
        line_id: lineId,
        enabled: !enabled,
      }),
    });
  };

  return (
    <label className="flex items-center justify-between bg-surface-lighter rounded px-3 py-2 cursor-pointer">
      <span className="text-sm">{label}</span>
      <button
        onClick={toggle}
        className={`w-10 h-5 rounded-full transition-colors relative ${
          enabled ? "bg-accent-green" : "bg-gray-600"
        }`}
      >
        <span
          className={`absolute top-0.5 w-4 h-4 bg-white rounded-full transition-transform ${
            enabled ? "translate-x-5" : "translate-x-0.5"
          }`}
        />
      </button>
    </label>
  );
}
