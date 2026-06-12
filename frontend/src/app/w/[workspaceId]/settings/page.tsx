"use client";

import { useRouter } from "next/navigation";
import { Moon, Sun, LogOut } from "lucide-react";
import { useAuth } from "@/stores/auth";
import { useTheme, type Theme } from "@/stores/theme";
import { DashShell } from "@/components/dash/DashShell";
import { cn } from "@/lib/cn";

export default function SettingsPage() {
  const router = useRouter();
  const user = useAuth((s) => s.user);
  const logout = useAuth((s) => s.logout);
  const theme = useTheme((s) => s.theme);
  const setTheme = useTheme((s) => s.setTheme);

  return (
    <DashShell title="Settings">
      <Section label="Profile">
        <Row label="Name" value={user?.name ?? "—"} />
        <Row label="Email" value={user?.email ?? "—"} />
      </Section>

      <Section label="Appearance">
        <div className="flex items-center justify-between rounded-md border border-line bg-ink-1 px-3.5 py-3">
          <span className="text-[13px] text-fg">Theme</span>
          <div className="flex items-center gap-0.5 rounded-md border border-line bg-ink-0 p-0.5">
            <ThemeBtn
              active={theme === "dark"}
              onClick={() => setTheme("dark")}
              icon={<Moon className="h-3 w-3" />}
              label="Dark"
              value="dark"
            />
            <ThemeBtn
              active={theme === "light"}
              onClick={() => setTheme("light")}
              icon={<Sun className="h-3 w-3" />}
              label="Light"
              value="light"
            />
          </div>
        </div>
      </Section>

      <Section label="Account">
        <button
          onClick={() => {
            logout();
            router.replace("/login");
          }}
          className="flex items-center gap-2 rounded-md border border-line px-3 py-2 text-[12px] text-fg-2 transition-colors hover:border-err/40 hover:text-err-2"
        >
          <LogOut className="h-3.5 w-3.5" /> Sign out
        </button>
      </Section>
    </DashShell>
  );
}

function Section({
  label,
  children,
}: {
  label: string;
  children: React.ReactNode;
}) {
  return (
    <div className="mb-6">
      <div className="mb-2.5 text-[10px] font-semibold uppercase tracking-[0.08em] text-fg-3">
        {label}
      </div>
      <div className="flex flex-col gap-2">{children}</div>
    </div>
  );
}

function Row({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex items-center justify-between rounded-md border border-line bg-ink-1 px-3.5 py-3">
      <span className="text-[13px] text-fg-2">{label}</span>
      <span className="text-[13px] text-fg">{value}</span>
    </div>
  );
}

function ThemeBtn({
  active,
  onClick,
  icon,
  label,
}: {
  active: boolean;
  onClick: () => void;
  icon: React.ReactNode;
  label: string;
  value: Theme;
}) {
  return (
    <button
      onClick={onClick}
      className={cn(
        "flex items-center gap-1.5 rounded px-2.5 py-1 text-[11px] font-medium transition-colors",
        active ? "bg-ink-3 text-fg" : "text-fg-3 hover:text-fg-2"
      )}
    >
      {icon}
      {label}
    </button>
  );
}
