import ReactMarkdown from "react-markdown";
import type { UIMessage } from "ai";

type MessageListProps = {
  messages: UIMessage[];
  status: string;
};

export function MessageList({ messages, status }: MessageListProps) {
  return (
    <>
      {messages.map((message) => (
        <div
          key={message.id}
          className={`flex items-end gap-3 ${
            message.role === "user" ? "justify-end" : "justify-start"
          }`}
        >
          {message.role === "assistant" && (
            <div className="hidden sm:flex shrink-0 items-center justify-center w-10 h-10 rounded-full bg-[var(--forest)] border border-[var(--forest-border)] text-[var(--primary)] shadow-lg">
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
                  d="M3.055 11H5a2 2 0 012 2v1a2 2 0 002 2 2 2 0 012 2v2.945M8 3.935V5.5A2.5 2.5 0 0010.5 8h.5a2 2 0 012 2 2 2 0 104 0 2 2 0 012-2h1.064M15 20.488V18a2 2 0 012-2h3.064M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                />
              </svg>
            </div>
          )}

          <div
            className={`flex flex-col gap-1 max-w-[85%] sm:max-w-[70%] ${
              message.role === "user" ? "items-end" : "items-start"
            }`}
          >
            <div
              className={`relative px-5 py-4 shadow-lg ${
                message.role === "user"
                  ? "rounded-[1.5rem] rounded-tr-sm bg-[var(--clay)] border-2 border-[var(--clay-border)] text-white"
                  : "rounded-[1.5rem] rounded-tl-sm bg-[var(--forest)] border-2 border-[var(--forest-border)] text-gray-100 prose-lowkey"
              } ${
                status === "streaming" &&
                message.role === "assistant" &&
                message === messages[messages.length - 1]
                  ? "streaming-cursor"
                  : ""
              }`}
              style={{ fontFamily: "Noto Sans, sans-serif" }}
            >
              {message.parts.map((part, i) => {
                if (part.type === "text") {
                  return message.role === "user" ? (
                    <span key={`${message.id}-${i}`}>{part.text}</span>
                  ) : (
                    <ReactMarkdown key={`${message.id}-${i}`}>
                      {part.text}
                    </ReactMarkdown>
                  );
                }
                return null;
              })}
            </div>
            <span
              className={`text-xs text-[var(--text-muted)] font-medium ${
                message.role === "user" ? "pr-2" : "pl-2"
              }`}
            >
              {message.role === "user" ? "You" : "Lowkey"} · just now
            </span>
          </div>
        </div>
      ))}
    </>
  );
}
