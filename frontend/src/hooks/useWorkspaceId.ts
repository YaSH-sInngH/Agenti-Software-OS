"use client";

import { useParams } from "next/navigation";

export function useWorkspaceId(): number {
  const params = useParams<{ workspaceId: string }>();
  return Number(params.workspaceId);
}
