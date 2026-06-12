"use client";

import { useRouter } from "next/navigation";
import { useQuery } from "@tanstack/react-query";
import { Loader2, FolderTree, History, Settings } from "lucide-react";
import { apiFetch } from "@/lib/api";
import { agentIcon, prettyAgent } from "@/lib/icons";
import { cn } from "@/lib/cn";
import type { AgentManifest, StepStatus } from "@/lib/types";
import { StatusDot, ScopeBadge } from "./parts";

export function AgentRoster({
  workspaceId,
  statusMap,
  activeAction,
}: {
  workspaceId: number;
  statusMap: Record<string, StepStatus | "idle">;
  activeAction: Record<string, string>;
}) {
  const router = useRouter();
  const { data: agents, isLoading } = useQuery({
    queryKey: ["agents"],
    queryFn: () => apiFetch<AgentManifest[]>("/api/agents"),
    staleTime: Infinity,
  });

  return (
    <aside className="hidden w-56 flex-shrink-0 flex-col overflow-hidden border-r border-line bg-ink-1 md:flex">
      <div className="flex items-center justify-between px-3.5 pb-1.5 pt-3.5">
        <span className="text-[10px] font-semibold uppercase tracking-[0.08em] text-fg-3">
          Agents
        </span>
        <span className="font-mono text-[10px] text-fg-3">
          {agents?.length ?? ""}
        </span>
      </div>

      <div className="flex-1 overflow-y-auto">
      {isLoading ? (
        <div className="flex justify-center py-6">
          <Loader2 className="spin h-4 w-4 text-fg-3" />
        </div>
      ) : (
        <div className="flex flex-col">
          {agents?.map((agent) => {
            const Icon = agentIcon(agent.name);
            const status = statusMap[agent.name] ?? "idle";
            const action = activeAction[agent.name];
            const active = status === "working";
            return (
              <div
                key={agent.name}
                className={cn(
                  "flex items-center gap-2.5 border-l-2 border-transparent px-3.5 py-1.5 transition-colors hover:bg-ink-2",
                  active && "border-l-work bg-ink-2"
                )}
              >
                <div
                  className={cn(
                    "flex h-[26px] w-[26px] flex-shrink-0 items-center justify-center rounded-[5px] border border-line bg-ink-2 text-fg-2",
                    active && "border-work/30 bg-work/[0.08] text-work-2"
                  )}
                >
                  <Icon className="h-3.5 w-3.5" />
                </div>
                <div className="min-w-0 flex-1">
                  <div className="truncate text-[12px] font-medium text-fg">
                    {prettyAgent(agent.name)}
                  </div>
                  <div className="truncate font-mono text-[10px] text-fg-3">
                    {action ?? agent.actions[0]?.name ?? ""}
                  </div>
                </div>
                <ScopeBadge scope={agent.scope} />
                <StatusDot status={status} />
              </div>
            );
          })}
        </div>
      )}
      </div>

      <div className="flex flex-col gap-0.5 border-t border-line p-2.5">
        <FooterBtn
          icon={<FolderTree className="h-3.5 w-3.5" />}
          label="Explorer"
          onClick={() => router.push(`/w/${workspaceId}/files`)}
        />
        <FooterBtn icon={<History className="h-3.5 w-3.5" />} label="Run History" />
        <FooterBtn icon={<Settings className="h-3.5 w-3.5" />} label="Settings" />
      </div>
    </aside>
  );
}

function FooterBtn({
  icon,
  label,
  onClick,
}: {
  icon: React.ReactNode;
  label: string;
  onClick?: () => void;
}) {
  return (
    <button
      onClick={onClick}
      className="flex items-center gap-2.5 rounded-md px-2 py-1.5 text-[12px] text-fg-2 transition-colors hover:bg-ink-2 hover:text-fg"
    >
      {icon}
      {label}
    </button>
  );
}
