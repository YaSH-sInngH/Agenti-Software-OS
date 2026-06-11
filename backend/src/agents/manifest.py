"""
Structured agent metadata registry.

Single source of truth for what each agent can do — powers GET /api/agents,
the dashboard direct-invoke buttons, and the frontend agent roster. Kept in
sync with the actual executors (NOT the planner prompt, which may list
aspirational actions the executors don't implement yet).

Scopes:
  workspace - reads/writes the active workspace (files, index, tasks, memory)
  web       - reaches out to the internet
  system    - runs sandboxed shell commands in the workspace dir
"""


def _p(name, type="string", required=False, description="", enum=None):
    param = {
        "name": name,
        "type": type,
        "required": required,
        "description": description,
    }
    if enum:
        param["enum"] = enum
    return param


AGENT_MANIFEST = [
    {
        "name": "file_agent",
        "description": "Create, read, write and list files in the workspace.",
        "icon": "folder",
        "scope": "workspace",
        "actions": [
            {
                "name": "create_folder",
                "description": "Create a folder in the workspace.",
                "parameters": [_p("folder_name", required=True)],
            },
            {
                "name": "list_files",
                "description": "List files and folders at the workspace root.",
                "parameters": [],
            },
            {
                "name": "write_file",
                "description": "Write text content to a file.",
                "parameters": [
                    _p("filename", required=True),
                    _p("content", required=True),
                ],
            },
            {
                "name": "read_file",
                "description": "Read a text file's content.",
                "parameters": [_p("filename", required=True)],
            },
        ],
    },
    {
        "name": "terminal_agent",
        "description": "Run allowlisted shell commands scoped to the workspace.",
        "icon": "terminal",
        "scope": "system",
        "actions": [
            {
                "name": "run_command",
                "description": "Run an allowlisted shell command.",
                "parameters": [_p("command", required=True)],
            },
        ],
    },
    {
        "name": "document_agent",
        "description": "Read and summarize documents (pdf, docx, txt).",
        "icon": "file-text",
        "scope": "workspace",
        "actions": [
            {
                "name": "read_document",
                "description": "Extract text from a document.",
                "parameters": [_p("file_path", required=True)],
            },
            {
                "name": "summarize_document",
                "description": "Summarize a document with the LLM.",
                "parameters": [_p("file_path", required=True)],
            },
        ],
    },
    {
        "name": "memory_agent",
        "description": "Store and recall long-term memories for this workspace.",
        "icon": "brain",
        "scope": "workspace",
        "actions": [
            {
                "name": "store_memory",
                "description": "Save a memory.",
                "parameters": [
                    _p("memory", required=True),
                    _p(
                        "memory_type",
                        description="Defaults to user_memory.",
                        enum=["user_memory", "project_memory", "workspace_memory"],
                    ),
                ],
            },
            {
                "name": "retrieve_memory",
                "description": "Recall memories relevant to a query.",
                "parameters": [_p("query", required=True)],
            },
        ],
    },
    {
        "name": "knowledge_agent",
        "description": "Index documents and answer questions over them (RAG).",
        "icon": "book-open",
        "scope": "workspace",
        "actions": [
            {
                "name": "index_document",
                "description": "Chunk, embed and index a single document.",
                "parameters": [_p("file_path", required=True)],
            },
            {
                "name": "ask_document",
                "description": "Answer a question about one specific document.",
                "parameters": [
                    _p("file_path", required=True),
                    _p("question", required=True),
                ],
            },
            {
                "name": "ask_workspace",
                "description": "Answer a question across all indexed documents.",
                "parameters": [_p("question", required=True)],
            },
            {
                "name": "search_workspace",
                "description": "Find which documents match a topic (no answer).",
                "parameters": [_p("query", required=True)],
            },
            {
                "name": "delete_document",
                "description": "Remove a document from the knowledge index.",
                "parameters": [_p("file_path", required=True)],
            },
            {
                "name": "reindex_document",
                "description": "Delete and re-index a document.",
                "parameters": [_p("file_path", required=True)],
            },
        ],
    },
    {
        "name": "task_agent",
        "description": "Manage tasks (create, list, update, complete, delete).",
        "icon": "check-square",
        "scope": "workspace",
        "actions": [
            {
                "name": "create_task",
                "description": "Create a task.",
                "parameters": [
                    _p("title", required=True),
                    _p("description"),
                    _p("due_date", description="ISO date YYYY-MM-DD."),
                ],
            },
            {
                "name": "list_tasks",
                "description": "List all tasks in the workspace.",
                "parameters": [],
            },
            {
                "name": "update_task",
                "description": "Update a task by title or id.",
                "parameters": [
                    _p("task", description="Task title to match."),
                    _p("task_id", type="integer"),
                    _p("title"),
                    _p("description"),
                    _p("due_date"),
                    _p("status"),
                ],
            },
            {
                "name": "complete_task",
                "description": "Mark a task complete.",
                "parameters": [
                    _p("task", description="Task title to match."),
                    _p("task_id", type="integer"),
                ],
            },
            {
                "name": "delete_task",
                "description": "Delete a task.",
                "parameters": [
                    _p("task", description="Task title to match."),
                    _p("task_id", type="integer"),
                ],
            },
        ],
    },
    {
        "name": "browser_agent",
        "description": "Open websites, search the web and extract page data.",
        "icon": "globe",
        "scope": "web",
        "actions": [
            {
                "name": "open_website",
                "description": "Open a URL.",
                "parameters": [_p("url", required=True)],
            },
            {
                "name": "web_search",
                "description": "Search the web for a query.",
                "parameters": [_p("query", required=True)],
            },
            {
                "name": "extract_data",
                "description": "Extract elements matching a CSS selector from a page.",
                "parameters": [
                    _p("url", required=True),
                    _p("selector", required=True, description="CSS selector."),
                ],
            },
        ],
    },
    {
        "name": "indexer_agent",
        "description": "Index the whole workspace and report index status.",
        "icon": "database",
        "scope": "workspace",
        "actions": [
            {
                "name": "index_workspace",
                "description": "Index new or changed files in the workspace.",
                "parameters": [],
            },
            {
                "name": "reindex_workspace",
                "description": "Force re-index of every supported file.",
                "parameters": [],
            },
            {
                "name": "index_workspace_background",
                "description": "Start workspace indexing in the background.",
                "parameters": [],
            },
            {
                "name": "index_status",
                "description": "List which files are indexed.",
                "parameters": [],
            },
        ],
    },
    {
        "name": "reminder_agent",
        "description": "Create reminders and produce a daily briefing.",
        "icon": "bell",
        "scope": "workspace",
        "actions": [
            {
                "name": "create_reminder",
                "description": "Create a reminder.",
                "parameters": [
                    _p("message", required=True),
                    _p("remind_at", description="ISO datetime."),
                ],
            },
            {
                "name": "list_reminders",
                "description": "List all reminders.",
                "parameters": [],
            },
            {
                "name": "delete_reminder",
                "description": "Delete a reminder by text or id.",
                "parameters": [
                    _p("reminder", description="Reminder text to match."),
                    _p("reminder_id", type="integer"),
                ],
            },
            {
                "name": "due_reminders",
                "description": "List reminders that are due now.",
                "parameters": [],
            },
            {
                "name": "daily_summary",
                "description": "Tasks and reminders due today.",
                "parameters": [],
            },
        ],
    },
    {
        "name": "report_agent",
        "description": "Generate reports as markdown, pdf or excel.",
        "icon": "file-bar-chart",
        "scope": "workspace",
        "actions": [
            {
                "name": "generate_report",
                "description": "LLM-write a report about a topic and save it.",
                "parameters": [
                    _p("topic", required=True),
                    _p("format", enum=["markdown", "pdf", "excel"]),
                    _p("title"),
                ],
            },
            {
                "name": "create_report",
                "description": "Save provided content as a report file.",
                "parameters": [
                    _p("title", required=True),
                    _p("content", required=True),
                    _p("format", enum=["markdown", "pdf", "excel"]),
                ],
            },
        ],
    },
    {
        "name": "resume_agent",
        "description": "Analyze and rank resumes in the workspace.",
        "icon": "users",
        "scope": "workspace",
        "actions": [
            {
                "name": "analyze_resumes",
                "description": "Analyze resumes, optionally against a job description.",
                "parameters": [_p("job_description")],
            },
        ],
    },
    {
        "name": "codebase_agent",
        "description": "Analyze a codebase's structure and tech stack.",
        "icon": "code",
        "scope": "workspace",
        "actions": [
            {
                "name": "analyze_codebase",
                "description": "Summarize structure, stack and improvements.",
                "parameters": [
                    _p("path", description="Optional folder inside the workspace."),
                ],
            },
        ],
    },
]


_BY_NAME = {agent["name"]: agent for agent in AGENT_MANIFEST}


def get_manifest():
    return AGENT_MANIFEST


def get_agent(name: str):
    return _BY_NAME.get(name)
