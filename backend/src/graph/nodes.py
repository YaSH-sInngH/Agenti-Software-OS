import json
import re
from src.graph.state import AgentState
from src.llm.claude import llm
from src.agents.file_agent.executor import file_agent_executor

def planner_node(state: AgentState) -> AgentState:

    prompt = f"""
You are an AI OS Assistant Planner.

Your job is to convert a user request into a structured execution plan.

IMPORTANT RULES:

1. Return ONLY valid JSON.
2. Do NOT return markdown.
3. Do NOT use ```json blocks.
4. Do NOT explain anything.
5. Do NOT add extra text.
6. Return exactly one JSON object.

AVAILABLE AGENTS:

1. file_agent
2. terminal_agent
3. document_agent
4. memory_agent

FILE AGENT ACTIONS:

- create_folder
- list_files
- write_file
- read_file
- delete_file
- search_files

SCHEMA:

{{
    "agent": "<agent_name>",
    "action": "<action_name>",
    "parameters": {{}}
}}

EXAMPLES

User: Create folder Reports

{{
    "agent": "file_agent",
    "action": "create_folder",
    "parameters": {{
        "folder_name": "Reports"
    }}
}}

User: Create a folder called invoices

{{
    "agent": "file_agent",
    "action": "create_folder",
    "parameters": {{
        "folder_name": "invoices"
    }}
}}

User: Show all files

{{
    "agent": "file_agent",
    "action": "list_files",
    "parameters": {{}}
}}

User: List files in workspace

{{
    "agent": "file_agent",
    "action": "list_files",
    "parameters": {{}}
}}

User: Create a file notes.txt with content Hello World

{{
    "agent": "file_agent",
    "action": "write_file",
    "parameters": {{
        "filename": "notes.txt",
        "content": "Hello World"
    }}
}}

User: Write 'My first note' into notes.txt

{{
    "agent": "file_agent",
    "action": "write_file",
    "parameters": {{
        "filename": "notes.txt",
        "content": "My first note"
    }}
}}

User: Read notes.txt

{{
    "agent": "file_agent",
    "action": "read_file",
    "parameters": {{
        "filename": "notes.txt"
    }}
}}

User: Open and read resume.pdf

{{
    "agent": "document_agent",
    "action": "read_document",
    "parameters": {{
        "filename": "resume.pdf"
    }}
}}

User: Remember my project folder is projects/resume-app

{{
    "agent": "memory_agent",
    "action": "store_memory",
    "parameters": {{
        "memory": "My project folder is projects/resume-app"
    }}
}}

User: Run git status

{{
    "agent": "terminal_agent",
    "action": "run_command",
    "parameters": {{
        "command": "git status"
    }}
}}

If the request cannot be mapped to an available action, return:

{{
    "agent": "unknown",
    "action": "unknown",
    "parameters": {{}}
}}

User Request:

{state["message"]}
"""

    result = llm.invoke(prompt)

    print("LLM Result:========", result.content)

    content = result.content

    try:

        json_match = re.search(
            r"\{.*\}",
            content,
            re.DOTALL
        )

        if not json_match:
            raise ValueError("No JSON found")

        plan = json.loads(
            json_match.group()
        )

    except Exception as e:

        print("Planner Parse Error:", e)

        plan = {
            "agent": "unknown",
            "action": "unknown",
            "parameters": {},
        }

    state["plan"] = plan

    return state

def router_nodes(state: AgentState):

    plan = state["plan"]
    agent = plan.get("agent")
    if agent == "file_agent":
        result = file_agent_executor(
            plan
        )
        state["result"] = result
        state["response"] = (
            f"Executed file agent"
        )
        return state

    state["response"] = (
        "Unknown agent"
    )
    return state