import { useState } from "react";
import { dial } from "../../api/lines";

export default function DialPad() {
  const [number, setNumber] = useState("");
  const [dialing, setDialing] = useState(false);

  const handleDial = async () => {
    if (!number.trim() || dialing) return;
    setDialing(true);
    try {
      await dial(number.trim());
      setNumber("");
    } finally {
      setDialing(false);
    }
  };

  return (
    <div className="p-3 border-t border-gray-700">
      <div className="flex gap-2">
        <input
          type="text"
          value={number}
          onChange={(e) => setNumber(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleDial()}
          placeholder="Phone number..."
          className="flex-1 bg-surface-lighter border border-gray-600 rounded px-3 py-2 text-sm text-gray-100 placeholder-gray-500 focus:outline-none focus:border-accent-blue"
        />
        <button
          onClick={handleDial}
          disabled={!number.trim() || dialing}
          className="px-4 py-2 bg-accent-green hover:bg-green-600 disabled:bg-gray-600 disabled:cursor-not-allowed rounded text-sm font-medium transition-colors"
        >
          {dialing ? "..." : "Dial"}
        </button>
      </div>
    </div>
  );
}
