import { AlertTriangle } from "lucide-react";

export function ErrorBanner({ error }: { error: unknown }) {
  const message =
    error instanceof Error ? error.message : "Something went wrong";
  return (
    <div className="flex items-center gap-2 rounded-md border border-err/25 bg-err/10 px-3.5 py-2.5 text-[12px] text-err-2">
      <AlertTriangle className="h-3.5 w-3.5 flex-shrink-0" />
      {message}
    </div>
  );
}

export function EmptyState({
  icon,
  title,
  hint,
}: {
  icon: React.ReactNode;
  title: string;
  hint?: string;
}) {
  return (
    <div className="flex flex-col items-center justify-center py-16 text-center">
      <span className="text-fg-3">{icon}</span>
      <p className="mt-3 text-[13px] text-fg-2">{title}</p>
      {hint && <p className="mt-1 text-[12px] text-fg-3">{hint}</p>}
    </div>
  );
}
