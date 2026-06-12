"use client";

import { useRouter } from "next/navigation";
import { useQuery } from "@tanstack/react-query";
import { Loader2, ChevronRight, History } from "lucide-react";
import { apiFetch, withWorkspace } from "@/lib/api";
import { useWorkspaceId } from "@/hooks/useWorkspaceId";
import { DashShell } from "@/components/dash/DashShell";
import { ErrorBanner } from "@/components/dash/States";
import { cn } from "@/lib/cn";
import type { RunSummary } from "@/lib/types";

export default function RunsPage() {
  const workspaceId = useWorkspaceId();
  const router = useRouter();

  const { data, isLoading, isError, error } = useQuery({
    queryKey: ["runs", workspaceId],
    queryFn: () =>
      apiFetch<{ runs: RunSummary[]; total: number }>(
        withWorkspace("/api/runs?limit=50", workspaceId)
      ),
  });

  const runs = data?.runs ?? [];

  function ago(iso: string | null) {
    if (!iso) return "";
    const d = new Date(iso);
    const mins = Math.round((Date.now() - d.getTime()) / 60000);
    if (mins < 1) return "just now";
    if (mins < 60) return `${mins}m ago`;
    const hrs = Math.round(mins / 60);
    if (hrs < 24) return `${hrs}h ago`;
    return `${Math.round(hrs / 24)}d ago`;
  }

  return (
    <DashShell title="Run history" subtitle={data ? `${data.total} runs` : undefined}>
      {isError && (
        <div className="mb-4">
          <ErrorBanner error={error} />
        </div>
      )}
      {isLoading ? (
        <Loader2 className="spin h-4 w-4 text-fg-3" />
      ) : runs.length === 0 ? (
        <div className="flex flex-col items-center justify-center py-16 text-center">
          <History className="h-6 w-6 text-fg-3" />
          <p className="mt-3 text-[13px] text-fg-2">No runs yet.</p>
          <p className="mt-1 text-[12px] text-fg-3">
            Every command you run shows up here.
          </p>
        </div>
      ) : (
        <div className="flex flex-col gap-1.5">
          {runs.map((run) => (
            <button
              key={run.id}
              onClick={() => router.push(`/w/${workspaceId}/runs/${run.id}`)}
              className="group flex items-center gap-3 rounded-md border border-line bg-ink-1 px-3 py-2.5 text-left transition-colors hover:border-line-2"
            >
              <span
                className={cn(
                  "mt-0.5 h-1.5 w-1.5 flex-shrink-0 rounded-full",
                  run.status === "completed" && "bg-done",
                  run.status === "partial" && "bg-warn",
                  run.status === "error" && "bg-err"
                )}
              />
              <span className="min-w-0 flex-1">
                <span className="block truncate text-[13px] text-fg">
                  {run.message || "(no message)"}
                </span>
                <span className="mt-0.5 block font-mono text-[10px] text-fg-3">
                  {run.step_count ?? 0} steps · {run.status} · {ago(run.created_at)}
                </span>
              </span>
              <ChevronRight className="h-3.5 w-3.5 text-fg-3 opacity-0 transition-opacity group-hover:opacity-100" />
            </button>
          ))}
        </div>
      )}
    </DashShell>
  );
}
