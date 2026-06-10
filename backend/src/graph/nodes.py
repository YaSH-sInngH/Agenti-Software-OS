import json
import re
from datetime import date
from src.graph.state import AgentState
from src.llm.claude import llm
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

def router_nodes(state: AgentState):

    steps = state.get("steps", [])
    user_id = state["user_id"]

    results = []

    for step in steps:

        agent_name = step.get("agent")
        executor = AGENT_REGISTRY.get(agent_name)

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

        if agent_name in ("memory_agent", "knowledge_agent", "task_agent"):
            result = executor(step, user_id)
        else:
            result = executor(step)

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