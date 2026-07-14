import { useEffect, useState } from "react";
import Dashboard from "./components/Dashboard/Dashboard";
import ModulesPage from "./components/Modules/ModulesPage";
import { useWebSocket } from "./hooks/useWebSocket";
import { useStore } from "./store";
import { getGroups } from "./api/contacts";
import { getVoices } from "./api/tts";

type View = "dashboard" | "modules";

function App() {
  useWebSocket();

  const [view, setView] = useState<View>("dashboard");
  const setContacts = useStore((s) => s.setContacts);
  const setVoices = useStore((s) => s.setVoices);
  const setRouting = useStore((s) => s.setRouting);

  useEffect(() => {
    getGroups().then(setContacts).catch(() => {});
    getVoices().then(setVoices).catch(() => {});
    fetch("/api/audio/routing")
      .then((r) => r.json())
      .then(setRouting)
      .catch(() => {});
  }, [setContacts, setVoices, setRouting]);

  return (
    <div className="flex flex-col h-screen overflow-hidden bg-surface text-gray-100">
      <nav className="flex-shrink-0 flex items-center gap-3 px-4 py-2 border-b border-gray-700 bg-surface-light">
        <span className="text-sm font-bold text-accent-blue tracking-wider uppercase">
          Spam Baiter
        </span>
        <div className="w-px h-4 bg-gray-700" />
        {(["dashboard", "modules"] as const).map((v) => (
          <button
            key={v}
            onClick={() => setView(v)}
            className={`px-3 py-1 text-xs rounded transition-colors capitalize ${
              view === v
                ? "bg-accent-blue text-white"
                : "bg-surface-lighter text-gray-400 hover:text-gray-200"
            }`}
          >
            {v}
          </button>
        ))}
      </nav>
      <div className="flex-1 min-h-0">
        {view === "dashboard" ? <Dashboard /> : <ModulesPage />}
      </div>
    </div>
  );
}

export default App;
