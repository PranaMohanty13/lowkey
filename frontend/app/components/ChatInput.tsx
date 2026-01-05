type ChatInputProps = {
  input: string;
  status: string;
  onChange: (value: string) => void;
  onSend: (text: string) => void;
};

export function ChatInput({ input, status, onChange, onSend }: ChatInputProps) {
  return (
    <form
      onSubmit={(e) => {
        e.preventDefault();
        const text = input.trim();
        if (!text || status === "streaming") return;
        onSend(text);
      }}
      className="relative flex items-center gap-2 p-2 rounded-full bg-[var(--surface)]/80 border border-[var(--surface-border)] shadow-2xl backdrop-blur-md focus-within:border-[var(--primary)]/50 transition-all duration-300"
    >
      <input
        className="flex-1 bg-transparent border-none text-white placeholder-[var(--text-muted)] focus:ring-0 focus:outline-none text-base h-10 px-4"
        style={{ fontFamily: "Noto Sans, sans-serif" }}
        value={input}
        placeholder={
          status === "streaming" ? "lowkey is typing..." : "ask for the vibe..."
        }
        onChange={(e) => onChange(e.currentTarget.value)}
      />
      <button
        type="submit"
        disabled={status === "streaming" || !input.trim()}
        className="flex items-center justify-center w-12 h-12 rounded-full bg-[var(--primary)] text-white shadow-[0_0_10px_var(--primary-glow)] hover:opacity-90 hover:scale-105 active:scale-95 transition-all disabled:opacity-50 disabled:cursor-not-allowed mr-1"
      >
        <svg
          className="w-5 h-5"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
          strokeWidth={2}
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"
          />
        </svg>
      </button>
    </form>
  );
}
