from src.agents.file_agent.executor import file_agent_executor
from src.agents.terminal_agent.executor import terminal_agent_executor

AGENT_REGISTRY = {
    "file_agent": file_agent_executor,
    "terminal_agent": terminal_agent_executor,
}