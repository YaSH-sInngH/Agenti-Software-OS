"use client";

import { useParams } from "next/navigation";
import { useRequireAuth } from "@/hooks/useRequireAuth";
import { FullScreenLoader } from "@/components/Loader";
import { TopBar } from "@/components/cockpit/TopBar";
import { IconNav } from "@/components/IconNav";
import { useUi } from "@/stores/ui";

export default function WorkspaceLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const params = useParams<{ workspaceId: string }>();
  const workspaceId = Number(params.workspaceId);
  const { ready } = useRequireAuth();
  const activeCount = useUi((s) => s.activeCount);

  if (!ready || Number.isNaN(workspaceId)) return <FullScreenLoader />;

  return (
    <div className="flex h-full flex-col bg-ink-0">
      <TopBar workspaceId={workspaceId} activeCount={activeCount} />
      <div className="flex flex-1 overflow-hidden">
        <IconNav workspaceId={workspaceId} />
        <div className="flex flex-1 overflow-hidden">{children}</div>
      </div>
    </div>
  );
}
