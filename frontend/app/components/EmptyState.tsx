type EmptyStateProps = {
  onSelectSuggestion: (text: string) => void;
};

export function EmptyState({ onSelectSuggestion }: EmptyStateProps) {
  const suggestions = [
    "tokyo hidden gems",
    "underrated beaches",
    "best street food",
  ];

  return (
    <div className="flex flex-col items-center justify-center h-[60vh] text-center gap-4">
      <div className="text-6xl">🌍</div>
      <h2 className="text-xl font-semibold text-[var(--text-primary)]">
        hey! where are we exploring today?
      </h2>
      <p className="text-sm text-[var(--text-muted)] max-w-md">
        ask me anything about travel - hidden gems, local spots, underrated
        destinations
      </p>
      <div className="flex flex-wrap gap-2 mt-4 justify-center">
        {suggestions.map((suggestion) => (
          <button
            key={suggestion}
            onClick={() => onSelectSuggestion(suggestion)}
            className="px-4 py-2 rounded-full bg-[var(--surface)] border border-[var(--surface-border)] text-sm text-[var(--text-secondary)] hover:border-[var(--primary)]/50 hover:text-[var(--primary)] transition-colors"
          >
            {suggestion}
          </button>
        ))}
      </div>
    </div>
  );
}
