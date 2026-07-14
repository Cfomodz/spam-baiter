import { useRef, useState } from "react";
import {
  deleteModule,
  deleteModuleClip,
  getModule,
  reorderClips,
  updateClip,
  updateModule,
  uploadClip,
} from "../../api/modules";
import type { BaitModule, ModuleClip } from "../../types";

interface Props {
  module: BaitModule;
  onChanged: (module: BaitModule) => void;
  onDeleted: () => void;
}

export default function ModuleEditor({ module, onChanged, onDeleted }: Props) {
  const [playingId, setPlayingId] = useState<number | null>(null);
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const [error, setError] = useState<string | null>(null);

  const script = module.clips
    .filter((c) => c.kind === "script")
    .sort((a, b) => a.position - b.position);
  const fillers = module.clips.filter((c) => c.kind === "filler");

  const refresh = () =>
    getModule(module.id).then(onChanged).catch(() => {});

  const run = async (action: () => Promise<unknown>) => {
    try {
      await action();
      setError(null);
      await refresh();
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    }
  };

  const togglePlay = (clip: ModuleClip) => {
    audioRef.current?.pause();
    if (playingId === clip.id) {
      setPlayingId(null);
      return;
    }
    const audio = new Audio(clip.file_path);
    audioRef.current = audio;
    audio.onended = () => setPlayingId(null);
    audio.play();
    setPlayingId(clip.id);
  };

  const moveStep = (index: number, delta: number) => {
    const target = index + delta;
    if (target < 0 || target >= script.length) return;
    const order = [...script];
    [order[index], order[target]] = [order[target], order[index]];
    run(() => reorderClips(module.id, "script", order.map((c) => c.id)));
  };

  const handleDeleteModule = () => {
    if (!window.confirm(`Delete module "${module.name}" and all its clips?`)) {
      return;
    }
    deleteModule(module.id)
      .then(onDeleted)
      .catch((e) => setError(e instanceof Error ? e.message : String(e)));
  };

  return (
    <div className="p-4 space-y-6 max-w-3xl">
      {/* Header */}
      <div className="space-y-2">
        <div className="flex items-center gap-2">
          <input
            key={`name-${module.id}-${module.name}`}
            defaultValue={module.name}
            onBlur={(e) => {
              const name = e.target.value.trim();
              if (name && name !== module.name) {
                run(() => updateModule(module.id, { name }));
              }
            }}
            className="flex-1 min-w-0 px-2 py-1 text-lg font-semibold bg-transparent border border-transparent hover:border-gray-700 focus:border-accent-blue rounded focus:outline-none"
          />
          <button
            onClick={handleDeleteModule}
            className="px-3 py-1 text-xs bg-surface-lighter hover:bg-accent-red/20 text-gray-400 hover:text-accent-red rounded transition-colors"
          >
            Delete Module
          </button>
        </div>
        <textarea
          key={`desc-${module.id}-${module.description ?? ""}`}
          defaultValue={module.description ?? ""}
          placeholder="Describe this persona / scam script..."
          rows={2}
          onBlur={(e) => {
            const description = e.target.value;
            if (description !== (module.description ?? "")) {
              run(() => updateModule(module.id, { description }));
            }
          }}
          className="w-full px-2 py-1 text-sm text-gray-300 bg-surface-lighter border border-gray-700 rounded focus:outline-none focus:border-accent-blue resize-none"
        />
        {error && (
          <div className="text-xs text-accent-red truncate" title={error}>
            {error}
          </div>
        )}
      </div>

      {/* Script steps */}
      <section>
        <div className="flex items-center justify-between mb-2">
          <h3 className="text-xs font-semibold text-gray-400 uppercase tracking-wider">
            Call Script ({script.length} steps)
          </h3>
          <UploadButton
            label="+ Add step"
            onUpload={(file) =>
              run(() => uploadClip(module.id, file, { kind: "script" }))
            }
          />
        </div>
        <div className="space-y-1">
          {script.map((clip, i) => (
            <div
              key={clip.id}
              className={`flex items-center gap-2 px-2 py-1.5 rounded border ${
                playingId === clip.id
                  ? "border-accent-green bg-surface-lighter"
                  : "border-gray-700 bg-surface-lighter"
              }`}
            >
              <span className="w-6 text-xs text-gray-500 text-right flex-shrink-0">
                {i + 1}.
              </span>
              <PlayButton
                playing={playingId === clip.id}
                onClick={() => togglePlay(clip)}
              />
              <LabelInput clip={clip} moduleId={module.id} run={run} />
              <input
                key={`dur-${clip.id}-${clip.expected_duration ?? ""}`}
                type="number"
                min={0}
                step={0.5}
                defaultValue={clip.expected_duration ?? ""}
                placeholder="sec"
                title="Expected duration of the scammer's response (seconds)"
                onBlur={(e) => {
                  const value = parseFloat(e.target.value);
                  if (
                    !Number.isNaN(value) &&
                    value !== clip.expected_duration
                  ) {
                    run(() =>
                      updateClip(module.id, clip.id, {
                        expected_duration: value,
                      }),
                    );
                  }
                }}
                className="w-16 flex-shrink-0 px-1 py-0.5 text-xs bg-surface border border-gray-700 rounded focus:outline-none focus:border-accent-blue text-right"
              />
              <div className="flex flex-col flex-shrink-0">
                <ArrowButton dir="up" disabled={i === 0} onClick={() => moveStep(i, -1)} />
                <ArrowButton
                  dir="down"
                  disabled={i === script.length - 1}
                  onClick={() => moveStep(i, 1)}
                />
              </div>
              <DeleteButton
                onClick={() =>
                  run(() => deleteModuleClip(module.id, clip.id))
                }
              />
            </div>
          ))}
          {script.length === 0 && (
            <div className="text-xs text-gray-500 py-3 text-center">
              Upload audio clips in the order they should play during the call
            </div>
          )}
        </div>
      </section>

      {/* Fillers */}
      <section>
        <div className="flex items-center justify-between mb-2">
          <h3 className="text-xs font-semibold text-gray-400 uppercase tracking-wider">
            Off-Script Fillers ({fillers.length})
          </h3>
        </div>
        <div className="space-y-3">
          {[1, 2, 3].map((tier) => (
            <FillerTier
              key={tier}
              tier={tier}
              clips={fillers
                .filter((c) => c.tier === tier)
                .sort((a, b) => a.position - b.position)}
              moduleId={module.id}
              playingId={playingId}
              togglePlay={togglePlay}
              run={run}
            />
          ))}
        </div>
      </section>
    </div>
  );
}

const TIER_TITLES: Record<number, string> = {
  1: "Tier 1 — Quick Acks",
  2: "Tier 2 — Deference",
  3: "Tier 3 — Stalling Stories",
};

function FillerTier({
  tier,
  clips,
  moduleId,
  playingId,
  togglePlay,
  run,
}: {
  tier: number;
  clips: ModuleClip[];
  moduleId: number;
  playingId: number | null;
  togglePlay: (clip: ModuleClip) => void;
  run: (action: () => Promise<unknown>) => Promise<void>;
}) {
  return (
    <div>
      <div className="flex items-center justify-between mb-1">
        <h4 className="text-xs font-semibold text-gray-500">
          {TIER_TITLES[tier]}
        </h4>
        <UploadButton
          label="+ Add filler"
          onUpload={(file) =>
            run(() => uploadClip(moduleId, file, { kind: "filler", tier }))
          }
        />
      </div>
      <div className="space-y-1">
        {clips.map((clip) => (
          <div
            key={clip.id}
            className="flex items-center gap-2 px-2 py-1.5 rounded border border-gray-700 bg-surface-lighter"
          >
            <PlayButton
              playing={playingId === clip.id}
              onClick={() => togglePlay(clip)}
            />
            <LabelInput clip={clip} moduleId={moduleId} run={run} />
            <select
              value={tier}
              onChange={(e) =>
                run(() =>
                  updateClip(moduleId, clip.id, {
                    tier: parseInt(e.target.value, 10),
                  }),
                )
              }
              className="flex-shrink-0 px-1 py-0.5 text-xs bg-surface border border-gray-700 rounded focus:outline-none"
              title="Move to another tier"
            >
              <option value={1}>T1</option>
              <option value={2}>T2</option>
              <option value={3}>T3</option>
            </select>
            <DeleteButton
              onClick={() => run(() => deleteModuleClip(moduleId, clip.id))}
            />
          </div>
        ))}
        {clips.length === 0 && (
          <div className="text-xs text-gray-600 py-1 pl-2">No clips</div>
        )}
      </div>
    </div>
  );
}

function LabelInput({
  clip,
  moduleId,
  run,
}: {
  clip: ModuleClip;
  moduleId: number;
  run: (action: () => Promise<unknown>) => Promise<void>;
}) {
  return (
    <input
      key={`label-${clip.id}-${clip.label}`}
      defaultValue={clip.label}
      title={clip.label}
      onBlur={(e) => {
        const label = e.target.value.trim();
        if (label && label !== clip.label) {
          run(() => updateClip(moduleId, clip.id, { label }));
        }
      }}
      className="flex-1 min-w-0 px-1 py-0.5 text-xs text-gray-300 bg-transparent border border-transparent hover:border-gray-700 focus:border-accent-blue rounded focus:outline-none truncate"
    />
  );
}

function PlayButton({
  playing,
  onClick,
}: {
  playing: boolean;
  onClick: () => void;
}) {
  return (
    <button
      onClick={onClick}
      className={`flex-shrink-0 px-2 py-0.5 text-xs rounded transition-colors ${
        playing
          ? "bg-accent-green text-black"
          : "bg-surface-light hover:bg-gray-600 text-gray-300"
      }`}
    >
      {playing ? "Stop" : "Play"}
    </button>
  );
}

function ArrowButton({
  dir,
  disabled,
  onClick,
}: {
  dir: "up" | "down";
  disabled: boolean;
  onClick: () => void;
}) {
  return (
    <button
      onClick={onClick}
      disabled={disabled}
      className="px-1 text-xs leading-3 text-gray-500 hover:text-gray-200 disabled:opacity-20 disabled:cursor-default"
      title={dir === "up" ? "Move earlier" : "Move later"}
    >
      {dir === "up" ? "▲" : "▼"}
    </button>
  );
}

function DeleteButton({ onClick }: { onClick: () => void }) {
  return (
    <button
      onClick={onClick}
      className="flex-shrink-0 px-2 py-0.5 text-xs bg-surface-light hover:bg-gray-600 text-gray-400 rounded transition-colors"
      title="Delete clip"
    >
      x
    </button>
  );
}

function UploadButton({
  label,
  onUpload,
}: {
  label: string;
  onUpload: (file: File) => void;
}) {
  const inputRef = useRef<HTMLInputElement | null>(null);
  return (
    <>
      <input
        ref={inputRef}
        type="file"
        accept=".wav,.mp3,.ogg,.m4a,.webm,audio/*"
        className="hidden"
        onChange={(e) => {
          const file = e.target.files?.[0];
          if (file) onUpload(file);
          e.target.value = "";
        }}
      />
      <button
        onClick={() => inputRef.current?.click()}
        className="px-2 py-0.5 text-xs bg-surface-lighter hover:bg-gray-600 text-gray-300 rounded border border-gray-700 transition-colors"
      >
        {label}
      </button>
    </>
  );
}
