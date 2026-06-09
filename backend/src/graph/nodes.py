import json
from src.graph.state import AgentState
from src.llm.claude import llm

def planner_node(state: AgentState) -> AgentState:
    prompt = f"""
You are an OS Assistant Planner.

Convert user requests into JSON.

Allowed agents:

file_agent
terminal_agent
document_agent
memory_agent

Return ONLY JSON.

Example:

{{
    "agent":"file_agent",
    "action":"create_folder",
    "parameters": {{
        "folder_name":"reports"
    }}
}}

User Request:

{state["message"]}
"""

    result = llm.invoke(prompt)

    content = result.content

    try:
        plan = json.loads(content)
    except Exception:
        plan = {
            "agent": "unknown",
            "action": "unknown",
            "parameters": {},
        }

    state["plan"] = plan

    return state

def router_nodes(state: AgentState):
    state["response"] = (
        f"Planner selected: "
        f"{state["plan"]}"
    )
    return state