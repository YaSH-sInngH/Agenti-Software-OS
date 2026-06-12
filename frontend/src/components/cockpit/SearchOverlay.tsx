"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useQuery } from "@tanstack/react-query";
import { Search, FileText, ListTodo, Brain, Loader2 } from "lucide-react";
import { apiFetch } from "@/lib/api";

interface SearchData {
  query: string;
  documents: { file_path: string; score: number; snippet: string }[];
  tasks: { id: number; title: string }[];
  memories: { id: number; text: string; type: string }[];
}

export function SearchOverlay({
  workspaceId,
  open,
  onClose,
}: {
  workspaceId: number;
  open: boolean;
  onClose: () => void;
}) {
  const router = useRouter();
  const [q, setQ] = useState("");
  const [debounced, setDebounced] = useState("");

  useEffect(() => {
    const t = setTimeout(() => setDebounced(q), 200);
    return () => clearTimeout(t);
  }, [q]);

  useEffect(() => {
    if (!open) setQ("");
  }, [open]);

  const { data, isFetching } = useQuery({
    queryKey: ["search", workspaceId, debounced],
    queryFn: () =>
      apiFetch<SearchData>(
        `/api/search?workspace_id=${workspaceId}&q=${encodeURIComponent(
          debounced
        )}`
      ),
    enabled: open && debounced.trim().length > 0,
  });

  if (!open) return null;

  const go = (href: string) => {
    onClose();
    router.push(href);
  };

  const empty =
    data &&
    data.documents.length === 0 &&
    data.tasks.length === 0 &&
    data.memories.length === 0;

  return (
    <div className="fixed inset-0 z-50 flex items-start justify-center bg-black/50 pt-[12vh]">
      <div
        className="absolute inset-0"
        onClick={onClose}
      />
      <div className="relative z-10 w-full max-w-xl overflow-hidden rounded-xl border border-line-2 bg-ink-1 shadow-2xl shadow-black/60">
        <div className="flex items-center gap-2.5 border-b border-line px-3.5">
          <Search className="h-4 w-4 text-fg-3" />
          <input
            autoFocus
            value={q}
            onChange={(e) => setQ(e.target.value)}
            onKeyDown={(e) => e.key === "Escape" && onClose()}
            placeholder="Search documents, tasks, memories…"
            className="h-11 flex-1 bg-transparent text-[14px] text-fg outline-none placeholder:text-fg-3"
          />
          {isFetching && <Loader2 className="spin h-3.5 w-3.5 text-fg-3" />}
          <span className="rounded-[3px] border border-line bg-ink-3 px-1.5 py-px font-mono text-[10px] text-fg-3">
            esc
          </span>
        </div>

        <div className="max-h-[50vh] overflow-y-auto p-1.5">
          {!debounced.trim() ? (
            <Hint text="Type to search this workspace." />
          ) : empty ? (
            <Hint text="No matches." />
          ) : (
            <>
              <Group label="Documents">
                {data?.documents.map((d, i) => (
                  <Row
                    key={`d${i}`}
                    icon={<FileText className="h-3.5 w-3.5" />}
                    primary={d.file_path}
                    secondary={d.snippet}
                    onClick={() => go(`/w/${workspaceId}/files`)}
                  />
                ))}
              </Group>
              <Group label="Tasks">
                {data?.tasks.map((t) => (
                  <Row
                    key={`t${t.id}`}
                    icon={<ListTodo className="h-3.5 w-3.5" />}
                    primary={t.title}
                    onClick={() => go(`/w/${workspaceId}/tasks`)}
                  />
                ))}
              </Group>
              <Group label="Memories">
                {data?.memories.map((m) => (
                  <Row
                    key={`m${m.id}`}
                    icon={<Brain className="h-3.5 w-3.5" />}
                    primary={m.text}
                    secondary={m.type.replace("_memory", "")}
                    onClick={() => go(`/w/${workspaceId}/memory`)}
                  />
                ))}
              </Group>
            </>
          )}
        </div>
      </div>
    </div>
  );
}

function Group({
  label,
  children,
}: {
  label: string;
  children: React.ReactNode;
}) {
  const arr = Array.isArray(children) ? children : [children];
  if (arr.filter(Boolean).length === 0) return null;
  return (
    <div className="mb-1">
      <div className="px-2 py-1 text-[10px] font-semibold uppercase tracking-[0.08em] text-fg-3">
        {label}
      </div>
      {children}
    </div>
  );
}

function Row({
  icon,
  primary,
  secondary,
  onClick,
}: {
  icon: React.ReactNode;
  primary: string;
  secondary?: string;
  onClick: () => void;
}) {
  return (
    <button
      onClick={onClick}
      className="flex w-full items-center gap-2.5 rounded-md px-2 py-2 text-left transition-colors hover:bg-ink-2"
    >
      <span className="text-fg-3">{icon}</span>
      <span className="min-w-0 flex-1">
        <span className="block truncate text-[13px] text-fg">{primary}</span>
        {secondary && (
          <span className="block truncate text-[11px] text-fg-3">
            {secondary}
          </span>
        )}
      </span>
    </button>
  );
}

function Hint({ text }: { text: string }) {
  return <div className="px-3 py-6 text-center text-[12px] text-fg-3">{text}</div>;
}
