import type { Message } from "../lib/types";

export default function MessageBubble({ message, pending }: { message: Message; pending?: boolean }) {
  const isUser = message.role === "user";

  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"}`}>
      <div
        className={`max-w-[80%] whitespace-pre-wrap rounded-lg px-4 py-2 text-sm leading-relaxed ${
          isUser
            ? "bg-emerald-700 text-white"
            : "border border-zinc-200 bg-white text-zinc-900 shadow-sm"
        }`}
      >
        {message.content || (pending ? <TypingDots /> : "")}
      </div>
    </div>
  );
}

function TypingDots() {
  return (
    <span className="inline-flex gap-1 align-middle">
      <span className="h-2 w-2 animate-bounce rounded-full bg-zinc-400 [animation-delay:-0.3s]" />
      <span className="h-2 w-2 animate-bounce rounded-full bg-zinc-400 [animation-delay:-0.15s]" />
      <span className="h-2 w-2 animate-bounce rounded-full bg-zinc-400" />
    </span>
  );
}
