"use client";

import { Pencil, X, CornerDownRight, Loader2 } from "lucide-react";
import { agentIcon, prettyAgent } from "@/lib/icons";
import { cn } from "@/lib/cn";
import type { RunState } from "@/hooks/useRun";
import { StepBadge } from "./parts";

function paramSummary(parameters: Record<string, unknown>): string | null {
  const keys = Object.keys(parameters);
  if (keys.length === 0) return null;
  const k = keys[0];
  const v = parameters[k];
  const val =
    typeof v === "string" ? v : JSON.stringify(v ?? "");
  return `${k}: ${val.length > 40 ? val.slice(0, 40) + "…" : val}`;
}

// Detect {{stepN.field}} dependency in a step's params.
function dependencyLabel(parameters: Record<string, unknown>): string | null {
  const m = JSON.stringify(parameters).match(/\{\{\s*step(\d+)(?:\.([\w.]+))?/);
  if (!m) return null;
  return `uses step${m[1]}${m[2] ? "." + m[2] : ""}`;
}

export function PlanSteps({
  state,
  onApprove,
  onEdit,
  onRemove,
  headerless,
}: {
  state: RunState;
  onApprove: () => void;
  onEdit: () => void;
  onRemove: (index: number) => void;
  headerless?: boolean;
}) {
  if (state.steps.length === 0) return null;

  const running = state.phase === "running";
  const editable = state.phase === "ready";
  const runningCount = state.steps.filter((s) => s.status === "working").length;

  return (
    <div className="flex flex-col gap-2.5">
      {!headerless && (
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="text-[10px] font-semibold uppercase tracking-[0.08em] text-fg-3">
              Execution plan
            </span>
            <span className="font-mono text-[10px] text-fg-3">
              {state.steps.length} steps
              {running ? ` · ${runningCount} running` : ""}
            </span>
          </div>

          {editable && (
            <div className="flex items-center gap-1.5">
              <button
                onClick={onEdit}
                className="flex items-center gap-1.5 rounded-md border border-line px-2.5 py-1 text-[12px] font-medium text-fg-2 transition-colors hover:border-line-2 hover:text-fg"
              >
                <Pencil className="h-3 w-3" /> Cancel
              </button>
              <button
                onClick={onApprove}
                className="flex items-center gap-2 rounded-md bg-fg px-3 py-1 text-[12px] font-medium text-ink-0 transition-colors hover:brightness-110"
              >
                Approve
                <span className="rounded-[3px] border border-ink-0/15 bg-ink-0/10 px-1.5 py-px font-mono text-[10px] text-ink-0/60">
                  ⌘↵
                </span>
              </button>
            </div>
          )}
        </div>
      )}

      <div className="flex flex-col">
        {state.steps.map((step, i) => {
          const Icon = agentIcon(step.agent);
          const dep = i > 0 ? dependencyLabel(step.parameters) : null;
          const summary = paramSummary(step.parameters);
          return (
            <div key={i}>
              {i > 0 && (
                <div className="flex h-[22px] items-center gap-1.5 pl-[27px]">
                  <div className="h-full w-px bg-line" />
                  {dep && (
                    <span className="flex items-center gap-1.5 font-mono text-[10px] text-fg-3">
                      <CornerDownRight className="h-2.5 w-2.5 text-ink-4" />
                      {dep}
                    </span>
                  )}
                </div>
              )}

              <div
                className={cn(
                  "flex items-center gap-2.5 rounded-md border border-l-[3px] border-line border-l-ink-4 bg-ink-1 px-3 py-2.5 transition-colors",
                  step.status === "working" && "border-l-work bg-work/[0.08]",
                  step.status === "done" && "border-l-done",
                  step.status === "error" && "border-l-err"
                )}
              >
                <span className="w-4 flex-shrink-0 font-mono text-[10px] text-fg-3">
                  {String(i + 1).padStart(2, "0")}
                </span>
                <div
                  className={cn(
                    "flex h-6 w-6 flex-shrink-0 items-center justify-center rounded-[5px] border border-line bg-ink-2 text-fg-2",
                    step.status === "working" &&
                      "border-work/30 bg-work/[0.12] text-work-2",
                    step.status === "done" &&
                      "border-done/25 text-done-2"
                  )}
                >
                  <Icon className="h-3 w-3" />
                </div>
                <div className="min-w-0 flex-1">
                  <div className="text-[12px] font-semibold text-fg">
                    {prettyAgent(step.agent)}
                  </div>
                  <div className="mt-0.5 flex items-center gap-1.5 text-[11px] text-fg-2">
                    <span className="font-mono text-[10px] text-fg-3">
                      {step.action}
                    </span>
                    {summary && (
                      <code className="truncate rounded bg-ink-2 px-1.5 py-px font-mono text-[10px] text-fg-2">
                        {summary}
                      </code>
                    )}
                  </div>
                </div>

                {editable ? (
                  <button
                    onClick={() => onRemove(i)}
                    className="flex h-5 w-5 items-center justify-center rounded text-fg-3 transition-colors hover:bg-ink-2 hover:text-err-2"
                    title="Remove step"
                  >
                    <X className="h-3 w-3" />
                  </button>
                ) : step.status === "working" ? (
                  <Loader2 className="spin h-3.5 w-3.5 text-work-2" />
                ) : (
                  <StepBadge status={step.status} />
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
