"use client";

import { useCallback, useRef, useState } from "react";
import { apiFetch } from "@/lib/api";
import { streamChat, streamRun, type SSEMessage } from "@/lib/sse";
import type { PlanResponse, Step, StepResult, StepStatus } from "@/lib/types";

export interface RunStep extends Step {
  status: StepStatus;
}

export type RunPhase =
  | "idle"
  | "planning"
  | "ready"
  | "running"
  | "done"
  | "error";

export interface RunState {
  phase: RunPhase;
  message: string;
  steps: RunStep[];
  results: (StepResult | null)[];
  response: string | null;
  error: string | null;
  runId: number | null;
}

const INITIAL: RunState = {
  phase: "idle",
  message: "",
  steps: [],
  results: [],
  response: null,
  error: null,
  runId: null,
};

function errMessage(e: unknown): string {
  return e instanceof Error ? e.message : "Something went wrong";
}

interface StepDoneData {
  index: number;
  agent: string;
  action: string;
  result: StepResult["result"];
}

export function useRun(workspaceId: number) {
  const [state, setState] = useState<RunState>(INITIAL);
  const stateRef = useRef<RunState>(INITIAL);
  const abortRef = useRef<AbortController | null>(null);

  const set = useCallback(
    (updater: RunState | ((prev: RunState) => RunState)) => {
      setState((prev) => {
        const next =
          typeof updater === "function"
            ? (updater as (p: RunState) => RunState)(prev)
            : updater;
        stateRef.current = next;
        return next;
      });
    },
    []
  );

  const reset = useCallback(() => {
    abortRef.current?.abort();
    set(INITIAL);
  }, [set]);

  // Plan only — preview steps without executing.
  const preview = useCallback(
    async (message: string) => {
      set({ ...INITIAL, phase: "planning", message });
      try {
        const data = await apiFetch<PlanResponse>("/api/plan", {
          method: "POST",
          body: { message, workspace_id: workspaceId },
        });
        const steps: RunStep[] = data.steps.map((s) => ({
          ...s,
          status: "pending",
        }));
        set({
          phase: "ready",
          message,
          steps,
          results: steps.map(() => null),
          response: null,
          error: null,
          runId: null,
        });
      } catch (e) {
        set({ ...INITIAL, phase: "error", message, error: errMessage(e) });
      }
    },
    [set, workspaceId]
  );

  // Shared SSE event handler for both live-run and approve-run streams.
  const makeHandler = useCallback(
    (ac: AbortController) => ({
      signal: ac.signal,
      onEvent: ({ event, data }: SSEMessage) => {
        const d = data as Record<string, unknown>;
        if (event === "plan_ready") {
          const steps: RunStep[] = ((d.steps as Step[]) ?? []).map((s) => ({
            ...s,
            status: "pending" as StepStatus,
          }));
          set((prev) => ({
            ...prev,
            phase: "running",
            steps,
            results: steps.map(() => null),
          }));
        } else if (event === "step_started") {
          const idx = d.index as number;
          set((prev) => ({
            ...prev,
            steps: prev.steps.map((st, i) =>
              i === idx ? { ...st, status: "working" } : st
            ),
          }));
        } else if (event === "step_done") {
          const dd = data as unknown as StepDoneData;
          const ok = dd.result?.success !== false;
          set((prev) => {
            const steps = prev.steps.map((st, i) =>
              i === dd.index
                ? { ...st, status: (ok ? "done" : "error") as StepStatus }
                : st
            );
            const results = [...prev.results];
            results[dd.index] = {
              agent: dd.agent,
              action: dd.action,
              result: dd.result,
            };
            return { ...prev, steps, results };
          });
        } else if (event === "final_response") {
          set((prev) => ({
            ...prev,
            response: (d.response as string) ?? prev.response,
            runId: (d.run_id as number) ?? prev.runId,
            // Authoritative full results from the server (same as run history),
            // so the cockpit always renders every agent's output.
            results: Array.isArray(d.results)
              ? (d.results as StepResult[])
              : prev.results,
          }));
        } else if (event === "done") {
          set((prev) => ({
            ...prev,
            phase: "done",
            runId: (d.run_id as number) ?? prev.runId,
          }));
        }
      },
    }),
    [set]
  );

  // Live SSE run — plans and executes, streaming each step.
  const run = useCallback(
    async (message: string) => {
      abortRef.current?.abort();
      const ac = new AbortController();
      abortRef.current = ac;
      set({ ...INITIAL, phase: "planning", message });
      try {
        await streamChat({ message, workspace_id: workspaceId }, makeHandler(ac));
      } catch (e) {
        if (ac.signal.aborted) return;
        set((prev) => ({ ...prev, phase: "error", error: errMessage(e) }));
      }
    },
    [set, workspaceId, makeHandler]
  );

  // Approve previewed steps — stream execution of the exact (edited) steps.
  const approve = useCallback(async () => {
    abortRef.current?.abort();
    const ac = new AbortController();
    abortRef.current = ac;
    const cur = stateRef.current;
    const bareSteps: Step[] = cur.steps.map(({ status: _status, ...rest }) => rest);
    set((prev) => ({ ...prev, phase: "running" }));
    try {
      await streamRun(
        { steps: bareSteps, message: cur.message, workspace_id: workspaceId },
        makeHandler(ac)
      );
    } catch (e) {
      if (ac.signal.aborted) return;
      set((prev) => ({ ...prev, phase: "error", error: errMessage(e) }));
    }
  }, [set, workspaceId, makeHandler]);

  const removeStep = useCallback(
    (index: number) => {
      set((prev) => {
        if (prev.phase !== "ready") return prev;
        return {
          ...prev,
          steps: prev.steps.filter((_, i) => i !== index),
          results: prev.results.filter((_, i) => i !== index),
        };
      });
    },
    [set]
  );

  return { state, preview, run, approve, reset, removeStep };
}
