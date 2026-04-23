import { useEffect, useState } from "react";
import { getLines, mergeLines } from "../../api/lines";
import { useStore } from "../../store";
import DialPad from "./DialPad";
import LineCard from "./LineCard";

export default function LinePanel() {
  const lines = useStore((s) => s.lines);
  const setLines = useStore((s) => s.setLines);
  const [selectedLines, setSelectedLines] = useState<string[]>([]);

  useEffect(() => {
    getLines().then(setLines);
  }, [setLines]);

  const lineList = Object.values(lines).filter(
    (l) => l.status !== "disconnected",
  );

  const toggleSelect = (id: string) => {
    setSelectedLines((prev) =>
      prev.includes(id) ? prev.filter((x) => x !== id) : [...prev, id],
    );
  };

  const handleMerge = async () => {
    if (selectedLines.length < 2) return;
    await mergeLines(selectedLines);
    setSelectedLines([]);
  };

  return (
    <div className="flex flex-col h-full">
      <div className="p-3 border-b border-gray-700">
        <h2 className="text-sm font-semibold text-gray-300 uppercase tracking-wider">
          Lines
        </h2>
      </div>

      <div className="flex-1 overflow-y-auto p-3 space-y-2">
        {lineList.length === 0 && (
          <div className="text-center text-gray-500 text-sm py-8">
            No active lines
          </div>
        )}
        {lineList.map((line) => (
          <LineCard
            key={line.line_id}
            line={line}
            selected={selectedLines.includes(line.line_id)}
            onSelect={() => toggleSelect(line.line_id)}
          />
        ))}
      </div>

      {selectedLines.length >= 2 && (
        <div className="p-3 border-t border-gray-700">
          <button
            onClick={handleMerge}
            className="w-full px-3 py-2 bg-accent-blue hover:bg-blue-600 rounded text-sm font-medium transition-colors"
          >
            Merge {selectedLines.length} Lines
          </button>
        </div>
      )}

      <DialPad />
    </div>
  );
}
