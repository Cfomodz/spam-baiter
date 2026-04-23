import { deleteGroup, deleteNumber } from "../../api/contacts";
import type { ContactGroup } from "../../types";

interface Props {
  group: ContactGroup;
  onRefresh: () => void;
}

export default function ContactCard({ group, onRefresh }: Props) {
  return (
    <div className="bg-surface-light border border-gray-700 rounded-lg p-3">
      <div className="flex items-center justify-between mb-2">
        <h3 className="text-sm font-semibold">{group.name}</h3>
        <button
          onClick={async () => {
            await deleteGroup(group.id);
            onRefresh();
          }}
          className="text-xs text-gray-500 hover:text-accent-red transition-colors"
        >
          Delete
        </button>
      </div>

      {group.notes && (
        <p className="text-xs text-gray-400 mb-2">{group.notes}</p>
      )}

      <div className="space-y-1">
        {group.phone_numbers.map((pn) => (
          <div
            key={pn.id}
            className="flex items-center justify-between text-xs bg-surface-lighter rounded px-2 py-1"
          >
            <span>
              <span className="text-accent-blue">
                #{pn.sequence_num ?? "?"}
              </span>{" "}
              {pn.number}
              {pn.label && (
                <span className="text-gray-500 ml-1">({pn.label})</span>
              )}
            </span>
            <button
              onClick={async () => {
                await deleteNumber(pn.id);
                onRefresh();
              }}
              className="text-gray-600 hover:text-accent-red transition-colors ml-2"
            >
              x
            </button>
          </div>
        ))}
        {group.phone_numbers.length === 0 && (
          <div className="text-xs text-gray-500">No numbers yet</div>
        )}
      </div>
    </div>
  );
}
