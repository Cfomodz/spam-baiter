import { useEffect } from "react";
import Dashboard from "./components/Dashboard/Dashboard";
import { useWebSocket } from "./hooks/useWebSocket";
import { useStore } from "./store";
import { getGroups } from "./api/contacts";
import { getVoices } from "./api/tts";

function App() {
  useWebSocket();

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

  return <Dashboard />;
}

export default App;
