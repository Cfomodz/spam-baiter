import { useEffect, useState } from "react";
import { createModule, getModule, getModules } from "../../api/modules";
import type { BaitModule, ModuleSummary } from "../../types";
import ModuleEditor from "./ModuleEditor";

export default function ModulesPage() {
  const [modules, setModules] = useState<ModuleSummary[]>([]);
  const [selected, setSelected] = useState<BaitModule | null>(null);
  const [newName, setNewName] = useState("");
  const [error, setError] = useState<string | null>(null);

  const refreshList = () => getModules().then(setModules).catch(() => {});

  const select = (id: number) => {
    getModule(id).then(setSelected).catch(() => {});
  };

  useEffect(() => {
    refreshList();
  }, []);

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
      <aside className="w-64 flex-shrink-0 border-r border-gray-700 flex flex-col overflow-hidden">
        <div className="p-3 border-b border-gray-700">
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
          {error && (
            <div className="mt-1 text-xs text-accent-red truncate" title={error}>
              {error}
            </div>
          )}
        </div>
        <div className="flex-1 overflow-y-auto p-2 space-y-1">
          {modules.map((m) => (
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
                {m.script_count} steps · {m.filler_count} fillers
              </div>
            </button>
          ))}
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
