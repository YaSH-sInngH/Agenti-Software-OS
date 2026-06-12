# Architecture — Workspace OS

Workspace OS is a personal, multi-tenant **operating system for AI agents**. A user
owns several isolated **workspaces** (think "This PC" with separate drives — one per
project), imports files / folders / codebases into them, and issues natural-language
requests. A visible team of **12 specialist agents** carries those requests out
through a **plan → approve → execute** loop, streaming each step live. It is
deliberately *not* a hidden chatbot: the agents, their steps and their outputs are all
first-class and controllable.

This document covers the **backend** and how a request flows through it. See also:

- [AGENTS.md](AGENTS.md) — the 12 agents, their scopes and actions.
- [FRONTEND.md](FRONTEND.md) — the cockpit, workspace UI and live run panel.

---

## 1. High-level shape

```
                       ┌──────────────────────────────────────────┐
   Browser (Next.js)   │  FastAPI app  (backend/src/main.py)        │
   ──────────────────► │                                            │
   JWT Bearer token    │  REST + SSE routers  (src/api/*)           │
                       │        │                                   │
                       │        ▼                                   │
                       │  Orchestration graph  (src/graph/*)        │
                       │   planner → router → response  (LangGraph) │
                       │        │                                   │
                       │        ▼                                   │
                       │  12 agent executors  (src/agents/*)        │
                       └────────┬──────────────┬────────────┬───────┘
                                │              │            │
                          SQL (SQLAlchemy)  Pinecone     Workspace disk
                          tasks/reminders/  vector index  workspaces/{id}/
                          memory/runs/...   (RAG + memory)
```

- **API layer** (`src/api/*`) — thin routers. One router per resource; every route is
  auth-guarded and returns the standard envelope.
- **Orchestration** (`src/graph/*`) — a LangGraph state machine that turns a message
  into a plan, runs the steps, and writes a friendly response.
- **Agents** (`src/agents/*`) — one folder per agent: an `executor` (dispatches
  actions) plus a `service`/`tools` module (the real work).
- **Core** (`src/core/*`) — config, DB, schemas, LLM clients, vector store, shared
  response helpers.
- **Workspace plumbing** (`src/workspaces/*`) — path resolution, the sandbox, and
  file tree / upload helpers.

---

## 2. Two architectural ideas everything is built around

1. **Multi-workspace scoping.** Every piece of data is keyed by `(user_id,
   workspace_id)`, never by user alone. Switching the active workspace re-scopes
   files, tasks, reminders, memory, the knowledge index and run history. On disk each
   workspace is an isolated directory `workspaces/{workspace_id}/`; in Pinecone each
   gets its own namespace `ws_{workspace_id}_*`. A `WorkspaceContext{user_id,
   workspace_id}` ([src/graph/context.py](../backend/src/graph/context.py)) is threaded
   into every agent executor so an agent can only ever touch the active workspace.

2. **Plan ↔ execute split.** Planning (decide which agents run) is decoupled from
   execution (run them). This is what makes the system agent-forward: the UI can show
   the plan, let the user edit it, and only then execute — with steps passing data to
   each other.

---

## 3. The orchestration graph

Defined in [src/graph/workflow.py](../backend/src/graph/workflow.py) as a LangGraph
`StateGraph` with three nodes:

```
planner ──► router ──► response ──► END
```

- **planner_node** — calls the LLM with the planner prompt + agent manifest and
  produces an ordered list of **steps**. Each step is
  `{ agent, action, parameters }`.
- **router_nodes** — executes the steps in order. Before running a step it resolves
  any `{{stepN.field}}` placeholders in the parameters against earlier steps' results,
  then dispatches to that agent's executor with the `WorkspaceContext`.
- **response_node** — the *response agent* summarizes all step results into a
  human-friendly markdown reply.

The shared `AgentState` ([src/graph/state.py](../backend/src/graph/state.py)) carries
`user_id`, `workspace_id`, the message, the plan, per-step results and the final
response through the graph.

### A step object

```json
{
  "agent": "report_agent",
  "action": "create_report",
  "parameters": {
    "title": "Resume Analysis",
    "content": "{{step0.analysis}}",
    "format": "markdown"
  }
}
```

`{{stepN.field}}` means "use the output of an earlier step." The UI visualizes these
as edges in the live step graph.

---

## 4. Request flows

| Flow | Endpoint(s) | What happens |
|------|-------------|--------------|
| **One-shot** | `POST /api/chat` | Runs the whole graph (plan + run + response) in a single call. Backward-compatible. |
| **Plan only** | `POST /api/plan` | Runs only the planner; returns `{ steps }` for preview/editing. No execution. |
| **Run approved** | `POST /api/run` | Executes a (possibly user-edited) `{ steps }` list and returns `{ results, response, run_id }`. |
| **Live stream** | `POST /api/chat/stream` | SSE. Emits `plan_ready → (step_started → step_done)× → final_response → done` so the UI can animate the run. |
| **Direct invoke** | `POST /api/agents/{name}/run` | Calls one executor directly with `{ action, parameters, workspace_id }` — **no LLM**. Powers dashboard buttons ("Index workspace", "Daily summary"). |

Every run is persisted as a **Run** record so history can replay it.

---

## 5. API surface

All routers live under [backend/src/api/](../backend/src/api/). Base URL in local dev:
`http://localhost:8001` (the Docker compose service publishes `8000`).

- **Auth / user:** `POST /api/auth/signup`, `POST /api/auth/login`, `GET /api/me`
- **Workspaces:** `GET/POST /api/workspaces`, `PATCH/DELETE /api/workspaces/{id}`
- **Files:** `GET /api/workspaces/{id}/files` (tree), `GET .../files/{path}` (content),
  `DELETE .../files/{path}`, `POST .../upload` (files / folder / `.zip`, optional
  auto-index), `GET .../download/{path}`
- **Plan / execute:** `POST /api/plan`, `POST /api/run`, `POST /api/chat`,
  `POST /api/chat/stream` (SSE)
- **Agents:** `GET /api/agents` (manifest), `POST /api/agents/{name}/run`
- **Tasks:** `GET /api/tasks` (filter `status`, `sort`, `order`, `limit`, `offset`),
  `POST /api/tasks`, `PATCH/DELETE /api/tasks/{id}`
- **Reminders:** `GET/POST /api/reminders`, `DELETE /api/reminders/{id}`,
  `GET /api/reminders/due`, `GET /api/reminders/daily-summary`
- **Knowledge:** `GET /api/knowledge/status`, `POST /api/knowledge/search`,
  `POST /api/knowledge/index`
- **Memories:** `GET /api/memories`, `DELETE /api/memories/{id}`
- **Runs (history):** `GET /api/runs`, `GET /api/runs/{id}`
- **Dashboard:** `GET /api/dashboard` (counts + recent activity in one call)
- **Search:** `GET /api/search?q=` (documents + tasks + memories)

### Conventions

- **Envelope.** Every response is `{ "success": bool, "data": <payload>, "error":
  <string|null> }`. The auth token is at `data.access_token`; lists at `data.tasks`,
  etc. Exception handlers in [src/core/utils/responses.py](../backend/src/core/utils/responses.py)
  wrap HTTP errors, validation errors and unhandled exceptions into the same shape with
  real HTTP status codes.
- **Active workspace.** Passed as `workspace_id` — in the **body** for
  chat/plan/run/agent-invoke, as a **query param** `?workspace_id=` for REST
  dashboards, and in the **path** for file routes. If omitted it defaults to the user's
  first workspace.
- **Auth.** JWT bearer (`Authorization: Bearer <token>`). Every route verifies
  `workspace.user_id == current_user.id`.
- **CORS.** Enabled in `main.py`; allowed origins come from the `CORS_ORIGINS` env var.

---

## 6. Data model

SQLAlchemy models in [src/core/db/models.py](../backend/src/core/db/models.py). Every
entity except `User`/`Workspace` is scoped to `(user_id, workspace_id)`.

```
User         id, name, email, password_hash
Workspace    id, user_id, name, created_at                          (User has many)
Task         id, user_id, workspace_id, title, description, status, due_date, created_at
Reminder     id, user_id, workspace_id, message, remind_at, status, created_at
IndexedFile  id, user_id, workspace_id, file_path, indexed_at        (what's in the index)
Memory       id, user_id, workspace_id, text, type, created_at       (mirrors a Pinecone vector)
Run          id, user_id, workspace_id, message, plan, results, response, status, created_at
```

The `Memory` table is a **mirror** of the Pinecone vector so memories are listable and
deletable by id. `Run` is the audit log that powers the history timeline.

---

## 7. Storage backends

- **Relational DB** — SQLAlchemy (`DATABASE_URL`). Holds all structured entities above.
- **Vector store** — Pinecone ([src/core/vectorstore/](../backend/src/core/vectorstore/)).
  Used for both the knowledge index (RAG over workspace documents) and long-term
  memory. Namespaces are per-workspace (`ws_{workspace_id}_*`); embeddings via the
  configured embedding model, reranking via Cohere.
- **Workspace disk** — `workspaces/{workspace_id}/` holds the actual imported files.
  Path resolution and the no-escape sandbox live in
  [src/workspaces/resolver.py](../backend/src/workspaces/resolver.py) and
  [src/core/utils/workspace.py](../backend/src/core/utils/workspace.py).

---

## 8. LLM clients

[src/core/llm/](../backend/src/core/llm/) wraps Anthropic Claude, OpenAI and
OpenRouter. The active model is configured via env (`MODEL_NAME` / `OPENROUTER_MODEL`).
Each agent's behavior is steered by a dedicated prompt in
[src/prompts/](../backend/src/prompts/).

---

## 9. Configuration

All settings come from environment variables, loaded by
[src/core/config/settings.py](../backend/src/core/config/settings.py) from
`backend/.env`:

| Var | Purpose |
|-----|---------|
| `APP_NAME` | App title |
| `DATABASE_URL` | SQLAlchemy connection string |
| `JWT_SECRET_KEY`, `JWT_ALGORITHM`, `ACCESS_TOKEN_EXPIRE_MINUTES` | Auth |
| `ANTHROPIC_API_KEY`, `MODEL_NAME` | Claude |
| `OPENROUTER_API_KEY`, `OPENROUTER_MODEL` | OpenRouter |
| `COHERE_API_KEY` | Reranking |
| `PINECONE_API_KEY`, `PINECONE_INDEX_NAME` | Vector store |
| `WORKSPACE_DIR`, `WORKSPACES_ROOT` | Disk layout |
| `CORS_ORIGINS` | Comma-separated allowed origins (default `http://localhost:3000`) |
