import json
import re
from datetime import date
from src.graph.state import AgentState
from src.graph.context import WorkspaceContext
from src.core.llm.claude import llm
from src.agents.file_agent.executor import file_agent_executor
from src.agents.registry import AGENT_REGISTRY
from src.agents.response_agent.executor import response_agent_executor
from src.prompts.planner_prompt import PLANNER_PROMPT

def planner_node(state: AgentState) -> AgentState:

    prompt = f"""
{PLANNER_PROMPT}

Today's date is {date.today().isoformat()}.
Use it to resolve relative dates like "tomorrow" or "next Friday" into an ISO date (YYYY-MM-DD).

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

    if isinstance(plan, dict) and "steps" in plan:
        state["steps"] = plan["steps"]
    else:
        state["steps"] = [plan]

    return state

PLACEHOLDER = re.compile(
    r"\{\{\s*step(\d+)(?:\.([\w\.]+))?\s*\}\}"
)

def resolve_placeholders(value, results):

    # Orchestrator: replace {{stepN}} / {{stepN.field.subfield}} in a step's
    # parameters with the corresponding value produced by an earlier step.

    if isinstance(value, dict):
        return {
            k: resolve_placeholders(v, results)
            for k, v in value.items()
        }

    if isinstance(value, list):
        return [
            resolve_placeholders(v, results)
            for v in value
        ]

    if not isinstance(value, str):
        return value

    def replace(match):

        index = int(match.group(1))
        path = match.group(2)

        if index >= len(results):
            return match.group(0)

        data = results[index].get("result")

        if path:
            for key in path.split("."):
                if isinstance(data, dict):
                    data = data.get(key)
                else:
                    data = None
                    break

        if isinstance(data, str):
            return data

        return json.dumps(data, default=str)

    return PLACEHOLDER.sub(replace, value)

def router_nodes(state: AgentState):

    steps = state.get("steps", [])

    context = WorkspaceContext(
        user_id=state["user_id"],
        workspace_id=state["workspace_id"],
    )

    results = []

    for step in steps:

        agent_name = step.get("agent")
        executor = AGENT_REGISTRY.get(agent_name)

        # Feed earlier step outputs into this step's parameters.
        resolved_step = dict(step)
        resolved_step["parameters"] = resolve_placeholders(
            step.get("parameters", {}),
            results,
        )

        if not executor:
            results.append({
                "agent": agent_name,
                "action": step.get("action"),
                "result": {
                    "success": False,
                    "message": f"Unknown agent: {agent_name}"
                }
            })
            continue

        result = executor(resolved_step, context)

        results.append({
            "agent": agent_name,
            "action": step.get("action"),
            "result": result
        })

    state["results"] = results

    return state

def response_node(state: AgentState):

    state["response"] = response_agent_executor(
        state["message"],
        state["results"]
    )

    return state