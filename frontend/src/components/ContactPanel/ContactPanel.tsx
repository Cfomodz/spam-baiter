import { useEffect, useState } from "react";
import { createGroup, getGroups } from "../../api/contacts";
import { useStore } from "../../store";
import AddNumberModal from "./AddNumberModal";
import ContactCard from "./ContactCard";

export default function ContactPanel() {
  const contacts = useStore((s) => s.contacts);
  const setContacts = useStore((s) => s.setContacts);
  const [showAddNumber, setShowAddNumber] = useState(false);
  const [newGroupName, setNewGroupName] = useState("");

  const refresh = () => {
    getGroups().then(setContacts);
  };

  useEffect(() => {
    refresh();
  }, []);

  const handleCreateGroup = async () => {
    if (!newGroupName.trim()) return;
    await createGroup(newGroupName.trim());
    setNewGroupName("");
    refresh();
  };

  return (
    <div className="flex items-center gap-3 px-4 py-2 overflow-x-auto">
      <div className="flex items-center gap-2 flex-shrink-0">
        <input
          type="text"
          value={newGroupName}
          onChange={(e) => setNewGroupName(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleCreateGroup()}
          placeholder="New group name..."
          className="bg-surface-lighter border border-gray-600 rounded px-2 py-1 text-xs text-gray-100 placeholder-gray-500 w-36 focus:outline-none focus:border-accent-blue"
        />
        <button
          onClick={handleCreateGroup}
          disabled={!newGroupName.trim()}
          className="px-2 py-1 bg-accent-blue hover:bg-blue-600 disabled:bg-gray-700 rounded text-xs font-medium transition-colors"
        >
          + Group
        </button>
        <button
          onClick={() => setShowAddNumber(true)}
          className="px-2 py-1 bg-surface-lighter border border-gray-600 rounded text-xs hover:border-gray-500 transition-colors"
        >
          + Number
        </button>
      </div>

      <div className="flex items-center gap-2 overflow-x-auto">
        {contacts.map((g) => (
          <div
            key={g.id}
            className="flex-shrink-0 bg-surface-light border border-gray-700 rounded px-3 py-1 text-xs"
          >
            <span className="font-medium">{g.name}</span>
            <span className="text-gray-500 ml-1">
              ({g.phone_numbers.length})
            </span>
          </div>
        ))}
      </div>

      {showAddNumber && (
        <AddNumberModal
          groups={contacts}
          onClose={() => setShowAddNumber(false)}
          onDone={refresh}
        />
      )}
    </div>
  );
}
