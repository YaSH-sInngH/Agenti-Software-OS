"use client";

import { useRef, useState } from "react";
import { useParams } from "next/navigation";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import {
  Upload,
  FolderUp,
  Download,
  Trash2,
  RotateCw,
  Loader2,
  FileText,
} from "lucide-react";
import { apiFetch, API_BASE, getToken } from "@/lib/api";
import { FileTree } from "@/components/FileTree";
import { toast } from "@/stores/toast";
import { cn } from "@/lib/cn";
import type { FileNode, FileContent } from "@/lib/types";

function encodePath(p: string): string {
  return p.split("/").map(encodeURIComponent).join("/");
}

function relPath(f: File): string {
  return (f as File & { webkitRelativePath?: string }).webkitRelativePath || f.name;
}

export default function ExplorerPage() {
  const params = useParams<{ workspaceId: string }>();
  const workspaceId = Number(params.workspaceId);
  const qc = useQueryClient();
  const fileInput = useRef<HTMLInputElement>(null);
  const folderInput = useRef<HTMLInputElement | null>(null);
  const [selected, setSelected] = useState<string | null>(null);
  const [dragging, setDragging] = useState(false);

  const treeQuery = useQuery({
    queryKey: ["files", workspaceId],
    queryFn: () => apiFetch<FileNode>(`/api/workspaces/${workspaceId}/files`),
  });

  const contentQuery = useQuery({
    queryKey: ["file", workspaceId, selected],
    queryFn: () =>
      apiFetch<FileContent>(
        `/api/workspaces/${workspaceId}/files/${encodePath(selected!)}`
      ),
    enabled: Boolean(selected),
  });

  const uploadMut = useMutation({
    mutationFn: async ({
      files,
      withPaths,
    }: {
      files: File[];
      withPaths: boolean;
    }) => {
      const fd = new FormData();
      for (const f of files) {
        fd.append("files", f);
        if (withPaths) fd.append("paths", relPath(f));
      }
      fd.append("auto_index", "false");
      return apiFetch<{ saved: string[]; errors: { file: string; error: string }[] }>(
        `/api/workspaces/${workspaceId}/upload`,
        { method: "POST", body: fd }
      );
    },
    onSuccess: (data) => {
      qc.invalidateQueries({ queryKey: ["files", workspaceId] });
      const saved = data?.saved?.length ?? 0;
      if (saved) toast.success(`Uploaded ${saved} file${saved === 1 ? "" : "s"}`);
      if (data?.errors?.length)
        toast.error(`${data.errors.length} file(s) rejected`);
    },
    onError: (e) => toast.error((e as Error).message),
  });

  const deleteMut = useMutation({
    mutationFn: (path: string) =>
      apiFetch(`/api/workspaces/${workspaceId}/files/${encodePath(path)}`, {
        method: "DELETE",
      }),
    onSuccess: () => {
      setSelected(null);
      qc.invalidateQueries({ queryKey: ["files", workspaceId] });
    },
  });

  async function download(path: string) {
    const res = await fetch(
      `${API_BASE}/api/workspaces/${workspaceId}/download/${encodePath(path)}`,
      { headers: { Authorization: `Bearer ${getToken() ?? ""}` } }
    );
    const blob = await res.blob();
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = path.split("/").pop() ?? "file";
    a.click();
    URL.revokeObjectURL(url);
  }

  function onDrop(e: React.DragEvent) {
    e.preventDefault();
    setDragging(false);
    const files = Array.from(e.dataTransfer.files);
    if (files.length) uploadMut.mutate({ files, withPaths: false });
  }

  const nodes = treeQuery.data?.children ?? [];

  return (
    <div className="flex flex-1 flex-col overflow-hidden">
      <div className="flex h-9 flex-shrink-0 items-center gap-3 border-b border-line bg-ink-1 px-4">
        <span className="text-[10px] font-semibold uppercase tracking-[0.08em] text-fg-3">
          Explorer
        </span>
        {uploadMut.isPending && (
          <span className="flex items-center gap-1.5 font-mono text-[11px] text-fg-3">
            <Loader2 className="spin h-3 w-3" /> uploading…
          </span>
        )}
        <div className="ml-auto flex items-center gap-2">
          <button
            onClick={() => treeQuery.refetch()}
            className="flex items-center gap-1.5 rounded-md border border-line px-2.5 py-1 text-[12px] text-fg-2 transition-colors hover:border-line-2 hover:text-fg"
          >
            <RotateCw className="h-3 w-3" /> Refresh
          </button>
          <button
            onClick={() => folderInput.current?.click()}
            className="flex items-center gap-1.5 rounded-md border border-line px-2.5 py-1 text-[12px] text-fg-2 transition-colors hover:border-line-2 hover:text-fg"
          >
            <FolderUp className="h-3 w-3" /> Folder
          </button>
          <button
            onClick={() => fileInput.current?.click()}
            className="flex items-center gap-1.5 rounded-md bg-fg px-3 py-1 text-[12px] font-medium text-ink-0 transition-colors hover:brightness-110"
          >
            <Upload className="h-3 w-3" /> Upload
          </button>
          <input
            ref={fileInput}
            type="file"
            multiple
            hidden
            onChange={(e) => {
              if (e.target.files?.length)
                uploadMut.mutate({
                  files: Array.from(e.target.files),
                  withPaths: false,
                });
              e.target.value = "";
            }}
          />
          <input
            ref={(el) => {
              folderInput.current = el;
              if (el) {
                el.setAttribute("webkitdirectory", "");
                el.setAttribute("directory", "");
              }
            }}
            type="file"
            multiple
            hidden
            onChange={(e) => {
              if (e.target.files?.length)
                uploadMut.mutate({
                  files: Array.from(e.target.files),
                  withPaths: true,
                });
              e.target.value = "";
            }}
          />
        </div>
      </div>

      <div className="flex flex-1 overflow-hidden">
        <div
          onDragOver={(e) => {
            e.preventDefault();
            setDragging(true);
          }}
          onDragLeave={() => setDragging(false)}
          onDrop={onDrop}
          className={cn(
            "flex w-[320px] flex-shrink-0 flex-col overflow-y-auto border-r border-line bg-ink-1",
            dragging && "ring-1 ring-inset ring-work"
          )}
        >
          {treeQuery.isLoading ? (
            <div className="flex justify-center py-6">
              <Loader2 className="spin h-4 w-4 text-fg-3" />
            </div>
          ) : (
            <FileTree nodes={nodes} selected={selected} onSelect={setSelected} />
          )}
          <div
            onClick={() => fileInput.current?.click()}
            className={cn(
              "m-2.5 mt-auto flex cursor-pointer flex-col items-center gap-1.5 rounded-md border border-dashed border-line-2 py-3.5 transition-colors hover:border-fg-3 hover:bg-ink-2",
              dragging && "border-work bg-work/10"
            )}
          >
            <Upload className="h-4 w-4 text-fg-3" />
            <span className="text-[11px] text-fg-3">
              {dragging ? "Drop to upload" : "Drop files or click to upload"}
            </span>
          </div>
        </div>

        <div className="flex flex-1 flex-col overflow-hidden">
          {!selected ? (
            <div className="flex flex-1 flex-col items-center justify-center text-center">
              <FileText className="h-6 w-6 text-fg-3" />
              <p className="mt-3 text-[13px] text-fg-2">
                Select a file to view it.
              </p>
            </div>
          ) : (
            <>
              <div className="flex h-9 flex-shrink-0 items-center gap-3 border-b border-line bg-ink-1 px-4">
                <span className="truncate font-mono text-[12px] text-fg">
                  {selected}
                </span>
                <div className="ml-auto flex items-center gap-2">
                  <button
                    onClick={() => download(selected)}
                    className="flex items-center gap-1.5 rounded-md border border-line px-2.5 py-1 text-[12px] text-fg-2 transition-colors hover:border-line-2 hover:text-fg"
                  >
                    <Download className="h-3 w-3" /> Download
                  </button>
                  <button
                    onClick={() => deleteMut.mutate(selected)}
                    disabled={deleteMut.isPending}
                    className="flex items-center gap-1.5 rounded-md border border-line px-2.5 py-1 text-[12px] text-fg-2 transition-colors hover:border-err/40 hover:text-err-2 disabled:opacity-60"
                  >
                    <Trash2 className="h-3 w-3" /> Delete
                  </button>
                </div>
              </div>
              <div className="flex-1 overflow-auto p-4">
                {contentQuery.isLoading ? (
                  <Loader2 className="spin h-4 w-4 text-fg-3" />
                ) : contentQuery.data?.encoding === "binary" ? (
                  <div className="text-[13px] text-fg-2">
                    Binary file — use Download to save it.
                  </div>
                ) : (
                  <pre className="whitespace-pre-wrap break-words font-mono text-[12px] leading-relaxed text-fg">
                    {contentQuery.data?.content ?? ""}
                  </pre>
                )}
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
