"use client";

import ReactMarkdown from "react-markdown";
import { Check, X, Download } from "lucide-react";
import { agentIcon, prettyAgent } from "@/lib/icons";
import { cn } from "@/lib/cn";
import { API_BASE, getToken } from "@/lib/api";
import type { StepResult } from "@/lib/types";

export function ResultCard({
  result,
  workspaceId,
}: {
  result: StepResult;
  workspaceId?: number;
}) {
  const Icon = agentIcon(result.agent);
  const r = result.result ?? {};
  const ok = r.success !== false;

  return (
    <div className="overflow-hidden rounded-lg border border-line bg-ink-1">
      <div className="flex items-center gap-2 border-b border-line bg-ink-2 px-3 py-2">
        <Icon className="h-3 w-3 text-fg-2" />
        <span className="text-[10px] font-semibold uppercase tracking-[0.06em] text-fg-2">
          {prettyAgent(result.agent)}
        </span>
        <span className="font-mono text-[10px] text-fg-3">· {result.action}</span>
        <span
          className={cn(
            "ml-auto flex items-center gap-1 font-mono text-[10px]",
            ok ? "text-done" : "text-err-2"
          )}
        >
          {ok ? <Check className="h-3 w-3" /> : <X className="h-3 w-3" />}
          {ok ? "done" : "failed"}
        </span>
      </div>
      <div className="min-w-0 p-3">
        <ResultBody
          agent={result.agent}
          action={result.action}
          r={r}
          ok={ok}
          workspaceId={workspaceId}
        />
      </div>
    </div>
  );
}

function Markdown({ text }: { text: string }) {
  return (
    <div className="md-body max-h-[420px] overflow-y-auto break-words text-[12px] leading-relaxed text-fg-2">
      <ReactMarkdown>{text}</ReactMarkdown>
    </div>
  );
}

async function downloadFile(workspaceId: number, relPath: string) {
  const enc = relPath.split("/").map(encodeURIComponent).join("/");
  const res = await fetch(
    `${API_BASE}/api/workspaces/${workspaceId}/download/${enc}`,
    { headers: { Authorization: `Bearer ${getToken() ?? ""}` } }
  );
  const blob = await res.blob();
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = relPath.split("/").pop() ?? "file";
  a.click();
  URL.revokeObjectURL(url);
}

function ResultBody({
  agent,
  action,
  r,
  ok,
  workspaceId,
}: {
  agent: string;
  action: string;
  r: Record<string, unknown>;
  ok: boolean;
  workspaceId?: number;
}) {
  if (!ok) {
    return (
      <div className="text-[12px] text-err-2">
        {(r.message as string) || "This step failed."}
      </div>
    );
  }

  // Terminal output
  if (agent === "terminal_agent") {
    return (
      <pre className="max-h-[420px] overflow-auto rounded-md border border-line bg-ink-0 px-3 py-2.5 font-mono text-[11.5px] leading-relaxed text-fg">
        {(r.stdout as string) || ""}
        {r.stderr ? (
          <span className="text-err-2">{"\n" + (r.stderr as string)}</span>
        ) : null}
        {"\n"}
        <span className="text-fg-3">exit {String(r.returncode ?? 0)}</span>
      </pre>
    );
  }

  // Resume analysis — files + rendered analysis
  if (agent === "resume_agent") {
    const files = (r.files as string[]) ?? [];
    return (
      <div className="flex flex-col gap-2.5">
        {files.length > 0 && (
          <div className="flex flex-wrap gap-1.5">
            {files.map((f) => (
              <span
                key={f}
                className="rounded border border-line bg-ink-2 px-1.5 py-px font-mono text-[10px] text-fg-3"
              >
                {f}
              </span>
            ))}
          </div>
        )}
        {typeof r.analysis === "string" && <Markdown text={r.analysis} />}
      </div>
    );
  }

  // Knowledge search
  if (Array.isArray(r.results)) {
    const results = r.results as Array<{
      file_path: string;
      score: number;
      snippet: string;
    }>;
    if (results.length === 0) return <Empty text="No matches found." />;
    return (
      <div className="flex flex-col gap-2">
        {results.map((m, i) => (
          <div key={i} className="rounded-md border border-line bg-ink-2 p-2.5">
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
        ))}
      </div>
    );
  }

  // Task list
  if (Array.isArray(r.tasks)) {
    const tasks = r.tasks as Array<{
      title: string;
      status: string;
      due_date: string | null;
    }>;
    if (tasks.length === 0) return <Empty text="No tasks." />;
    return (
      <div className="flex flex-col gap-1.5">
        {tasks.map((t, i) => {
          const done = t.status === "completed";
          return (
            <div
              key={i}
              className="flex items-center gap-2.5 rounded-md bg-ink-2 px-2.5 py-1.5"
            >
              <span
                className={cn(
                  "flex h-3.5 w-3.5 items-center justify-center rounded border",
                  done
                    ? "border-done bg-done text-white"
                    : "border-line-2 bg-ink-0"
                )}
              >
                {done && <Check className="h-2.5 w-2.5" strokeWidth={3} />}
              </span>
              <span
                className={cn(
                  "flex-1 text-[12px]",
                  done ? "text-fg-3 line-through" : "text-fg"
                )}
              >
                {t.title}
              </span>
              {t.due_date && (
                <span className="rounded border border-line bg-ink-3 px-1.5 py-px font-mono text-[10px] text-fg-3">
                  {t.due_date.slice(0, 10)}
                </span>
              )}
            </div>
          );
        })}
      </div>
    );
  }

  // Report generated — path + format + download
  if (typeof r.path === "string" && (action.includes("report") || r.format)) {
    const base = (r.path as string).split(/[\\/]/).pop() ?? (r.path as string);
    return (
      <div className="flex items-center gap-2 text-[12px] text-fg-2">
        <span className="rounded border border-line bg-ink-3 px-1.5 py-px font-mono text-[10px] uppercase text-fg-2">
          {String(r.format ?? "file")}
        </span>
        <span className="truncate font-mono text-fg">{base}</span>
        {workspaceId != null && (
          <button
            onClick={() => downloadFile(workspaceId, base)}
            className="ml-auto flex items-center gap-1.5 rounded-md border border-line px-2 py-1 text-[11px] text-fg-2 transition-colors hover:border-line-2 hover:text-fg"
          >
            <Download className="h-3 w-3" /> Download
          </button>
        )}
      </div>
    );
  }

  // File write/create
  if (typeof r.path === "string") {
    const base = (r.path as string).split(/[\\/]/).pop() ?? (r.path as string);
    return <div className="font-mono text-[12px] text-fg">{base}</div>;
  }

  // Indexer summary
  if (Array.isArray(r.indexed) || typeof r.total === "number") {
    const indexed = (r.indexed as unknown[])?.length ?? 0;
    const skipped = (r.skipped as unknown[])?.length ?? 0;
    return (
      <div className="flex gap-4 text-[12px] text-fg-2">
        <span>
          Indexed <strong className="text-fg">{indexed}</strong>
        </span>
        <span>{skipped} unchanged</span>
        <span className="text-fg-3">{String(r.total ?? 0)} total</span>
      </div>
    );
  }

  // Rendered markdown text fields (answer / summary / analysis / content)
  const textField =
    (r.answer as string) ||
    (r.summary as string) ||
    (r.content as string);
  if (typeof textField === "string") {
    const sources = r.sources as string[] | undefined;
    return (
      <div className="flex flex-col gap-2">
        <Markdown text={textField} />
        {sources && sources.length > 0 && (
          <div className="flex flex-wrap gap-1.5">
            {sources.map((s) => (
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
    );
  }

  if (typeof r.message === "string") {
    return <div className="text-[12px] text-fg-2">{r.message}</div>;
  }

  return (
    <pre className="max-h-[300px] overflow-auto rounded-md border border-line bg-ink-0 p-2.5 font-mono text-[11px] text-fg-2">
      {JSON.stringify(r, null, 2)}
    </pre>
  );
}

function Empty({ text }: { text: string }) {
  return <div className="text-[12px] text-fg-3">{text}</div>;
}
