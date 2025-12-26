"use client";

import { useState } from "react";
import { useChat } from "@ai-sdk/react";
import { TextStreamChatTransport } from "ai";

export default function Home() {
  const [input, setInput] = useState("");

  const { messages, sendMessage, status, error } = useChat({
    // IMPORTANT: point directly at FastAPI (not a Next.js API route)
    transport: new TextStreamChatTransport({
      api: "http://localhost:8000/api/chat",
    }),
  });

  return (
    <main className="mx-auto flex w-full max-w-2xl flex-col gap-4 px-4 py-8">
      <header className="flex flex-col gap-1">
        <h1 className="text-2xl font-semibold">Lowkey</h1>
        <p className="text-sm opacity-70">
          Reddit-powered travel recs (UI wired to FastAPI).
        </p>
      </header>

      <section className="flex flex-col gap-3 rounded-lg border p-4">
        {messages.length === 0 ? (
          <div className="text-sm opacity-70">
            Ask something like: “3 days in Tokyo for food + thrift stores”.
          </div>
        ) : null}

        {messages.map((message) => (
          <div key={message.id} className="whitespace-pre-wrap">
            <div className="text-xs opacity-60">
              {message.role === "user" ? "You" : "Lowkey"}
            </div>

            <div className="mt-1">
              {message.parts.map((part, i) => {
                if (part.type === "text") {
                  return <span key={`${message.id}-${i}`}>{part.text}</span>;
                }
                return null; // ignore non-text parts for now
              })}
            </div>
          </div>
        ))}

        {error ? (
          <div className="text-sm text-red-600">Error: {error.message}</div>
        ) : null}
      </section>

      <form
        className="flex gap-2"
        onSubmit={(e) => {
          e.preventDefault();

          const text = input.trim();
          if (!text) return;

          // TextStreamChatTransport expects plain text input like this:
          sendMessage({ text });
          setInput("");
        }}
      >
        <input
          className="flex-1 rounded-md border px-3 py-2"
          value={input}
          placeholder={
            status === "streaming" ? "Lowkey is typing…" : "Type a message…"
          }
          onChange={(e) => setInput(e.currentTarget.value)}
        />
        <button
          className="rounded-md border px-3 py-2"
          type="submit"
          disabled={status === "streaming"}
        >
          Send
        </button>
      </form>
    </main>
  );
}
