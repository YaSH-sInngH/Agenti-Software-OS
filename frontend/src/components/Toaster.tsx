"use client";

import { Loader2, X } from "lucide-react";
import { useToasts } from "@/stores/toast";
import { cn } from "@/lib/cn";

export function Toaster() {
  const toasts = useToasts((s) => s.toasts);
  const dismiss = useToasts((s) => s.dismiss);

  if (toasts.length === 0) return null;

  return (
    <div className="fixed bottom-4 right-4 z-[60] flex flex-col gap-1.5">
      {toasts.map((t) => (
        <div
          key={t.id}
          className="flex min-w-[240px] items-center gap-2.5 rounded-lg border border-line-2 bg-ink-2 px-3.5 py-2.5 text-[12px] text-fg shadow-xl shadow-black/50"
        >
          {t.kind === "working" ? (
            <Loader2 className="spin h-3 w-3 flex-shrink-0 text-work-2" />
          ) : (
            <span
              className={cn(
                "h-1.5 w-1.5 flex-shrink-0 rounded-full",
                t.kind === "success" && "bg-done",
                t.kind === "error" && "bg-err",
                t.kind === "info" && "bg-fg-3"
              )}
            />
          )}
          <span className="flex-1">{t.message}</span>
          <button
            onClick={() => dismiss(t.id)}
            className="flex h-4 w-4 items-center justify-center rounded text-fg-3 transition-colors hover:text-fg"
          >
            <X className="h-3 w-3" />
          </button>
        </div>
      ))}
    </div>
  );
}
