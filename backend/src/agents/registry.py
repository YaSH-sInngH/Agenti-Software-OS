from src.agents.file_agent.executor import file_agent_executor
from src.agents.terminal_agent.executor import terminal_agent_executor
from src.agents.memory_agent.executor import memory_agent_executor
from src.agents.document_agent.executor import document_agent_executor
from src.agents.knowledge_agent.executor import knowledge_agent_executor
from src.agents.task_agent.executor import task_agent_executor
from src.agents.browser_agent.executor import browser_agent_executor
from src.agents.indexer_agent.executor import indexer_agent_executor
from src.agents.reminder_agent.executor import reminder_agent_executor
from src.agents.report_agent.executor import report_agent_executor
from src.agents.resume_agent.executor import resume_agent_executor
from src.agents.codebase_agent.executor import codebase_agent_executor

AGENT_REGISTRY = {
    "file_agent": file_agent_executor,
    "terminal_agent": terminal_agent_executor,
    "memory_agent": memory_agent_executor,
    "document_agent": document_agent_executor,
    "knowledge_agent": knowledge_agent_executor,
    "task_agent": task_agent_executor,
    "browser_agent": browser_agent_executor,
    "indexer_agent": indexer_agent_executor,
    "reminder_agent": reminder_agent_executor,
    "report_agent": report_agent_executor,
    "resume_agent": resume_agent_executor,
    "codebase_agent": codebase_agent_executor,
}