import { cn } from "@/lib/cn";
import { SCOPE_LABEL } from "@/lib/icons";
import type { AgentScope, StepStatus } from "@/lib/types";

export function StatusDot({
  status,
  className,
}: {
  status: StepStatus | "idle";
  className?: string;
}) {
  return (
    <span
      className={cn(
        "h-1.5 w-1.5 flex-shrink-0 rounded-full",
        status === "idle" && "bg-ink-4",
        status === "pending" && "bg-ink-4",
        status === "working" && "pulse-dot bg-work",
        status === "done" && "bg-done",
        status === "error" && "bg-err",
        className
      )}
    />
  );
}

export function ScopeBadge({ scope }: { scope: AgentScope }) {
  return (
    <span
      className={cn(
        "rounded-[3px] border border-line bg-ink-3 px-1 py-px font-mono text-[9px] font-medium tracking-[0.03em]",
        scope === "workspace" && "text-fg-3",
        scope === "web" && "text-[#7DA0C4]",
        scope === "system" && "text-[#C4A77D]"
      )}
    >
      {SCOPE_LABEL[scope]}
    </span>
  );
}

export function StepBadge({ status }: { status: StepStatus }) {
  const label =
    status === "working"
      ? "running…"
      : status === "done"
      ? "done"
      : status === "error"
      ? "failed"
      : "queued";
  return (
    <span
      className={cn(
        "flex-shrink-0 rounded font-mono text-[10px] font-medium",
        "px-2 py-0.5",
        status === "working" && "bg-work/[0.12] text-work-2",
        status === "done" && "bg-done/[0.12] text-done-2",
        status === "error" && "bg-err/[0.12] text-err-2",
        status === "pending" && "bg-ink-2 text-fg-3"
      )}
    >
      {label}
    </span>
  );
}
