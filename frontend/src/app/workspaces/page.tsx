"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { LayoutGrid, Plus, ArrowRight, Loader2, LogOut } from "lucide-react";
import { apiFetch } from "@/lib/api";
import { useAuth } from "@/stores/auth";
import { useRequireAuth } from "@/hooks/useRequireAuth";
import { FullScreenLoader } from "@/components/Loader";
import type { Workspace } from "@/lib/types";

export default function WorkspacesPage() {
  const { user, ready } = useRequireAuth();
  const router = useRouter();
  const logout = useAuth((s) => s.logout);
  const qc = useQueryClient();
  const [creating, setCreating] = useState(false);
  const [name, setName] = useState("");

  const { data: workspaces, isLoading } = useQuery({
    queryKey: ["workspaces"],
    queryFn: () => apiFetch<Workspace[]>("/api/workspaces"),
    enabled: ready,
  });

  const createMut = useMutation({
    mutationFn: (n: string) =>
      apiFetch<Workspace>("/api/workspaces", {
        method: "POST",
        body: { name: n },
      }),
    onSuccess: (ws) => {
      qc.invalidateQueries({ queryKey: ["workspaces"] });
      router.push(`/w/${ws.id}`);
    },
  });

  if (!ready) return <FullScreenLoader />;

  function submitCreate(e: React.FormEvent) {
    e.preventDefault();
    if (!name.trim()) return;
    createMut.mutate(name.trim());
  }

  return (
    <div className="flex h-full flex-col bg-ink-0">
      {/* header */}
      <header className="flex h-10 flex-shrink-0 items-center border-b border-line bg-ink-1 px-4">
        <div className="flex items-center gap-2">
          <div className="flex h-5 w-5 items-center justify-center rounded bg-ink-3 text-fg-2">
            <LayoutGrid className="h-3 w-3" />
          </div>
          <span className="text-[13px] font-semibold text-fg">Workspace OS</span>
        </div>
        <div className="ml-auto flex items-center gap-3">
          <span className="text-[12px] text-fg-2">{user?.email}</span>
          <button
            onClick={() => {
              logout();
              router.replace("/login");
            }}
            className="flex items-center gap-1.5 rounded-md border border-line px-2.5 py-1 text-[12px] text-fg-2 transition-colors hover:border-line-2 hover:text-fg"
          >
            <LogOut className="h-3 w-3" /> Sign out
          </button>
        </div>
      </header>

      {/* body */}
      <main className="mx-auto w-full max-w-5xl flex-1 overflow-y-auto px-6 py-10">
        <div className="mb-1 flex items-end justify-between">
          <div>
            <h1 className="text-base font-medium text-fg">This PC</h1>
            <p className="mt-0.5 text-[13px] text-fg-2">
              Your workspaces — each one an isolated project.
            </p>
          </div>
          {!creating && (workspaces?.length ?? 0) > 0 && (
            <button
              onClick={() => setCreating(true)}
              className="flex items-center gap-1.5 rounded-md bg-fg px-3 py-1.5 text-[12px] font-medium text-ink-0 transition-colors hover:brightness-110"
            >
              <Plus className="h-3.5 w-3.5" /> New workspace
            </button>
          )}
        </div>

        {creating && (
          <form
            onSubmit={submitCreate}
            className="mt-5 flex items-center gap-2 rounded-lg border border-line bg-ink-1 p-3"
          >
            <input
              autoFocus
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="Workspace name (e.g. Resume Pipeline)"
              className="h-8 flex-1 rounded-md border border-line bg-ink-0 px-3 text-[13px] text-fg outline-none placeholder:text-fg-3 focus:border-line-2"
            />
            <button
              type="submit"
              disabled={createMut.isPending}
              className="flex h-8 items-center gap-1.5 rounded-md bg-fg px-3 text-[12px] font-medium text-ink-0 hover:brightness-110 disabled:opacity-60"
            >
              {createMut.isPending && <Loader2 className="spin h-3.5 w-3.5" />}
              Create
            </button>
            <button
              type="button"
              onClick={() => {
                setCreating(false);
                setName("");
              }}
              className="h-8 rounded-md border border-line px-3 text-[12px] text-fg-2 hover:text-fg"
            >
              Cancel
            </button>
          </form>
        )}

        {isLoading ? (
          <div className="mt-12 flex justify-center">
            <Loader2 className="spin h-5 w-5 text-fg-3" />
          </div>
        ) : (workspaces?.length ?? 0) === 0 && !creating ? (
          <EmptyState onCreate={() => setCreating(true)} />
        ) : (
          <div className="mt-6 grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3">
            {workspaces?.map((ws) => (
              <WorkspaceCard
                key={ws.id}
                ws={ws}
                onOpen={() => router.push(`/w/${ws.id}`)}
              />
            ))}
          </div>
        )}
      </main>
    </div>
  );
}

function WorkspaceCard({
  ws,
  onOpen,
}: {
  ws: Workspace;
  onOpen: () => void;
}) {
  const created = ws.created_at
    ? new Date(ws.created_at).toLocaleDateString(undefined, {
        month: "short",
        day: "numeric",
      })
    : "";
  return (
    <button
      onClick={onOpen}
      className="group flex h-[120px] flex-col items-start rounded-lg border border-line bg-ink-1 p-4 text-left transition-colors hover:border-line-2"
    >
      <span className="text-[14px] font-medium text-fg">{ws.name}</span>
      <span className="mt-1 text-[11px] text-fg-3">Created {created}</span>
      <span className="mt-auto flex items-center gap-1 text-[12px] text-fg-3 opacity-0 transition-opacity group-hover:opacity-100">
        Open <ArrowRight className="h-3 w-3" />
      </span>
    </button>
  );
}

function EmptyState({ onCreate }: { onCreate: () => void }) {
  return (
    <div className="mt-20 flex flex-col items-center justify-center text-center">
      <button
        onClick={onCreate}
        className="flex h-12 w-12 items-center justify-center rounded-full border border-line-2 text-fg-2 transition-colors hover:border-fg-2 hover:text-fg"
      >
        <Plus className="h-5 w-5" />
      </button>
      <p className="mt-4 text-[13px] text-fg-2">Create your first workspace</p>
    </div>
  );
}
