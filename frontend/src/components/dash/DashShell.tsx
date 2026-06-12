export function DashShell({
  title,
  subtitle,
  actions,
  children,
  wide,
}: {
  title: string;
  subtitle?: string;
  actions?: React.ReactNode;
  children: React.ReactNode;
  wide?: boolean;
}) {
  return (
    <div className="flex flex-1 flex-col overflow-hidden">
      <div className="flex h-9 flex-shrink-0 items-center gap-3 border-b border-line bg-ink-1 px-4">
        <span className="text-[10px] font-semibold uppercase tracking-[0.08em] text-fg-3">
          {title}
        </span>
        {subtitle && (
          <span className="font-mono text-[11px] text-fg-3">{subtitle}</span>
        )}
        <div className="ml-auto flex items-center gap-2">{actions}</div>
      </div>
      <div className="flex-1 overflow-y-auto">
        <div
          className={`mx-auto w-full px-6 py-6 ${wide ? "max-w-5xl" : "max-w-3xl"}`}
        >
          {children}
        </div>
      </div>
    </div>
  );
}
