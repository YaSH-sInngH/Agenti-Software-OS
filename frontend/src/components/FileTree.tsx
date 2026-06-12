"use client";

import { useState } from "react";
import {
  ChevronRight,
  ChevronDown,
  Folder,
  FolderOpen,
  FileText,
  FileCode,
  File as FileIcon,
  type LucideIcon,
} from "lucide-react";
import { cn } from "@/lib/cn";
import type { FileNode } from "@/lib/types";

const CODE_EXT = new Set([
  "js", "ts", "tsx", "jsx", "py", "go", "rs", "java", "c", "cpp", "cc",
  "h", "rb", "php", "sh", "json", "html", "css", "yml", "yaml", "toml",
]);
const DOC_EXT = new Set(["md", "txt", "pdf", "docx", "doc", "rtf", "csv"]);

function fileIcon(name: string): LucideIcon {
  const ext = name.split(".").pop()?.toLowerCase() ?? "";
  if (CODE_EXT.has(ext)) return FileCode;
  if (DOC_EXT.has(ext)) return FileText;
  return FileIcon;
}

function fmtSize(bytes?: number): string {
  if (bytes == null) return "";
  if (bytes < 1024) return `${bytes}b`;
  if (bytes < 1024 * 1024) return `${Math.round(bytes / 1024)}k`;
  return `${(bytes / (1024 * 1024)).toFixed(1)}m`;
}

export function FileTree({
  nodes,
  selected,
  onSelect,
}: {
  nodes: FileNode[];
  selected: string | null;
  onSelect: (path: string) => void;
}) {
  if (nodes.length === 0) {
    return (
      <div className="px-3 py-6 text-center text-[12px] text-fg-3">
        This workspace is empty.
      </div>
    );
  }
  return (
    <div className="flex flex-col py-1">
      {nodes.map((n) => (
        <TreeNode
          key={n.path}
          node={n}
          depth={0}
          selected={selected}
          onSelect={onSelect}
        />
      ))}
    </div>
  );
}

function TreeNode({
  node,
  depth,
  selected,
  onSelect,
}: {
  node: FileNode;
  depth: number;
  selected: string | null;
  onSelect: (path: string) => void;
}) {
  const [open, setOpen] = useState(depth < 1);
  const pad = { paddingLeft: 8 + depth * 12 };

  if (node.type === "folder") {
    const Chevron = open ? ChevronDown : ChevronRight;
    const Fi = open ? FolderOpen : Folder;
    return (
      <>
        <button
          style={pad}
          onClick={() => setOpen((o) => !o)}
          className="flex items-center gap-1.5 py-1 pr-2 text-left transition-colors hover:bg-ink-2"
        >
          <Chevron className="h-3 w-3 flex-shrink-0 text-fg-3" />
          <Fi className="h-3.5 w-3.5 flex-shrink-0 text-fg-2" />
          <span className="truncate font-mono text-[11px] text-fg-2">
            {node.name}
          </span>
        </button>
        {open &&
          node.children?.map((c) => (
            <TreeNode
              key={c.path}
              node={c}
              depth={depth + 1}
              selected={selected}
              onSelect={onSelect}
            />
          ))}
      </>
    );
  }

  const Fi = fileIcon(node.name);
  const active = selected === node.path;
  return (
    <button
      style={pad}
      onClick={() => onSelect(node.path)}
      className={cn(
        "flex items-center gap-1.5 py-1 pr-2 text-left transition-colors hover:bg-ink-2",
        active && "bg-ink-2"
      )}
    >
      <span className="w-3 flex-shrink-0" />
      <Fi
        className={cn(
          "h-3.5 w-3.5 flex-shrink-0",
          active ? "text-fg" : "text-fg-3"
        )}
      />
      <span
        className={cn(
          "flex-1 truncate font-mono text-[11px]",
          active ? "text-fg" : "text-fg-2"
        )}
      >
        {node.name}
      </span>
      <span className="font-mono text-[10px] text-fg-3">
        {fmtSize(node.size)}
      </span>
    </button>
  );
}
