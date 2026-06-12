"use client";

import { Pencil, List, Workflow } from "lucide-react";
import { cn } from "@/lib/cn";
import type { RunState } from "@/hooks/useRun";
import { PlanSteps } from "./PlanSteps";
import { StepGraph } from "./StepGraph";

export type RunViewMode = "list" | "graph";

export function RunView({
  state,
  view,
  onView,
  editable,
  onApprove,
  onEdit,
  onRemove,
}: {
  state: RunState;
  view: RunViewMode;
  onView: (v: RunViewMode) => void;
  editable?: boolean;
  onApprove?: () => void;
  onEdit?: () => void;
  onRemove?: (index: number) => void;
}) {
  if (state.steps.length === 0) return null;

  const running = state.phase === "running";
  const runningCount = state.steps.filter((s) => s.status === "working").length;
  const isEditing = editable && state.phase === "ready";
  // Editing happens in the list; the graph is for live/replay viewing.
  const effectiveView: RunViewMode = isEditing ? "list" : view;

  return (
    <div className="flex flex-col gap-2.5">
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

        {isEditing ? (
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
        ) : (
          <div className="flex items-center gap-0.5 rounded-md border border-line bg-ink-1 p-0.5">
            <ToggleBtn
              active={effectiveView === "list"}
              onClick={() => onView("list")}
              icon={<List className="h-3 w-3" />}
              label="List"
            />
            <ToggleBtn
              active={effectiveView === "graph"}
              onClick={() => onView("graph")}
              icon={<Workflow className="h-3 w-3" />}
              label="Graph"
            />
          </div>
        )}
      </div>

      {effectiveView === "graph" ? (
        <StepGraph steps={state.steps} />
      ) : (
        <PlanSteps
          state={state}
          headerless
          onApprove={onApprove ?? (() => {})}
          onEdit={onEdit ?? (() => {})}
          onRemove={onRemove ?? (() => {})}
        />
      )}
    </div>
  );
}

function ToggleBtn({
  active,
  onClick,
  icon,
  label,
}: {
  active: boolean;
  onClick: () => void;
  icon: React.ReactNode;
  label: string;
}) {
  return (
    <button
      onClick={onClick}
      className={cn(
        "flex items-center gap-1.5 rounded px-2 py-1 text-[11px] font-medium transition-colors",
        active ? "bg-ink-3 text-fg" : "text-fg-3 hover:text-fg-2"
      )}
    >
      {icon}
      {label}
    </button>
  );
}
