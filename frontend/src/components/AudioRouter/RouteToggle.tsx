interface Props {
  label: string;
  enabled: boolean;
  onToggle: () => void;
}

export default function RouteToggle({ label, enabled, onToggle }: Props) {
  return (
    <label className="flex items-center gap-2 cursor-pointer">
      <span className="text-xs text-gray-300 w-20 truncate" title={label}>
        {label}
      </span>
      <button
        onClick={onToggle}
        className={`w-8 h-4 rounded-full transition-colors relative flex-shrink-0 ${
          enabled ? "bg-accent-green" : "bg-gray-600"
        }`}
      >
        <span
          className={`absolute top-0.5 w-3 h-3 bg-white rounded-full transition-transform ${
            enabled ? "translate-x-4" : "translate-x-0.5"
          }`}
        />
      </button>
    </label>
  );
}
