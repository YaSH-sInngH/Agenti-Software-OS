from src.agents.response_agent.service import (
    ResponseService
)


def response_agent_executor(
    message: str,
    result: dict
):

    return ResponseService.generate(
        message,
        result
    )
