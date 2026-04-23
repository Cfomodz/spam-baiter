interface Props {
  value: string;
  onChange: (value: string) => void;
  onGenerate: () => void;
  generating: boolean;
  disabled: boolean;
}

export default function TextInput({
  value,
  onChange,
  onGenerate,
  generating,
  disabled,
}: Props) {
  return (
    <div className="flex flex-col gap-2">
      <textarea
        value={value}
        onChange={(e) => onChange(e.target.value)}
        onKeyDown={(e) => {
          if (e.key === "Enter" && e.ctrlKey) onGenerate();
        }}
        placeholder="Type text to generate speech..."
        rows={4}
        className="w-full bg-surface-lighter border border-gray-600 rounded px-3 py-2 text-sm text-gray-100 placeholder-gray-500 resize-none focus:outline-none focus:border-accent-blue"
      />
      <button
        onClick={onGenerate}
        disabled={disabled || generating || !value.trim()}
        className="w-full px-4 py-2 bg-purple-600 hover:bg-purple-700 disabled:bg-gray-600 disabled:cursor-not-allowed rounded text-sm font-medium transition-colors"
      >
        {generating ? "Generating..." : "Generate Speech"}
      </button>
      <span className="text-xs text-gray-500">Ctrl+Enter to generate</span>
    </div>
  );
}
