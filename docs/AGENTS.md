# The Agents — Workspace OS's "team"

Workspace OS ships with **12 specialist agents**. They are visible first-class
citizens: the cockpit renders them as a live roster, the planner composes them into
multi-step plans, and each one's output gets a purpose-built result card.

Every agent lives in its own folder under
[backend/src/agents/](../backend/src/agents/) and follows the same shape:

```
agents/<name>_agent/
  executor.py   # dispatches an `action` (+ parameters + WorkspaceContext) to the right call
  service.py    # the real work (LLM calls, file IO, vector ops, HTTP, …)
  tools.py      # (some agents) lower-level helpers
```

The structured metadata for all of them — names, icons, scopes, actions and
parameters — is the single source of truth in
[backend/src/agents/manifest.py](../backend/src/agents/manifest.py), served at
`GET /api/agents`. It is kept in sync with the **executors**, not the planner prompt.

## Scopes

Each agent declares a **scope** that tells the user (and the UI badge color) how far
its reach extends:

| Scope | Meaning |
|-------|---------|
| `workspace` | Reads/writes the active workspace — files, index, tasks, memory. |
| `web` | Reaches out to the internet. |
| `system` | Runs sandboxed, allowlisted shell commands in the workspace dir. |

## Agent states

The roster and step nodes render five states: `idle` (neutral), `queued`, `working`
(animated/pulsing), `done` (green/check), `error` (red).

---

## The roster

| # | Agent | Icon | Scope | What it does |
|---|-------|------|-------|--------------|
| 1 | **File Agent** | folder | workspace | Create / read / write / list files |
| 2 | **Terminal Agent** | terminal | system | Run allowlisted shell commands in the workspace |
| 3 | **Document Agent** | file-text | workspace | Read & summarize docs (pdf / docx / txt) |
| 4 | **Memory Agent** | brain | workspace | Store & recall long-term memories |
| 5 | **Knowledge Agent** | book-open | workspace | Index docs & answer questions over them (RAG) |
| 6 | **Task Agent** | check-square | workspace | Manage to-dos |
| 7 | **Browser Agent** | globe | web | Open sites, web search, scrape page data |
| 8 | **Indexer Agent** | database | workspace | Index the whole workspace; report index status |
| 9 | **Reminder Agent** | bell | workspace | Reminders + a daily briefing |
| 10 | **Report Agent** | file-bar-chart | workspace | Generate reports as md / pdf / excel |
| 11 | **Resume Agent** | users | workspace | Analyze & rank resumes in the workspace |
| 12 | **Codebase Agent** | code | workspace | Analyze a codebase's structure & tech stack |

---

## Actions per agent

These are the actions a planner step can target (`{ agent, action, parameters }`).

### 1. File Agent — `file_agent` · folder · workspace
- `create_folder(folder_name)` — create a folder in the workspace.
- `list_files()` — list files and folders at the workspace root.
- `write_file(filename, content)` — write text content to a file.
- `read_file(filename)` — read a text file's content.

### 2. Terminal Agent — `terminal_agent` · terminal · system
- `run_command(...)` — run an **allowlisted** shell command, cwd scoped to the
  workspace. Renders as a terminal block (stdout/stderr, exit code).

### 3. Document Agent — `document_agent` · file-text · workspace
- `read_document(...)` — extract text from a document.
- `summarize_document(...)` — summarize a document with the LLM.

### 4. Memory Agent — `memory_agent` · brain · workspace
- `store_memory(...)` — save a memory.
- `retrieve_memory(...)` — recall memories relevant to a query.

  Memories are written both to Pinecone (vector) and the `Memory` mirror table so they
  are listable/deletable from the Memory dashboard.

### 5. Knowledge Agent — `knowledge_agent` · book-open · workspace (RAG)
- `index_document(...)` — chunk, embed and index a single document.
- `ask_document(...)` — answer a question about one specific document.
- `ask_workspace(...)` — answer a question across all indexed documents.
- `search_workspace(...)` — find which documents match a topic (no answer); renders as
  result cards with relevance score bars.
- `delete_document(...)` — remove a document from the index.
- `reindex_document(...)` — delete and re-index a document.

### 6. Task Agent — `task_agent` · check-square · workspace
- `create_task(title, description?, due_date?)`
- `list_tasks()`
- `update_task(...)` — update a task by title or id.
- `complete_task(...)` — mark a task complete.
- `delete_task(...)`

### 7. Browser Agent — `browser_agent` · globe · **web**
- `open_website(url)` — open a URL.
- `web_search(query)` — search the web.
- `extract_data(selector)` — extract elements matching a CSS selector from a page.

### 8. Indexer Agent — `indexer_agent` · database · workspace
- `index_workspace()` — index new or changed files.
- `reindex_workspace()` — force re-index of every supported file.
- `index_workspace_background()` — start indexing in the background.
- `index_status()` — list which files are indexed.

### 9. Reminder Agent — `reminder_agent` · bell · workspace
- `create_reminder(...)`
- `list_reminders()`
- `delete_reminder(...)` — by text or id.
- `due_reminders()` — reminders due now.
- `daily_summary()` — tasks and reminders due today (the "good morning" briefing).

### 10. Report Agent — `report_agent` · file-bar-chart · workspace
- `generate_report(...)` — LLM-write a report about a topic and save it.
- `create_report(...)` — save provided content as a report file (md / pdf / xlsx),
  rendered as a "report generated" card with a download button.

### 11. Resume Agent — `resume_agent` · users · workspace
- `analyze_resumes(job_description?)` — analyze resumes, optionally against a job
  description; renders as a candidate ranking table.

### 12. Codebase Agent — `codebase_agent` · code · workspace
- `analyze_codebase(...)` — summarize structure, tech stack and improvements; renders
  as a file tree + tech-stack badges + analysis text.

---

## How agents get invoked

1. **Through a plan (LLM).** The planner emits steps; the router resolves
   `{{stepN.field}}` placeholders and calls each executor with the active
   `WorkspaceContext`. See [ARCHITECTURE.md](ARCHITECTURE.md#3-the-orchestration-graph).
2. **Directly (no LLM).** `POST /api/agents/{name}/run { action, parameters,
   workspace_id }` dispatches straight to an executor — this powers the one-click
   dashboard buttons ("Index workspace", "Analyze codebase", "Daily summary").

## Result renderers

Every agent's output is rendered as a **purpose-built card**, never raw JSON — terminal
block, knowledge cards with score bars, task checklist, web-result links, report
download, resume ranking table, codebase tree + stack badges, memory chips, etc. See
[FRONTEND.md](FRONTEND.md#per-agent-result-cards).
