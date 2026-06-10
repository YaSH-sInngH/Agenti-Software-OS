from src.agents.file_agent.executor import file_agent_executor
from src.agents.terminal_agent.executor import terminal_agent_executor
from src.agents.memory_agent.executor import memory_agent_executor
from src.agents.document_agent.executor import document_agent_executor
from src.agents.knowledge_agent.executor import knowledge_agent_executor
from src.agents.task_agent.executor import task_agent_executor

AGENT_REGISTRY = {
    "file_agent": file_agent_executor,
    "terminal_agent": terminal_agent_executor,
    "memory_agent": memory_agent_executor,
    "document_agent": document_agent_executor,
    "knowledge_agent": knowledge_agent_executor,
    "task_agent": task_agent_executor,
}