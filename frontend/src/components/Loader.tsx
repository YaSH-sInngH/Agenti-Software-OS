import { Loader2 } from "lucide-react";

export function FullScreenLoader() {
  return (
    <div className="flex h-full w-full items-center justify-center bg-ink-0">
      <Loader2 className="spin h-5 w-5 text-fg-3" />
    </div>
  );
}
