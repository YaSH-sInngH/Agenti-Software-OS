import { API_BASE, getToken, ApiError } from "./api";
import type { Step } from "./types";

export interface SSEMessage {
  event: string;
  data: unknown;
}

function parseFrame(frame: string): SSEMessage | null {
  let event = "message";
  const dataLines: string[] = [];

  for (const line of frame.split("\n")) {
    if (line.startsWith("event:")) event = line.slice(6).trim();
    else if (line.startsWith("data:")) dataLines.push(line.slice(5).trim());
  }

  if (dataLines.length === 0) return null;

  const raw = dataLines.join("\n");
  let data: unknown = raw;
  try {
    data = JSON.parse(raw);
  } catch {
    /* keep raw string */
  }
  return { event, data };
}

// POST to an SSE endpoint and invoke onEvent for each event frame.
// EventSource can't do POST + auth headers, so we stream the fetch body manually.
async function streamSSE(
  path: string,
  body: unknown,
  handlers: { onEvent: (msg: SSEMessage) => void; signal?: AbortSignal }
): Promise<void> {
  const res = await fetch(`${API_BASE}${path}`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${getToken() ?? ""}`,
    },
    body: JSON.stringify(body),
    signal: handlers.signal,
  });

  if (!res.ok || !res.body) {
    throw new ApiError("Stream failed to start", res.status);
  }

  const reader = res.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });

    let idx: number;
    while ((idx = buffer.indexOf("\n\n")) !== -1) {
      const frame = buffer.slice(0, idx);
      buffer = buffer.slice(idx + 2);
      const msg = parseFrame(frame);
      if (msg) handlers.onEvent(msg);
    }
  }
}

export function streamChat(
  body: { message: string; workspace_id?: number },
  handlers: { onEvent: (msg: SSEMessage) => void; signal?: AbortSignal }
) {
  return streamSSE("/api/chat/stream", body, handlers);
}

export function streamRun(
  body: { steps: Step[]; message?: string; workspace_id?: number },
  handlers: { onEvent: (msg: SSEMessage) => void; signal?: AbortSignal }
) {
  return streamSSE("/api/run/stream", body, handlers);
}
