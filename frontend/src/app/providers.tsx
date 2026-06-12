"use client";

import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { useEffect, useState } from "react";
import { useTheme } from "@/stores/theme";
import { Toaster } from "@/components/Toaster";

export function Providers({ children }: { children: React.ReactNode }) {
  const initTheme = useTheme((s) => s.init);
  useEffect(() => {
    initTheme();
  }, [initTheme]);

  const [client] = useState(
    () =>
      new QueryClient({
        defaultOptions: {
          queries: {
            staleTime: 30_000,
            refetchOnWindowFocus: false,
            retry: 1,
          },
        },
      })
  );

  return (
    <QueryClientProvider client={client}>
      {children}
      <Toaster />
    </QueryClientProvider>
  );
}
