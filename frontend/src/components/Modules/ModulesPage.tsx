import { useEffect, useState } from "react";
import {
  createModule,
  generateModule,
  getModule,
  getModules,
  getTemplates,
} from "../../api/modules";
import { useStore } from "../../store";
import type { BaitModule, ModuleSummary, ReplyTemplate } from "../../types";
import ModuleEditor from "./ModuleEditor";

export default function ModulesPage() {
  const [modules, setModules] = useState<ModuleSummary[]>([]);
  const [templates, setTemplates] = useState<ReplyTemplate[]>([]);
  const [selected, setSelected] = useState<BaitModule | null>(null);
  const [newName, setNewName] = useState("");
  const [error, setError] = useState<string | null>(null);

  const generationProgress = useStore((s) => s.generationProgress);
  const selectedProgress = selected
    ? generationProgress[selected.id]
    : undefined;

  const refreshList = () => getModules().then(setModules).catch(() => {});

  const select = (id: number) => {
    getModule(id).then(setSelected).catch(() => {});
  };

  useEffect(() => {
    refreshList();
    getTemplates().then(setTemplates).catch(() => {});
  }, []);

  // While clips are being generated for the open module, keep it fresh.
  useEffect(() => {
    if (!selected || !selectedProgress) return;
    getModule(selected.id)
      .then(setSelected)
      .catch(() => {});
    if (selectedProgress.status === "complete") refreshList();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selectedProgress?.done, selectedProgress?.status]);

  const handleCreate = async () => {
    const name = newName.trim();
    if (!name) return;
    try {
      const mod = await createModule(name);
      setNewName("");
      setError(null);
      refreshList();
      setSelected(mod);
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    }
  };

  return (
    <div className="flex h-full min-h-0">
      {/* Module list */}
      <aside className="w-72 flex-shrink-0 border-r border-gray-700 flex flex-col overflow-hidden">
        <div className="p-3 border-b border-gray-700 space-y-3">
          <div>
            <h2 className="text-sm font-semibold text-gray-300 uppercase tracking-wider mb-2">
              Bait Modules
            </h2>
            <div className="flex gap-1">
              <input
                value={newName}
                onChange={(e) => setNewName(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && handleCreate()}
                placeholder="New persona name..."
                className="flex-1 min-w-0 px-2 py-1 text-xs bg-surface-lighter border border-gray-700 rounded focus:outline-none focus:border-accent-blue"
              />
              <button
                onClick={handleCreate}
                className="px-2 py-1 text-xs bg-accent-blue text-white rounded hover:bg-blue-600 transition-colors"
              >
                Add
              </button>
            </div>
          </div>

          <GenerateForm
            templates={templates}
            modules={modules}
            onStarted={(mod) => {
              setError(null);
              refreshList();
              setSelected(mod);
            }}
            onError={setError}
          />

          {error && (
            <div className="text-xs text-accent-red break-words" title={error}>
              {error}
            </div>
          )}
        </div>
        <div className="flex-1 overflow-y-auto p-2 space-y-1">
          {modules.map((m) => {
            const progress = generationProgress[m.id];
            return (
              <button
                key={m.id}
                onClick={() => select(m.id)}
                className={`w-full text-left px-3 py-2 rounded transition-colors ${
                  selected?.id === m.id
                    ? "bg-accent-blue/20 border border-accent-blue"
                    : "bg-surface-lighter border border-gray-700 hover:bg-gray-600"
                }`}
              >
                <div className="text-sm text-gray-200 truncate">{m.name}</div>
                <div className="text-xs text-gray-500">
                  {progress?.status === "running"
                    ? `Generating ${progress.done}/${progress.total}...`
                    : `${m.script_count} steps · ${m.filler_count} fillers`}
                </div>
              </button>
            );
          })}
          {modules.length === 0 && (
            <div className="text-center text-gray-500 text-sm py-8">
              No modules yet
            </div>
          )}
        </div>
      </aside>

      {/* Editor */}
      <section className="flex-1 min-w-0 overflow-y-auto">
        {selected ? (
          <>
            {selectedProgress && (
              <GenerationBanner progress={selectedProgress} />
            )}
            <ModuleEditor
              module={selected}
              onChanged={(m) => {
                setSelected(m);
                refreshList();
              }}
              onDeleted={() => {
                setSelected(null);
                refreshList();
              }}
            />
          </>
        ) : (
          <div className="h-full flex items-center justify-center text-gray-500 text-sm px-8 text-center">
            Select a module to edit its call script and fillers, or create a
            new persona. "Walter Nelson" is the migrated legacy example.
          </div>
        )}
      </section>
    </div>
  );
}

function GenerateForm({
  templates,
  modules,
  onStarted,
  onError,
}: {
  templates: ReplyTemplate[];
  modules: ModuleSummary[];
  onStarted: (module: BaitModule) => void;
  onError: (message: string) => void;
}) {
  const voices = useStore((s) => s.voices);
  const [source, setSource] = useState("");
  const [voiceId, setVoiceId] = useState("");
  const [name, setName] = useState("");
  const [busy, setBusy] = useState(false);

  const handleGenerate = async () => {
    if (!source || !voiceId.trim() || !name.trim() || busy) return;
    setBusy(true);
    try {
      const body: Parameters<typeof generateModule>[0] = {
        name: name.trim(),
        voice_id: voiceId.trim(),
      };
      if (source.startsWith("tpl:")) {
        body.template_key = source.slice(4);
      } else {
        body.source_module_id = parseInt(source.slice(4), 10);
      }
      const result = await generateModule(body);
      setName("");
      onStarted(result.module);
    } catch (e) {
      onError(e instanceof Error ? e.message : String(e));
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="space-y-1">
      <h3 className="text-xs font-semibold text-gray-400 uppercase tracking-wider">
        Voice a Template
      </h3>
      <select
        value={source}
        onChange={(e) => {
          setSource(e.target.value);
          if (!name) {
            const tpl = templates.find(
              (t) => `tpl:${t.key}` === e.target.value,
            );
            const mod = modules.find(
              (m) => `mod:${m.id}` === e.target.value,
            );
            setName(tpl ? tpl.name : mod ? `${mod.name} (new voice)` : "");
          }
        }}
        className="w-full px-2 py-1 text-xs bg-surface-lighter border border-gray-700 rounded focus:outline-none focus:border-accent-blue"
      >
        <option value="">Choose a template...</option>
        {templates.length > 0 && (
          <optgroup label="Templates">
            {templates.map((t) => (
              <option key={t.key} value={`tpl:${t.key}`}>
                {t.name} ({t.script_count + t.filler_count} lines)
              </option>
            ))}
          </optgroup>
        )}
        {modules.length > 0 && (
          <optgroup label="Copy existing module">
            {modules.map((m) => (
              <option key={m.id} value={`mod:${m.id}`}>
                {m.name}
              </option>
            ))}
          </optgroup>
        )}
      </select>
      <input
        value={voiceId}
        onChange={(e) => setVoiceId(e.target.value)}
        list="voice-options"
        placeholder="ElevenLabs voice ID..."
        className="w-full px-2 py-1 text-xs bg-surface-lighter border border-gray-700 rounded focus:outline-none focus:border-accent-blue"
      />
      <datalist id="voice-options">
        {voices.map((v) => (
          <option key={v.voice_id} value={v.voice_id}>
            {v.name}
          </option>
        ))}
      </datalist>
      <input
        value={name}
        onChange={(e) => setName(e.target.value)}
        placeholder="New module name..."
        className="w-full px-2 py-1 text-xs bg-surface-lighter border border-gray-700 rounded focus:outline-none focus:border-accent-blue"
      />
      <button
        onClick={handleGenerate}
        disabled={busy || !source || !voiceId.trim() || !name.trim()}
        className="w-full px-2 py-1 text-xs bg-accent-green/80 hover:bg-accent-green text-black font-semibold rounded transition-colors disabled:opacity-40 disabled:cursor-default"
      >
        {busy ? "Starting..." : "Generate All Clips"}
      </button>
    </div>
  );
}

function GenerationBanner({
  progress,
}: {
  progress: {
    status: "running" | "complete";
    done: number;
    total: number;
    failed: number;
    current?: string;
    failed_labels?: string[];
  };
}) {
  const pct = progress.total
    ? Math.round((progress.done / progress.total) * 100)
    : 0;
  return (
    <div className="m-4 mb-0 p-3 rounded border border-gray-700 bg-surface-lighter space-y-1">
      <div className="flex items-center justify-between text-xs">
        <span
          className={
            progress.status === "complete"
              ? progress.failed > 0
                ? "text-accent-yellow"
                : "text-accent-green"
              : "text-gray-300"
          }
        >
          {progress.status === "complete"
            ? progress.failed > 0
              ? `Generation finished with ${progress.failed} failed line(s)`
              : "Generation complete"
            : `Generating clips... ${progress.current ?? ""}`}
        </span>
        <span className="text-gray-400">
          {progress.done}/{progress.total}
        </span>
      </div>
      <div className="h-1.5 bg-surface rounded overflow-hidden">
        <div
          className={`h-full transition-all ${
            progress.status === "complete"
              ? "bg-accent-green"
              : "bg-accent-blue"
          }`}
          style={{ width: `${pct}%` }}
        />
      </div>
      {progress.failed_labels && progress.failed_labels.length > 0 && (
        <div className="text-xs text-accent-yellow truncate">
          Failed: {progress.failed_labels.join(", ")}
        </div>
      )}
    </div>
  );
}
