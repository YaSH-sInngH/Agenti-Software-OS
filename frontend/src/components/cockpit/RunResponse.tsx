"use client";

import ReactMarkdown from "react-markdown";
import { Sparkles } from "lucide-react";

export function RunResponse({ text }: { text: string }) {
  return (
    <div className="rounded-lg border border-line bg-ink-1 p-4">
      <div className="mb-2.5 flex items-center gap-2">
        <Sparkles className="h-3.5 w-3.5 text-fg-2" />
        <span className="text-[11px] font-semibold uppercase tracking-[0.02em] text-fg-2">
          Response
        </span>
      </div>
      <div className="md-body text-[13px] leading-relaxed text-fg">
        <ReactMarkdown>{text}</ReactMarkdown>
      </div>
    </div>
  );
}
