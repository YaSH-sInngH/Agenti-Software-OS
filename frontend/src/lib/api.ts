export const API_BASE =
  process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8001";

const TOKEN_KEY = "wos_token";

export function getToken(): string | null {
  if (typeof window === "undefined") return null;
  return window.localStorage.getItem(TOKEN_KEY);
}

export function setToken(token: string) {
  window.localStorage.setItem(TOKEN_KEY, token);
}

export function clearToken() {
  window.localStorage.removeItem(TOKEN_KEY);
}

export class ApiError extends Error {
  status: number;
  constructor(message: string, status: number) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

interface RequestOptions extends Omit<RequestInit, "body"> {
  body?: unknown;
}

// Unwraps the backend envelope { success, data, error } and returns `data`.
export async function apiFetch<T = unknown>(
  path: string,
  options: RequestOptions = {}
): Promise<T> {
  const { body, headers: hdrs, ...rest } = options;
  const headers = new Headers(hdrs);

  const isForm = typeof FormData !== "undefined" && body instanceof FormData;
  if (body !== undefined && !isForm && !headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }

  const token = getToken();
  if (token) headers.set("Authorization", `Bearer ${token}`);

  const res = await fetch(`${API_BASE}${path}`, {
    ...rest,
    headers,
    body:
      body === undefined
        ? undefined
        : isForm
        ? (body as FormData)
        : JSON.stringify(body),
  });

  let json: { success?: boolean; data?: T; error?: string } | null = null;
  try {
    json = await res.json();
  } catch {
    /* non-JSON response */
  }

  if (!res.ok || (json && json.success === false)) {
    const message =
      (json && json.error) || res.statusText || "Request failed";
    throw new ApiError(message, res.status);
  }

  return (json ? (json.data as T) : (undefined as T)) as T;
}

// Append a workspace_id query param when present.
export function withWorkspace(path: string, workspaceId?: number | null) {
  if (workspaceId == null) return path;
  const sep = path.includes("?") ? "&" : "?";
  return `${path}${sep}workspace_id=${workspaceId}`;
}
