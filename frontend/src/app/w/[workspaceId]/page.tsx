"use client";

import { useEffect, useMemo, useState } from "react";
import { useParams } from "next/navigation";
import { useRun } from "@/hooks/useRun";
import { useUi } from "@/stores/ui";
import { AgentRoster } from "@/components/cockpit/AgentRoster";
import { CommandBar } from "@/components/cockpit/CommandBar";
import { RunView, type RunViewMode } from "@/components/cockpit/RunView";
import { ResultCard } from "@/components/cockpit/ResultCard";
import { RunResponse } from "@/components/cockpit/RunResponse";
import type { StepStatus } from "@/lib/types";

const RANK: Record<StepStatus | "idle", number> = {
  idle: 0,
  pending: 1,
  done: 2,
  error: 3,
  working: 4,
};

export default function CockpitPage() {
  const params = useParams<{ workspaceId: string }>();
  const workspaceId = Number(params.workspaceId);
  const { state, preview, run, approve, reset, removeStep } = useRun(workspaceId);
  const [input, setInput] = useState("");
  const [view, setView] = useState<RunViewMode>("list");
  const setActiveCount = useUi((s) => s.setActiveCount);

  const { statusMap, activeAction, activeCount } = useMemo(() => {
    const statusMap: Record<string, StepStatus | "idle"> = {};
    const activeAction: Record<string, string> = {};
    let activeCount = 0;
    for (const s of state.steps) {
      const prev = statusMap[s.agent];
      if (!prev || RANK[s.status] >= RANK[prev]) statusMap[s.agent] = s.status;
      if (s.status === "working") {
        activeAction[s.agent] = s.action;
        activeCount += 1;
      }
    }
    return { statusMap, activeAction, activeCount };
  }, [state.steps]);

  useEffect(() => {
    setActiveCount(activeCount);
    return () => setActiveCount(0);
  }, [activeCount, setActiveCount]);

  const busy = state.phase === "planning" || state.phase === "running";
  const results = state.results.filter(Boolean);
  const showEmpty = state.phase === "idle";

  return (
    <>
      <AgentRoster
        workspaceId={workspaceId}
        statusMap={statusMap}
        activeAction={activeAction}
      />

      <main className="flex flex-1 flex-col overflow-hidden">
        <CommandBar
          value={input}
          onChange={setInput}
          onRun={() => run(input)}
          onPreview={() => preview(input)}
          busy={busy}
        />

        <div className="flex flex-1 flex-col gap-3.5 overflow-y-auto px-5 py-4">
          {state.phase === "planning" && state.steps.length === 0 && (
            <div className="font-mono text-[12px] text-fg-3">Planning…</div>
          )}

          {state.error && (
            <div className="rounded-lg border border-err/25 bg-err/10 px-3.5 py-2.5 text-[12px] text-err-2">
              {state.error}
            </div>
          )}

          <RunView
            state={state}
            view={view}
            onView={setView}
            editable
            onApprove={approve}
            onEdit={reset}
            onRemove={removeStep}
          />

          {results.map((res, i) =>
            res ? (
              <ResultCard key={i} result={res} workspaceId={workspaceId} />
            ) : null
          )}

          {state.response && <RunResponse text={state.response} />}

          {showEmpty && (
            <div className="flex flex-1 flex-col items-center justify-center text-center">
              <p className="text-[13px] text-fg-2">
                Type a command to plan a run.
              </p>
              <p className="mt-1 text-[12px] text-fg-3">
                e.g. “Index my workspace and summarize the documents”
              </p>
            </div>
          )}
        </div>
      </main>
    </>
  );
}
