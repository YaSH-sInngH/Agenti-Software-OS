"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/stores/auth";
import { getToken } from "@/lib/api";
import { FullScreenLoader } from "@/components/Loader";

export default function Home() {
  const router = useRouter();
  const loadUser = useAuth((s) => s.loadUser);

  useEffect(() => {
    (async () => {
      if (!getToken()) {
        router.replace("/login");
        return;
      }
      const me = await loadUser();
      router.replace(me ? "/workspaces" : "/login");
    })();
  }, [router, loadUser]);

  return <FullScreenLoader />;
}
