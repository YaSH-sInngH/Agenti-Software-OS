"use client";

import { useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { useQuery } from "@tanstack/react-query";
import { ArrowLeft, Loader2 } from "lucide-react";
import { apiFetch, withWorkspace } from "@/lib/api";
import { useWorkspaceId } from "@/hooks/useWorkspaceId";
import { DashShell } from "@/components/dash/DashShell";
import { RunView, type RunViewMode } from "@/components/cockpit/RunView";
import { ResultCard } from "@/components/cockpit/ResultCard";
import { RunResponse } from "@/components/cockpit/RunResponse";
import type { RunState, RunStep } from "@/hooks/useRun";
import type { RunDetail } from "@/lib/types";

export default function RunDetailPage() {
  const workspaceId = useWorkspaceId();
  const router = useRouter();
  const params = useParams<{ runId: string }>();
  const runId = Number(params.runId);
  const [view, setView] = useState<RunViewMode>("list");

  const { data, isLoading } = useQuery({
    queryKey: ["run", workspaceId, runId],
    queryFn: () =>
      apiFetch<RunDetail>(withWorkspace(`/api/runs/${runId}`, workspaceId)),
  });

  const plan = data?.plan ?? [];
  const results = data?.results ?? [];

  const steps: RunStep[] = plan.map((s, i) => ({
    ...s,
    status: results[i]?.result?.success === false ? "error" : "done",
  }));

  const replayState: RunState = {
    phase: "done",
    message: data?.message ?? "",
    steps,
    results,
    response: data?.response ?? null,
    error: null,
    runId,
  };

  return (
    <DashShell
      title="Run"
      subtitle={data ? `#${data.id} · ${data.status}` : undefined}
      actions={
        <button
          onClick={() => router.push(`/w/${workspaceId}/runs`)}
          className="flex items-center gap-1.5 rounded-md border border-line px-2.5 py-1 text-[12px] text-fg-2 transition-colors hover:border-line-2 hover:text-fg"
        >
          <ArrowLeft className="h-3 w-3" /> History
        </button>
      }
    >
      {isLoading ? (
        <Loader2 className="spin h-4 w-4 text-fg-3" />
      ) : !data ? (
        <p className="text-[13px] text-fg-3">Run not found.</p>
      ) : (
        <div className="flex flex-col gap-3.5">
          <div className="rounded-lg border border-line bg-ink-1 px-3.5 py-2.5">
            <div className="text-[10px] font-semibold uppercase tracking-[0.08em] text-fg-3">
              Command
            </div>
            <div className="mt-1 text-[13px] text-fg">{data.message}</div>
          </div>

          {steps.length > 0 && (
            <RunView state={replayState} view={view} onView={setView} />
          )}

          {results.map((res, i) =>
            res ? (
              <ResultCard key={i} result={res} workspaceId={workspaceId} />
            ) : null
          )}

          {data.response && <RunResponse text={data.response} />}
        </div>
      )}
    </DashShell>
  );
}
