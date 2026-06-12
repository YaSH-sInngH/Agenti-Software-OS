"use client";

import { Folder, Loader2 } from "lucide-react";

export function CommandBar({
  value,
  onChange,
  onRun,
  onPreview,
  busy,
}: {
  value: string;
  onChange: (v: string) => void;
  onRun: () => void;
  onPreview: () => void;
  busy: boolean;
}) {
  function onKeyDown(e: React.KeyboardEvent) {
    if ((e.metaKey || e.ctrlKey) && e.key === "Enter") {
      e.preventDefault();
      if (value.trim() && !busy) onRun();
    }
  }

  return (
    <div className="flex-shrink-0 border-b border-line bg-ink-1 px-5 pb-3 pt-3.5">
      <div className="flex items-center gap-2.5">
        <div className="flex h-11 flex-1 items-center gap-2.5 rounded-lg border border-line-2 bg-ink-0 px-3.5 focus-within:border-[#444]">
          <span className="flex h-5 w-5 flex-shrink-0 items-center justify-center rounded bg-ink-2 text-fg-3">
            {busy ? (
              <Loader2 className="spin h-3 w-3" />
            ) : (
              <Folder className="h-3 w-3" />
            )}
          </span>
          <input
            value={value}
            onChange={(e) => onChange(e.target.value)}
            onKeyDown={onKeyDown}
            disabled={busy}
            placeholder="What do you want to do?"
            className="flex-1 bg-transparent text-[14px] text-fg outline-none placeholder:text-fg-3 disabled:opacity-60"
          />
        </div>

        <button
          onClick={onPreview}
          disabled={!value.trim() || busy}
          className="h-9 rounded-md border border-line px-3 text-[12px] font-medium text-fg-2 transition-colors hover:border-line-2 hover:text-fg disabled:opacity-40"
        >
          Preview
        </button>
        <button
          onClick={onRun}
          disabled={!value.trim() || busy}
          className="flex h-9 items-center gap-2 rounded-md bg-fg px-3 text-[12px] font-medium text-ink-0 transition-colors hover:brightness-110 disabled:opacity-40"
        >
          Run
          <span className="rounded-[3px] border border-ink-0/15 bg-ink-0/10 px-1.5 py-px font-mono text-[10px] text-ink-0/60">
            ⌘↵
          </span>
        </button>
      </div>
    </div>
  );
}
