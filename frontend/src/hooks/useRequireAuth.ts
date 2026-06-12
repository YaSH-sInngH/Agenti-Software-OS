"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/stores/auth";
import { getToken } from "@/lib/api";

export function useRequireAuth() {
  const router = useRouter();
  const user = useAuth((s) => s.user);
  const loadUser = useAuth((s) => s.loadUser);
  const [ready, setReady] = useState(Boolean(user));

  useEffect(() => {
    let active = true;
    (async () => {
      if (!getToken()) {
        router.replace("/login");
        return;
      }
      if (user) {
        setReady(true);
        return;
      }
      const me = await loadUser();
      if (!active) return;
      if (!me) router.replace("/login");
      else setReady(true);
    })();
    return () => {
      active = false;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return { user, ready };
}
