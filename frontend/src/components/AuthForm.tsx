"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { Loader2, LayoutGrid } from "lucide-react";
import { useAuth } from "@/stores/auth";

export function AuthForm({ mode }: { mode: "login" | "register" }) {
  const router = useRouter();
  const login = useAuth((s) => s.login);
  const register = useAuth((s) => s.register);

  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      if (mode === "login") await login(email, password);
      else await register(name, email, password);
      router.replace("/workspaces");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong");
      setLoading(false);
    }
  }

  return (
    <div className="flex h-full w-full items-center justify-center bg-ink-0 px-4">
      <div className="w-full max-w-[340px]">
        <div className="mb-7 flex items-center gap-2.5">
          <div className="flex h-7 w-7 items-center justify-center rounded-md bg-ink-2 text-fg-2">
            <LayoutGrid className="h-3.5 w-3.5" />
          </div>
          <span className="text-[15px] font-semibold text-fg">Workspace OS</span>
        </div>

        <h1 className="mb-1 text-base font-medium text-fg">
          {mode === "login" ? "Sign in" : "Create your account"}
        </h1>
        <p className="mb-6 text-[13px] text-fg-2">
          {mode === "login"
            ? "Welcome back. Enter your credentials."
            : "Start with a fresh workspace in seconds."}
        </p>

        <form onSubmit={onSubmit} className="flex flex-col gap-3">
          {mode === "register" && (
            <Field
              label="Name"
              value={name}
              onChange={setName}
              type="text"
              placeholder="Ada Lovelace"
              autoFocus
            />
          )}
          <Field
            label="Email"
            value={email}
            onChange={setEmail}
            type="email"
            placeholder="you@company.com"
            autoFocus={mode === "login"}
          />
          <Field
            label="Password"
            value={password}
            onChange={setPassword}
            type="password"
            placeholder="••••••••"
          />

          {error && (
            <div className="rounded-md border border-err/25 bg-err/[0.08] px-3 py-2 text-[12px] text-err-2">
              {error}
            </div>
          )}

          <button
            type="submit"
            disabled={loading}
            className="mt-1 flex h-9 items-center justify-center gap-2 rounded-md bg-fg text-[13px] font-medium text-ink-0 transition-colors hover:brightness-110 disabled:opacity-60"
          >
            {loading && <Loader2 className="spin h-3.5 w-3.5" />}
            {mode === "login" ? "Sign in" : "Create account"}
          </button>
        </form>

        <p className="mt-5 text-[12px] text-fg-2">
          {mode === "login" ? (
            <>
              No account?{" "}
              <Link href="/register" className="text-fg hover:underline">
                Create one
              </Link>
            </>
          ) : (
            <>
              Already have an account?{" "}
              <Link href="/login" className="text-fg hover:underline">
                Sign in
              </Link>
            </>
          )}
        </p>
      </div>
    </div>
  );
}

function Field({
  label,
  value,
  onChange,
  type,
  placeholder,
  autoFocus,
}: {
  label: string;
  value: string;
  onChange: (v: string) => void;
  type: string;
  placeholder?: string;
  autoFocus?: boolean;
}) {
  return (
    <label className="flex flex-col gap-1.5">
      <span className="text-[11px] font-medium uppercase tracking-[0.06em] text-fg-3">
        {label}
      </span>
      <input
        type={type}
        value={value}
        autoFocus={autoFocus}
        placeholder={placeholder}
        onChange={(e) => onChange(e.target.value)}
        required
        className="h-9 rounded-md border border-line bg-ink-1 px-3 text-[13px] text-fg outline-none transition-colors placeholder:text-fg-3 focus:border-line-2"
      />
    </label>
  );
}
