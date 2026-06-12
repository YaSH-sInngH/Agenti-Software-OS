"use client";

import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import {
  Database,
  RefreshCw,
  Search,
  Loader2,
  FileText,
  Sparkles,
} from "lucide-react";
import ReactMarkdown from "react-markdown";
import { apiFetch, withWorkspace } from "@/lib/api";
import { useWorkspaceId } from "@/hooks/useWorkspaceId";
import { DashShell } from "@/components/dash/DashShell";
import { toast } from "@/stores/toast";

interface IndexStatus {
  indexed_files: { file_path: string; indexed_at: string | null }[];
}
interface SearchResult {
  results: { file_path: string; score: number; snippet: string }[];
}
interface AskResult {
  answer: string;
  sources: string[];
}

export default function KnowledgePage() {
  const workspaceId = useWorkspaceId();
  const qc = useQueryClient();
  const [query, setQuery] = useState("");
  const [question, setQuestion] = useState("");

  const statusQuery = useQuery({
    queryKey: ["knowledge-status", workspaceId],
    queryFn: () =>
      apiFetch<IndexStatus>(withWorkspace("/api/knowledge/status", workspaceId)),
  });

  const indexMut = useMutation({
    mutationFn: (action: "index_workspace" | "reindex_workspace") =>
      apiFetch("/api/agents/indexer_agent/run", {
        method: "POST",
        body: { action, parameters: {}, workspace_id: workspaceId },
      }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["knowledge-status", workspaceId] });
      toast.success("Workspace indexed");
    },
    onError: (e) => toast.error((e as Error).message),
  });

  const searchMut = useMutation({
    mutationFn: () =>
      apiFetch<SearchResult>(withWorkspace("/api/knowledge/search", workspaceId), {
        method: "POST",
        body: { query, top_k: 10 },
      }),
  });

  const askMut = useMutation({
    mutationFn: () =>
      apiFetch<AskResult>("/api/agents/knowledge_agent/run", {
        method: "POST",
        body: {
          action: "ask_workspace",
          parameters: { question },
          workspace_id: workspaceId,
        },
      }).then((r) => (r as unknown as { result?: AskResult }).result ?? r),
  });

  const files = statusQuery.data?.indexed_files ?? [];

  return (
    <DashShell
      title="Knowledge"
      subtitle={`${files.length} indexed`}
      actions={
        <div className="flex items-center gap-2">
          <button
            onClick={() => indexMut.mutate("index_workspace")}
            disabled={indexMut.isPending}
            className="flex items-center gap-1.5 rounded-md bg-fg px-3 py-1 text-[12px] font-medium text-ink-0 hover:brightness-110 disabled:opacity-60"
          >
            {indexMut.isPending ? (
              <Loader2 className="spin h-3 w-3" />
            ) : (
              <Database className="h-3 w-3" />
            )}
            Index workspace
          </button>
          <button
            onClick={() => indexMut.mutate("reindex_workspace")}
            disabled={indexMut.isPending}
            className="flex items-center gap-1.5 rounded-md border border-line px-2.5 py-1 text-[12px] text-fg-2 transition-colors hover:border-line-2 hover:text-fg disabled:opacity-60"
          >
            <RefreshCw className="h-3 w-3" /> Re-index
          </button>
        </div>
      }
    >
      {indexMut.isError && (
        <div className="mb-4 rounded-md border border-err/25 bg-err/10 px-3 py-2 text-[12px] text-err-2">
          {(indexMut.error as Error).message}
        </div>
      )}

      {/* Ask */}
      <Section icon={<Sparkles className="h-3.5 w-3.5" />} label="Ask your documents">
        <form
          onSubmit={(e) => {
            e.preventDefault();
            if (question.trim()) askMut.mutate();
          }}
          className="flex items-center gap-2"
        >
          <input
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            placeholder="What do my documents say about…?"
            className="h-9 flex-1 rounded-md border border-line bg-ink-1 px-3 text-[13px] text-fg outline-none placeholder:text-fg-3 focus:border-line-2"
          />
          <button
            type="submit"
            disabled={!question.trim() || askMut.isPending}
            className="flex h-9 items-center gap-1.5 rounded-md bg-fg px-3 text-[12px] font-medium text-ink-0 hover:brightness-110 disabled:opacity-50"
          >
            {askMut.isPending ? (
              <Loader2 className="spin h-3.5 w-3.5" />
            ) : (
              "Ask"
            )}
          </button>
        </form>
        {askMut.data && (
          <div className="mt-3 rounded-md border border-line bg-ink-1 p-3">
            <div className="md-body text-[13px] leading-relaxed text-fg">
              <ReactMarkdown>{askMut.data.answer}</ReactMarkdown>
            </div>
            {askMut.data.sources?.length > 0 && (
              <div className="mt-2 flex flex-wrap gap-1.5">
                {askMut.data.sources.map((s) => (
                  <span
                    key={s}
                    className="rounded border border-line bg-ink-2 px-1.5 py-px font-mono text-[10px] text-fg-3"
                  >
                    {s}
                  </span>
                ))}
              </div>
            )}
          </div>
        )}
      </Section>

      {/* Search */}
      <Section icon={<Search className="h-3.5 w-3.5" />} label="Search documents">
        <form
          onSubmit={(e) => {
            e.preventDefault();
            if (query.trim()) searchMut.mutate();
          }}
          className="flex items-center gap-2"
        >
          <input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Find documents matching…"
            className="h-9 flex-1 rounded-md border border-line bg-ink-1 px-3 text-[13px] text-fg outline-none placeholder:text-fg-3 focus:border-line-2"
          />
          <button
            type="submit"
            disabled={!query.trim() || searchMut.isPending}
            className="flex h-9 items-center gap-1.5 rounded-md border border-line px-3 text-[12px] text-fg-2 hover:border-line-2 hover:text-fg disabled:opacity-50"
          >
            {searchMut.isPending ? (
              <Loader2 className="spin h-3.5 w-3.5" />
            ) : (
              "Search"
            )}
          </button>
        </form>
        {searchMut.data && (
          <div className="mt-3 flex flex-col gap-2">
            {searchMut.data.results.length === 0 ? (
              <p className="text-[12px] text-fg-3">No matches.</p>
            ) : (
              searchMut.data.results.map((m, i) => (
                <div key={i} className="rounded-md border border-line bg-ink-1 p-2.5">
                  <div className="mb-1 text-[12px] font-medium text-fg">
                    {m.file_path}
                  </div>
                  {m.snippet && (
                    <div className="mb-2 text-[11px] leading-relaxed text-fg-2">
                      {m.snippet}
                    </div>
                  )}
                  <div className="flex items-center gap-2">
                    <div className="h-[3px] flex-1 overflow-hidden rounded-full bg-ink-4">
                      <div
                        className="h-full rounded-full bg-work"
                        style={{ width: `${Math.round((m.score ?? 0) * 100)}%` }}
                      />
                    </div>
                    <span className="w-8 text-right font-mono text-[10px] text-fg-3">
                      {(m.score ?? 0).toFixed(2)}
                    </span>
                  </div>
                </div>
              ))
            )}
          </div>
        )}
      </Section>

      {/* Indexed files */}
      <Section icon={<Database className="h-3.5 w-3.5" />} label="Indexed files">
        {statusQuery.isLoading ? (
          <Loader2 className="spin h-4 w-4 text-fg-3" />
        ) : files.length === 0 ? (
          <p className="text-[12px] text-fg-3">
            Nothing indexed yet. Upload files, then “Index workspace”.
          </p>
        ) : (
          <div className="flex flex-col gap-1">
            {files.map((f) => (
              <div
                key={f.file_path}
                className="flex items-center gap-2 rounded-md border border-line bg-ink-1 px-2.5 py-1.5"
              >
                <FileText className="h-3.5 w-3.5 flex-shrink-0 text-fg-3" />
                <span className="flex-1 truncate font-mono text-[11px] text-fg-2">
                  {f.file_path}
                </span>
                {f.indexed_at && (
                  <span className="font-mono text-[10px] text-fg-3">
                    {f.indexed_at.slice(0, 10)}
                  </span>
                )}
              </div>
            ))}
          </div>
        )}
      </Section>
    </DashShell>
  );
}

function Section({
  icon,
  label,
  children,
}: {
  icon: React.ReactNode;
  label: string;
  children: React.ReactNode;
}) {
  return (
    <div className="mb-6">
      <div className="mb-2.5 flex items-center gap-2 text-fg-2">
        {icon}
        <span className="text-[11px] font-semibold uppercase tracking-[0.06em]">
          {label}
        </span>
      </div>
      {children}
    </div>
  );
}
