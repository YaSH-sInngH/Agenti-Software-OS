import json
import re
from src.graph.state import AgentState
from src.llm.claude import llm
from src.agents.file_agent.executor import file_agent_executor
from src.agents.registry import AGENT_REGISTRY
from src.prompts.planner_prompt import PLANNER_PROMPT

def planner_node(state: AgentState) -> AgentState:

    prompt = f"""
{PLANNER_PROMPT}

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
    agent_name = plan.get("agent")
    executor = AGENT_REGISTRY.get(
        agent_name
    )
    if not executor:
        state["result"] = {
            "success": False,
            "message": f"Unknown agent: {agent_name}"
        }
        state["response"] = "Unknown agent"
        return state
    if agent_name == "memory_agent":
        result = executor(plan, state["user_id"])
    else:
        result = executor(plan)
    state["result"] = result
    state["response"] = (
        f"Executed {agent_name}"
    )
    return state