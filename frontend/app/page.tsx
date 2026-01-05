"use client";

import { useState } from "react";
import { useChat } from "@ai-sdk/react";
import { TextStreamChatTransport } from "ai";
import { HeaderBar } from "./components/HeaderBar";
import { EmptyState } from "./components/EmptyState";
import { MessageList } from "./components/MessageList";
import { ChatInput } from "./components/ChatInput";
import { ErrorBanner } from "./components/ErrorBanner";

export default function Home() {
  const [input, setInput] = useState("");

  const { messages, sendMessage, status, error } = useChat({
    transport: new TextStreamChatTransport({
      api: "http://localhost:8000/api/chat",
    }),
  });

  return (
    <div className="relative flex h-screen w-full flex-col bg-[var(--background)] bg-noise overflow-hidden">
      <HeaderBar />

      <main className="flex-1 overflow-y-auto px-4 py-6 sm:px-6 md:px-20 lg:px-60 scroll-smooth">
        <div className="flex flex-col gap-6 max-w-4xl mx-auto">
          {messages.length === 0 && (
            <EmptyState onSelectSuggestion={setInput} />
          )}

          <MessageList messages={messages} status={status} />

          {error && <ErrorBanner message={error.message} />}
        </div>
      </main>

      <footer className="px-4 pb-6 pt-4 bg-gradient-to-t from-[var(--background)] via-[var(--background)] to-transparent">
        <div className="max-w-4xl mx-auto">
          <ChatInput
            input={input}
            status={status}
            onChange={setInput}
            onSend={(text) => {
              sendMessage({ text });
              setInput("");
            }}
          />
          <div className="text-center mt-3">
            <p className="text-[10px] text-[var(--text-muted)] font-medium tracking-wide">
              Lowkey can make mistakes. Check important info.
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
}
