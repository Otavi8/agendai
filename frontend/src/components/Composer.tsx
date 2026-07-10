import { useState } from "react";
import type { KeyboardEvent } from "react";

export default function Composer({
  onSend,
  disabled,
}: {
  onSend: (text: string) => void;
  disabled: boolean;
}) {
  const [text, setText] = useState("");

  function submit() {
    const trimmed = text.trim();
    if (!trimmed || disabled) return;
    onSend(trimmed);
    setText("");
  }

  function onKeyDown(e: KeyboardEvent<HTMLTextAreaElement>) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      submit();
    }
  }

  return (
    <div className="flex items-end gap-2 border-t border-zinc-200 bg-white p-3">
      <textarea
        value={text}
        onChange={(e) => setText(e.target.value)}
        onKeyDown={onKeyDown}
        rows={1}
        placeholder="Pergunte ao AgendAI"
        className="max-h-40 flex-1 resize-none rounded-lg border border-zinc-300 bg-white px-4 py-3 text-sm text-zinc-950 outline-none focus:border-emerald-600"
      />
      <button
        onClick={submit}
        disabled={disabled || !text.trim()}
        className="rounded-lg bg-emerald-700 px-4 py-3 text-sm font-medium text-white hover:bg-emerald-800 disabled:opacity-50"
      >
        Enviar
      </button>
    </div>
  );
}
