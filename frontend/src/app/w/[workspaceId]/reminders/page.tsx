"use client";

import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Plus, Trash2, Loader2, Sunrise, Bell } from "lucide-react";
import { apiFetch, withWorkspace } from "@/lib/api";
import { useWorkspaceId } from "@/hooks/useWorkspaceId";
import { DashShell } from "@/components/dash/DashShell";
import { ErrorBanner } from "@/components/dash/States";
import type { Reminder } from "@/lib/types";

interface DailySummary {
  date: string;
  tasks: { title: string; due_date: string; status: string }[];
  reminders: Reminder[];
}

export default function RemindersPage() {
  const workspaceId = useWorkspaceId();
  const qc = useQueryClient();
  const [message, setMessage] = useState("");
  const [remindAt, setRemindAt] = useState("");

  const summaryQuery = useQuery({
    queryKey: ["daily-summary", workspaceId],
    queryFn: () =>
      apiFetch<DailySummary>(
        withWorkspace("/api/reminders/daily-summary", workspaceId)
      ),
  });

  const listQuery = useQuery({
    queryKey: ["reminders", workspaceId],
    queryFn: () =>
      apiFetch<{ reminders: Reminder[]; total: number }>(
        withWorkspace("/api/reminders", workspaceId)
      ),
  });

  const queryError = summaryQuery.error ?? listQuery.error;

  const invalidate = () => {
    qc.invalidateQueries({ queryKey: ["reminders", workspaceId] });
    qc.invalidateQueries({ queryKey: ["daily-summary", workspaceId] });
  };

  const createMut = useMutation({
    mutationFn: () =>
      apiFetch(withWorkspace("/api/reminders", workspaceId), {
        method: "POST",
        body: {
          message,
          remind_at: remindAt ? new Date(remindAt).toISOString() : undefined,
        },
      }),
    onSuccess: () => {
      setMessage("");
      setRemindAt("");
      invalidate();
    },
  });

  const deleteMut = useMutation({
    mutationFn: (id: number) =>
      apiFetch(withWorkspace(`/api/reminders/${id}`, workspaceId), {
        method: "DELETE",
      }),
    onSuccess: invalidate,
  });

  const summary = summaryQuery.data;
  const reminders = listQuery.data?.reminders ?? [];

  return (
    <DashShell title="Reminders" subtitle="Daily briefing">
      {queryError && (
        <div className="mb-4">
          <ErrorBanner error={queryError} />
        </div>
      )}

      {/* Briefing card */}
      <div className="mb-5 rounded-lg border border-line bg-ink-1 p-4">
        <div className="mb-3 flex items-center gap-2">
          <Sunrise className="h-4 w-4 text-warn" />
          <span className="text-[13px] font-medium text-fg">
            Today&apos;s briefing
          </span>
          {summary?.date && (
            <span className="font-mono text-[11px] text-fg-3">
              {summary.date}
            </span>
          )}
        </div>
        {summaryQuery.isLoading ? (
          <Loader2 className="spin h-4 w-4 text-fg-3" />
        ) : (summary?.tasks.length ?? 0) === 0 &&
          (summary?.reminders.length ?? 0) === 0 ? (
          <p className="text-[12px] text-fg-3">
            Nothing due today. You&apos;re clear.
          </p>
        ) : (
          <div className="flex flex-col gap-3 sm:flex-row">
            <Briefing label="Tasks due" count={summary?.tasks.length ?? 0}>
              {summary?.tasks.map((t, i) => (
                <li key={i} className="truncate text-[12px] text-fg-2">
                  {t.title}
                </li>
              ))}
            </Briefing>
            <Briefing
              label="Reminders"
              count={summary?.reminders.length ?? 0}
            >
              {summary?.reminders.map((r) => (
                <li key={r.id} className="truncate text-[12px] text-fg-2">
                  {r.message}
                </li>
              ))}
            </Briefing>
          </div>
        )}
      </div>

      {/* Create */}
      <form
        onSubmit={(e) => {
          e.preventDefault();
          if (message.trim()) createMut.mutate();
        }}
        className="mb-5 flex items-center gap-2"
      >
        <input
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          placeholder="Remind me to…"
          className="h-9 flex-1 rounded-md border border-line bg-ink-1 px-3 text-[13px] text-fg outline-none placeholder:text-fg-3 focus:border-line-2"
        />
        <input
          type="datetime-local"
          value={remindAt}
          onChange={(e) => setRemindAt(e.target.value)}
          className="h-9 rounded-md border border-line bg-ink-1 px-2 text-[12px] text-fg-2 outline-none focus:border-line-2"
        />
        <button
          type="submit"
          disabled={!message.trim() || createMut.isPending}
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

      {listQuery.isLoading ? (
        <Loader2 className="spin h-4 w-4 text-fg-3" />
      ) : reminders.length === 0 ? (
        <p className="text-[13px] text-fg-3">No reminders yet.</p>
      ) : (
        <div className="flex flex-col gap-1.5">
          {reminders.map((r) => (
            <div
              key={r.id}
              className="group flex items-center gap-3 rounded-md border border-line bg-ink-1 px-3 py-2.5"
            >
              <Bell className="h-3.5 w-3.5 flex-shrink-0 text-fg-3" />
              <span className="flex-1 text-[13px] text-fg">{r.message}</span>
              {r.remind_at && (
                <span className="rounded border border-line bg-ink-3 px-1.5 py-px font-mono text-[10px] text-fg-3">
                  {r.remind_at.slice(0, 16).replace("T", " ")}
                </span>
              )}
              <button
                onClick={() => deleteMut.mutate(r.id)}
                className="flex h-5 w-5 items-center justify-center rounded text-fg-3 opacity-0 transition-opacity hover:text-err-2 group-hover:opacity-100"
              >
                <Trash2 className="h-3 w-3" />
              </button>
            </div>
          ))}
        </div>
      )}
    </DashShell>
  );
}

function Briefing({
  label,
  count,
  children,
}: {
  label: string;
  count: number;
  children: React.ReactNode;
}) {
  return (
    <div className="flex-1 rounded-md border border-line bg-ink-2 p-3">
      <div className="mb-2 flex items-baseline gap-2">
        <span className="text-[18px] font-semibold text-fg">{count}</span>
        <span className="text-[11px] text-fg-3">{label}</span>
      </div>
      <ul className="flex flex-col gap-1">{children}</ul>
    </div>
  );
}
