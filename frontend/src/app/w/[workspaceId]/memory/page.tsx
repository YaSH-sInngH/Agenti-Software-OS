"use client";

import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Plus, X, Loader2, Brain } from "lucide-react";
import { apiFetch, withWorkspace } from "@/lib/api";
import { useWorkspaceId } from "@/hooks/useWorkspaceId";
import { DashShell } from "@/components/dash/DashShell";
import { ErrorBanner } from "@/components/dash/States";
import type { Memory } from "@/lib/types";

const TYPES = ["user_memory", "project_memory", "workspace_memory"];

export default function MemoryPage() {
  const workspaceId = useWorkspaceId();
  const qc = useQueryClient();
  const [text, setText] = useState("");
  const [type, setType] = useState(TYPES[0]);

  const { data, isLoading, isError, error } = useQuery({
    queryKey: ["memories", workspaceId],
    queryFn: () =>
      apiFetch<{ memories: Memory[] }>(
        withWorkspace("/api/memories", workspaceId)
      ),
  });

  const invalidate = () =>
    qc.invalidateQueries({ queryKey: ["memories", workspaceId] });

  const addMut = useMutation({
    mutationFn: () =>
      apiFetch("/api/agents/memory_agent/run", {
        method: "POST",
        body: {
          action: "store_memory",
          parameters: { memory: text, memory_type: type },
          workspace_id: workspaceId,
        },
      }),
    onSuccess: () => {
      setText("");
      invalidate();
    },
  });

  const deleteMut = useMutation({
    mutationFn: (id: number) =>
      apiFetch(withWorkspace(`/api/memories/${id}`, workspaceId), {
        method: "DELETE",
      }),
    onSuccess: invalidate,
  });

  const memories = data?.memories ?? [];
  const grouped = TYPES.map((t) => ({
    type: t,
    items: memories.filter((m) => m.type === t),
  })).filter((g) => g.items.length > 0);

  // include any other types not in the canonical list
  const otherTypes = memories.filter((m) => !TYPES.includes(m.type));
  if (otherTypes.length) grouped.push({ type: "other", items: otherTypes });

  return (
    <DashShell title="Memory" subtitle={`${memories.length} stored`}>
      {isError && (
        <div className="mb-4">
          <ErrorBanner error={error} />
        </div>
      )}
      <form
        onSubmit={(e) => {
          e.preventDefault();
          if (text.trim()) addMut.mutate();
        }}
        className="mb-6 flex items-center gap-2"
      >
        <input
          value={text}
          onChange={(e) => setText(e.target.value)}
          placeholder="Remember that…"
          className="h-9 flex-1 rounded-md border border-line bg-ink-1 px-3 text-[13px] text-fg outline-none placeholder:text-fg-3 focus:border-line-2"
        />
        <select
          value={type}
          onChange={(e) => setType(e.target.value)}
          className="h-9 rounded-md border border-line bg-ink-1 px-2 text-[12px] text-fg-2 outline-none focus:border-line-2"
        >
          {TYPES.map((t) => (
            <option key={t} value={t}>
              {t.replace("_memory", "")}
            </option>
          ))}
        </select>
        <button
          type="submit"
          disabled={!text.trim() || addMut.isPending}
          className="flex h-9 items-center gap-1.5 rounded-md bg-fg px-3 text-[12px] font-medium text-ink-0 hover:brightness-110 disabled:opacity-50"
        >
          {addMut.isPending ? (
            <Loader2 className="spin h-3.5 w-3.5" />
          ) : (
            <Plus className="h-3.5 w-3.5" />
          )}
          Store
        </button>
      </form>

      {isLoading ? (
        <Loader2 className="spin h-4 w-4 text-fg-3" />
      ) : memories.length === 0 ? (
        <div className="flex flex-col items-center justify-center py-16 text-center">
          <Brain className="h-6 w-6 text-fg-3" />
          <p className="mt-3 text-[13px] text-fg-2">No memories yet.</p>
        </div>
      ) : (
        <div className="flex flex-col gap-5">
          {grouped.map((g) => (
            <div key={g.type}>
              <div className="mb-2 text-[10px] font-semibold uppercase tracking-[0.08em] text-fg-3">
                {g.type.replace("_memory", "")}
              </div>
              <div className="flex flex-wrap gap-2">
                {g.items.map((m) => (
                  <div
                    key={m.id}
                    className="group flex items-center gap-2 rounded-full border border-line bg-ink-1 py-1 pl-3 pr-1.5 text-[12px] text-fg"
                  >
                    <span>{m.text}</span>
                    <button
                      onClick={() => deleteMut.mutate(m.id)}
                      className="flex h-4 w-4 items-center justify-center rounded-full text-fg-3 transition-colors hover:bg-ink-3 hover:text-err-2"
                    >
                      <X className="h-3 w-3" />
                    </button>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}
    </DashShell>
  );
}
