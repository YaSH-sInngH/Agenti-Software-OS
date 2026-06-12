# Frontend — the Cockpit

The frontend is a **Next.js (App Router) + TypeScript + Tailwind v4** app in
[frontend/](../frontend/). Its design north star is *"a mission-control cockpit for a
team of AI workers"* — the user always sees what the agents are doing and stays in
control. Dark theme by default, high information density, status color everywhere
(idle / working / done / error / partial).

It binds to the backend described in [ARCHITECTURE.md](ARCHITECTURE.md) and renders the
12 agents in [AGENTS.md](AGENTS.md).

---

## 1. Stack

| Concern | Choice |
|---------|--------|
| Framework | Next.js 16 (App Router), React 19, TypeScript |
| Styling | Tailwind CSS v4 |
| Server state | TanStack Query (`@tanstack/react-query`) |
| Client state | Zustand |
| Step graph | React Flow (`@xyflow/react`) |
| Markdown | `react-markdown` |
| Icons | `lucide-react` |
| Live runs | A small SSE client ([src/lib/sse.ts](../frontend/src/lib/sse.ts)) |

The API base URL is read from `NEXT_PUBLIC_API_URL` (default `http://localhost:8001`).
All requests go through [src/lib/api.ts](../frontend/src/lib/api.ts), which attaches the
JWT bearer token and **unwraps the `{ success, data, error }` envelope** so callers get
`data` directly.

---

## 2. Project layout

```
frontend/src/
  app/                         # App Router routes
    layout.tsx, providers.tsx  # root shell: Query client, theme, toaster
    page.tsx                   # entry / redirect
    login/  register/          # auth pages
    workspaces/                # "This PC" — workspace grid
    w/[workspaceId]/           # the cockpit, scoped to one workspace
      layout.tsx               #   shared shell (icon nav + ⌘K search)
      page.tsx                 #   the cockpit (command bar + plan + live run)
      files/                   #   workspace explorer
      knowledge/               #   knowledge / indexer status + search + Q&A
      memory/                  #   memory chips
      reminders/               #   reminders + daily briefing
      tasks/                   #   tasks dashboard
      runs/  runs/[runId]/     #   run history list + replay
      settings/                #   profile + theme
  components/
    cockpit/                   # CommandBar, PlanSteps, StepGraph, RunView,
                               # RunResponse, ResultCard, AgentRoster, TopBar,
                               # SearchOverlay, parts
    dash/                      # DashShell, States (empty/loading/error)
    AuthForm, FileTree, IconNav, Loader, Toaster
  hooks/                       # useRequireAuth, useRun, useWorkspaceId
  lib/                         # api, sse, types, icons, cn
  stores/                      # auth, theme, toast, ui  (Zustand)
```

---

## 3. The three big ideas, in the UI

### Multi-workspace ("This PC")
`/workspaces` is a grid of workspace cards (name, created date, quick stats) with
create / rename / delete and an empty state ("Create your first workspace"). Opening one
routes into `/w/[workspaceId]/...`, which makes that workspace **active** — its id is
read by [useWorkspaceId](../frontend/src/hooks/useWorkspaceId.ts) and sent as
`workspace_id` on every call. Switching workspaces re-scopes everything.

### Agent-forward roster
The cockpit's left rail is the **Agent Roster**
([AgentRoster.tsx](../frontend/src/components/cockpit/AgentRoster.tsx)), backed by
`GET /api/agents`. All 12 agents show with icon + scope badge + live status; during a
run they light up idle → working → done/error.

### Plan → approve → execute
The signature flow lives in the cockpit center:

1. **Command bar** ([CommandBar.tsx](../frontend/src/components/cockpit/CommandBar.tsx)) —
   the user types a request (⌘K reachable).
2. **Plan preview** — `POST /api/plan` returns ordered steps, rendered as editable
   agent chips ([PlanSteps.tsx](../frontend/src/components/cockpit/PlanSteps.tsx)) with
   `{{stepN.field}}` data-flow links. User can edit / remove / reorder, then **Approve**
   or **Cancel**.
3. **Live run** — on approve, `POST /api/chat/stream` (SSE) drives the run.
   [useRun](../frontend/src/hooks/useRun.ts) consumes the event sequence and updates
   state; [RunView](../frontend/src/components/cockpit/RunView.tsx) renders it.

---

## 4. The live run panel

Driven by the SSE event sequence:

```
plan_ready → (step_started → step_done)× per step → final_response → done
```

Each `step_*` event carries `index`, `agent`, `action`, and (on done) `result`. The
panel offers two views of the same run:

- **List view** — steps as a vertical pipeline of status chips with inline result
  cards.
- **Graph view** — a React Flow node graph
  ([StepGraph.tsx](../frontend/src/components/cockpit/StepGraph.tsx)): nodes = agents/steps,
  edges = data flow, animating as events arrive.

When the run finishes it collapses into a friendly markdown
**[RunResponse](../frontend/src/components/cockpit/RunResponse.tsx)** with expandable
step details.

---

## 5. Per-agent result cards

Each agent's output renders as a purpose-built card via
[ResultCard.tsx](../frontend/src/components/cockpit/ResultCard.tsx) (and `parts.tsx`),
never raw JSON:

| Agent | Card |
|-------|------|
| File | created/updated path confirmation / file grid |
| Terminal | terminal block (stdout/stderr, exit code) |
| Document | title + summary text |
| Knowledge | search result cards with **relevance score bars**; Q&A with source citations |
| Task | task checklist (checkbox, title, due-date chip) |
| Browser | web-result link cards / extracted data list |
| Indexer | indexed-files list + counts |
| Reminder | reminder list / daily briefing card |
| Report | "report generated" card with a **download** button |
| Resume | candidate **ranking table** |
| Codebase | file tree + tech-stack badges + analysis text |
| Memory | memory chips by type |

---

## 6. Dashboards & explorer

Built on the shared [DashShell](../frontend/src/components/dash/DashShell.tsx) +
[States](../frontend/src/components/dash/States.tsx) (empty / loading / error):

- **Tasks** — board/list, complete/delete, due-date chips, filter/sort.
- **Reminders / Daily briefing** — "good morning" card (today's tasks + reminders).
- **Memory** — chips grouped by type (user / project / workspace), delete.
- **Knowledge / Indexer** — what's indexed, re-index, search box (score bars) + Q&A box.
- **Workspace Explorer** — [FileTree](../frontend/src/components/FileTree.tsx) with
  drag-drop / folder / `.zip` import → upload endpoint → auto-index; document viewer;
  per-file "Index this"; download / delete.
- **Run history** — list of past runs; each replays its step graph + results.
- **Settings** — profile + dark/light theme (theme in the Zustand
  [theme store](../frontend/src/stores/theme.ts)).

Direct-agent buttons ("Index workspace", "Analyze codebase", "Daily summary") call
`POST /api/agents/{name}/run` — no LLM.

---

## 7. State & auth

- **Zustand stores** ([src/stores/](../frontend/src/stores/)): `auth` (token + user),
  `theme`, `toast`, `ui`.
- **Auth guard** — [useRequireAuth](../frontend/src/hooks/useRequireAuth.ts) protects
  workspace routes; the token is stored in `localStorage` and attached by `api.ts`.
- **Toasts** — [Toaster](../frontend/src/components/Toaster.tsx) surfaces actions
  (uploaded, indexed, task completed) and errors (rate limit, file not found).
- **Global search** — ⌘K
  [SearchOverlay](../frontend/src/components/cockpit/SearchOverlay.tsx) → `GET
  /api/search?q=` across documents, tasks and memories.

---

## 8. Running it

```bash
cd frontend
npm install
npm run dev        # http://localhost:3000
```

Set `NEXT_PUBLIC_API_URL` in `frontend/.env.local` to point at the backend. Or run the
whole stack with Docker — see the root [README](../README.md).
