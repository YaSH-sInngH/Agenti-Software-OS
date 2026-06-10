import json

from src.llm.claude import llm
from src.prompts.response_agent_prompt import (
    RESPONSE_AGENT_PROMPT
)


class ResponseService:

    @staticmethod
    def generate(
        message: str,
        result: dict
    ):

        raw = json.dumps(
            result,
            indent=2,
            default=str
        )

        prompt = f"""
{RESPONSE_AGENT_PROMPT}

User Request:

{message}

Agent Result:

{raw}
"""

        response = llm.invoke(
            prompt
        )

        return response.content
