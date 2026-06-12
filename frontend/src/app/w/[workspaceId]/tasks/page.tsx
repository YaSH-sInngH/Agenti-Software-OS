"use client";

import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Check, Plus, Trash2, Loader2 } from "lucide-react";
import { apiFetch, withWorkspace } from "@/lib/api";
import { useWorkspaceId } from "@/hooks/useWorkspaceId";
import { DashShell } from "@/components/dash/DashShell";
import { ErrorBanner } from "@/components/dash/States";
import { cn } from "@/lib/cn";
import type { Task } from "@/lib/types";

type Filter = "all" | "pending" | "completed";

export default function TasksPage() {
  const workspaceId = useWorkspaceId();
  const qc = useQueryClient();
  const [filter, setFilter] = useState<Filter>("all");
  const [title, setTitle] = useState("");
  const [due, setDue] = useState("");

  const key = ["tasks", workspaceId, filter];
  const { data, isLoading, isError, error } = useQuery({
    queryKey: key,
    queryFn: () =>
      apiFetch<{ tasks: Task[]; total: number }>(
        withWorkspace(
          `/api/tasks${filter === "all" ? "" : `?status=${filter}`}`,
          workspaceId
        )
      ),
  });

  const invalidate = () =>
    qc.invalidateQueries({ queryKey: ["tasks", workspaceId] });

  const createMut = useMutation({
    mutationFn: () =>
      apiFetch(withWorkspace("/api/tasks", workspaceId), {
        method: "POST",
        body: { title, due_date: due || undefined },
      }),
    onSuccess: () => {
      setTitle("");
      setDue("");
      invalidate();
    },
  });

  const toggleMut = useMutation({
    mutationFn: (t: Task) =>
      apiFetch(withWorkspace(`/api/tasks/${t.id}`, workspaceId), {
        method: "PATCH",
        body: { status: t.status === "completed" ? "pending" : "completed" },
      }),
    onSuccess: invalidate,
  });

  const deleteMut = useMutation({
    mutationFn: (id: number) =>
      apiFetch(withWorkspace(`/api/tasks/${id}`, workspaceId), {
        method: "DELETE",
      }),
    onSuccess: invalidate,
  });

  const tasks = data?.tasks ?? [];

  return (
    <DashShell
      title="Tasks"
      subtitle={data ? `${data.total} total` : undefined}
      actions={
        <div className="flex items-center gap-1">
          {(["all", "pending", "completed"] as Filter[]).map((f) => (
            <button
              key={f}
              onClick={() => setFilter(f)}
              className={cn(
                "rounded-md px-2.5 py-1 text-[12px] capitalize transition-colors",
                filter === f
                  ? "bg-ink-2 text-fg"
                  : "text-fg-3 hover:text-fg-2"
              )}
            >
              {f}
            </button>
          ))}
        </div>
      }
    >
      <form
        onSubmit={(e) => {
          e.preventDefault();
          if (title.trim()) createMut.mutate();
        }}
        className="mb-5 flex items-center gap-2"
      >
        <input
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          placeholder="Add a task…"
          className="h-9 flex-1 rounded-md border border-line bg-ink-1 px-3 text-[13px] text-fg outline-none placeholder:text-fg-3 focus:border-line-2"
        />
        <input
          type="date"
          value={due}
          onChange={(e) => setDue(e.target.value)}
          className="h-9 rounded-md border border-line bg-ink-1 px-2 text-[12px] text-fg-2 outline-none focus:border-line-2"
        />
        <button
          type="submit"
          disabled={!title.trim() || createMut.isPending}
          className="flex h-9 items-center gap-1.5 rounded-md bg-fg px-3 text-[12px] font-medium text-ink-0 hover:brightness-110 disabled:opacity-50"
        >
          {createMut.isPending ? (
            <Loader2 className="spin h-3.5 w-3.5" />
          ) : (
            <Plus className="h-3.5 w-3.5" />
          )}
          Add
        </button>
      </form>

      {isError && (
        <div className="mb-4">
          <ErrorBanner error={error} />
        </div>
      )}

      {isLoading ? (
        <Loader2 className="spin h-4 w-4 text-fg-3" />
      ) : tasks.length === 0 ? (
        <p className="text-[13px] text-fg-3">No tasks here.</p>
      ) : (
        <div className="flex flex-col gap-1.5">
          {tasks.map((t) => {
            const done = t.status === "completed";
            const overdue =
              !done &&
              t.due_date &&
              new Date(t.due_date) < new Date(new Date().toDateString());
            return (
              <div
                key={t.id}
                className="group flex items-center gap-3 rounded-md border border-line bg-ink-1 px-3 py-2.5"
              >
                <button
                  onClick={() => toggleMut.mutate(t)}
                  className={cn(
                    "flex h-4 w-4 flex-shrink-0 items-center justify-center rounded border",
                    done
                      ? "border-done bg-done text-white"
                      : "border-line-2 bg-ink-0 hover:border-fg-3"
                  )}
                >
                  {done && <Check className="h-2.5 w-2.5" strokeWidth={3} />}
                </button>
                <span
                  className={cn(
                    "flex-1 text-[13px]",
                    done ? "text-fg-3 line-through" : "text-fg"
                  )}
                >
                  {t.title}
                </span>
                {t.due_date && (
                  <span
                    className={cn(
                      "rounded border px-1.5 py-px font-mono text-[10px]",
                      overdue
                        ? "border-err/20 bg-err/10 text-err-2"
                        : "border-line bg-ink-3 text-fg-3"
                    )}
                  >
                    {t.due_date.slice(0, 10)}
                  </span>
                )}
                <button
                  onClick={() => deleteMut.mutate(t.id)}
                  className="flex h-5 w-5 items-center justify-center rounded text-fg-3 opacity-0 transition-opacity hover:text-err-2 group-hover:opacity-100"
                >
                  <Trash2 className="h-3 w-3" />
                </button>
              </div>
            );
          })}
        </div>
      )}
    </DashShell>
  );
}
