from langgraph.graph import StateGraph, END
from src.graph.state import AgentState
from src.graph.nodes import planner_node, router_nodes

builder = StateGraph(AgentState)

builder.add_node(
    "planner",
    planner_node,
)

builder.add_node(
    "router",
    router_nodes,
)

builder.set_entry_point("planner")

builder.add_edge("planner", "router")

builder.add_edge("router", END)

graph = builder.compile()