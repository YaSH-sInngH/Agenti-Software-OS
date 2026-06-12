"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import {
  LayoutGrid,
  ChevronDown,
  Search,
  LogOut,
  Check,
  Pencil,
  Trash2,
} from "lucide-react";
import { apiFetch } from "@/lib/api";
import { useAuth } from "@/stores/auth";
import { toast } from "@/stores/toast";
import { cn } from "@/lib/cn";
import type { Workspace } from "@/lib/types";
import { SearchOverlay } from "./SearchOverlay";

export function TopBar({
  workspaceId,
  activeCount,
}: {
  workspaceId: number;
  activeCount: number;
}) {
  const router = useRouter();
  const user = useAuth((s) => s.user);
  const logout = useAuth((s) => s.logout);
  const [open, setOpen] = useState(false);
  const [searchOpen, setSearchOpen] = useState(false);
  const [renameId, setRenameId] = useState<number | null>(null);
  const [renameValue, setRenameValue] = useState("");
  const qc = useQueryClient();

  const renameMut = useMutation({
    mutationFn: ({ id, name }: { id: number; name: string }) =>
      apiFetch(`/api/workspaces/${id}`, { method: "PATCH", body: { name } }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["workspaces"] });
      setRenameId(null);
      toast.success("Workspace renamed");
    },
    onError: (e) => toast.error((e as Error).message),
  });

  const deleteMut = useMutation({
    mutationFn: (id: number) =>
      apiFetch(`/api/workspaces/${id}`, { method: "DELETE" }),
    onSuccess: (_data, id) => {
      qc.invalidateQueries({ queryKey: ["workspaces"] });
      toast.success("Workspace deleted");
      if (id === workspaceId) router.replace("/workspaces");
    },
    onError: (e) => toast.error((e as Error).message),
  });

  useEffect(() => {
    function onKey(e: KeyboardEvent) {
      if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === "k") {
        e.preventDefault();
        setSearchOpen(true);
      }
    }
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, []);

  const { data: workspaces } = useQuery({
    queryKey: ["workspaces"],
    queryFn: () => apiFetch<Workspace[]>("/api/workspaces"),
  });

  const current = workspaces?.find((w) => w.id === workspaceId);
  const initials = (user?.name ?? user?.email ?? "?")
    .slice(0, 2)
    .toUpperCase();

  return (
    <header className="relative z-20 flex h-10 flex-shrink-0 items-center border-b border-line bg-ink-1 px-2.5">
      {/* workspace switcher */}
      <div className="relative">
        <button
          onClick={() => setOpen((o) => !o)}
          className="flex items-center gap-2 rounded-md border border-transparent px-2 py-1 transition-colors hover:border-line hover:bg-ink-2 sm:min-w-[170px]"
        >
          <span className="flex h-[18px] w-[18px] items-center justify-center rounded bg-ink-3 text-fg-2">
            <LayoutGrid className="h-2.5 w-2.5" />
          </span>
          <span className="text-[12px] font-medium text-fg">
            {current?.name ?? "Workspace"}
          </span>
          <span className="ml-0.5 h-1.5 w-1.5 rounded-full bg-done" />
          <ChevronDown className="ml-auto h-3 w-3 text-fg-3" />
        </button>

        {open && (
          <>
            <div
              className="fixed inset-0 z-10"
              onClick={() => setOpen(false)}
            />
            <div className="absolute left-0 top-9 z-20 w-60 rounded-lg border border-line bg-ink-2 p-1 shadow-xl shadow-black/40">
              <div className="px-2 py-1.5 text-[10px] font-semibold uppercase tracking-[0.08em] text-fg-3">
                Workspaces
              </div>
              {workspaces?.map((w) =>
                renameId === w.id ? (
                  <form
                    key={w.id}
                    onSubmit={(e) => {
                      e.preventDefault();
                      if (renameValue.trim())
                        renameMut.mutate({ id: w.id, name: renameValue.trim() });
                    }}
                    className="flex items-center gap-1 px-1 py-1"
                  >
                    <input
                      autoFocus
                      value={renameValue}
                      onChange={(e) => setRenameValue(e.target.value)}
                      onKeyDown={(e) => e.key === "Escape" && setRenameId(null)}
                      className="h-7 flex-1 rounded border border-line bg-ink-0 px-2 text-[12px] text-fg outline-none focus:border-line-2"
                    />
                    <button
                      type="submit"
                      className="flex h-7 w-7 items-center justify-center rounded text-fg-2 hover:bg-ink-3 hover:text-fg"
                    >
                      <Check className="h-3 w-3" />
                    </button>
                  </form>
                ) : (
                  <div
                    key={w.id}
                    className="group flex items-center gap-2 rounded-md px-2 py-1.5 transition-colors hover:bg-ink-3"
                  >
                    <button
                      onClick={() => {
                        setOpen(false);
                        if (w.id !== workspaceId) router.push(`/w/${w.id}`);
                      }}
                      className="flex min-w-0 flex-1 items-center gap-2 text-left text-[12px] text-fg"
                    >
                      <span className="truncate">{w.name}</span>
                      {w.id === workspaceId && (
                        <Check className="h-3 w-3 flex-shrink-0 text-fg-2" />
                      )}
                    </button>
                    <button
                      onClick={() => {
                        setRenameId(w.id);
                        setRenameValue(w.name);
                      }}
                      className="flex h-5 w-5 flex-shrink-0 items-center justify-center rounded text-fg-3 opacity-0 transition-opacity hover:text-fg group-hover:opacity-100"
                      title="Rename"
                    >
                      <Pencil className="h-3 w-3" />
                    </button>
                    <button
                      onClick={() => {
                        if (
                          confirm(`Delete workspace “${w.name}”? This cannot be undone.`)
                        )
                          deleteMut.mutate(w.id);
                      }}
                      className="flex h-5 w-5 flex-shrink-0 items-center justify-center rounded text-fg-3 opacity-0 transition-opacity hover:text-err-2 group-hover:opacity-100"
                      title="Delete"
                    >
                      <Trash2 className="h-3 w-3" />
                    </button>
                  </div>
                )
              )}
              <div className="my-1 h-px bg-line" />
              <button
                onClick={() => {
                  setOpen(false);
                  router.push("/workspaces");
                }}
                className="w-full rounded-md px-2 py-1.5 text-left text-[12px] text-fg-2 transition-colors hover:bg-ink-3 hover:text-fg"
              >
                All workspaces…
              </button>
            </div>
          </>
        )}
      </div>

      <div className="mx-2 h-[18px] w-px bg-line" />

      {/* search */}
      <button
        onClick={() => setSearchOpen(true)}
        className="flex h-7 max-w-[360px] flex-1 items-center gap-2 rounded-md border border-line bg-ink-2 px-2.5 text-fg-3 transition-colors hover:border-line-2"
      >
        <Search className="h-3 w-3" />
        <span className="flex-1 text-left text-[12px]">
          Search files, tasks, memories…
        </span>
        <span className="rounded-[3px] border border-line bg-ink-3 px-1.5 py-px font-mono text-[10px]">
          ⌘K
        </span>
      </button>

      <SearchOverlay
        workspaceId={workspaceId}
        open={searchOpen}
        onClose={() => setSearchOpen(false)}
      />

      <div className="ml-auto flex items-center gap-3">
        <span
          className={cn(
            "hidden items-center gap-1.5 font-mono text-[11px] text-fg-3 sm:flex",
            activeCount > 0 && "text-fg-2"
          )}
        >
          {activeCount > 0 && (
            <span className="pulse-dot h-[5px] w-[5px] rounded-full bg-work" />
          )}
          {activeCount} active
        </span>
        <div className="h-[18px] w-px bg-line" />
        <button
          title="Sign out"
          onClick={() => {
            logout();
            router.replace("/login");
          }}
          className="flex h-6 items-center gap-1.5 rounded-md border border-line px-2 text-[11px] text-fg-2 transition-colors hover:border-line-2 hover:text-fg"
        >
          <span className="flex h-4 w-4 items-center justify-center rounded-full bg-ink-3 text-[9px] font-semibold">
            {initials}
          </span>
          <LogOut className="h-3 w-3" />
        </button>
      </div>
    </header>
  );
}
