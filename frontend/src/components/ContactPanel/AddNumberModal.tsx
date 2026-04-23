import { useState } from "react";
import { addNumber, assignNumber } from "../../api/contacts";
import type { ContactGroup } from "../../types";

interface Props {
  groups: ContactGroup[];
  onClose: () => void;
  onDone: () => void;
}

export default function AddNumberModal({ groups, onClose, onDone }: Props) {
  const [number, setNumber] = useState("");
  const [groupId, setGroupId] = useState<number | "">("");
  const [label, setLabel] = useState("");

  const handleSubmit = async () => {
    if (!number.trim()) return;
    await addNumber(
      number.trim(),
      groupId === "" ? undefined : groupId,
      label || undefined,
    );
    onDone();
    onClose();
  };

  return (
    <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-50">
      <div className="bg-surface-light border border-gray-700 rounded-lg p-5 w-96">
        <h3 className="text-lg font-semibold mb-4">Add Phone Number</h3>

        <input
          type="text"
          value={number}
          onChange={(e) => setNumber(e.target.value)}
          placeholder="Phone number"
          className="w-full bg-surface-lighter border border-gray-600 rounded px-3 py-2 text-sm mb-3 text-gray-100 placeholder-gray-500 focus:outline-none focus:border-accent-blue"
        />

        <input
          type="text"
          value={label}
          onChange={(e) => setLabel(e.target.value)}
          placeholder="Label (optional)"
          className="w-full bg-surface-lighter border border-gray-600 rounded px-3 py-2 text-sm mb-3 text-gray-100 placeholder-gray-500 focus:outline-none focus:border-accent-blue"
        />

        <select
          value={groupId}
          onChange={(e) =>
            setGroupId(e.target.value === "" ? "" : Number(e.target.value))
          }
          className="w-full bg-surface-lighter border border-gray-600 rounded px-3 py-2 text-sm mb-4 text-gray-100 focus:outline-none focus:border-accent-blue"
        >
          <option value="">No group</option>
          {groups.map((g) => (
            <option key={g.id} value={g.id}>
              {g.name}
            </option>
          ))}
        </select>

        <div className="flex gap-2 justify-end">
          <button
            onClick={onClose}
            className="px-4 py-2 text-sm text-gray-400 hover:text-gray-200 transition-colors"
          >
            Cancel
          </button>
          <button
            onClick={handleSubmit}
            disabled={!number.trim()}
            className="px-4 py-2 bg-accent-blue hover:bg-blue-600 disabled:bg-gray-600 rounded text-sm font-medium transition-colors"
          >
            Add
          </button>
        </div>
      </div>
    </div>
  );
}
