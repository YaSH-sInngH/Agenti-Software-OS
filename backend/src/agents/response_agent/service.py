import json

from src.llm.claude import llm
from src.prompts.response_agent_prompt import (
    RESPONSE_AGENT_PROMPT
)


class ResponseService:

    @staticmethod
    def generate(
        message: str,
        results
    ):

        raw = json.dumps(
            results,
            indent=2,
            default=str
        )

        prompt = f"""
{RESPONSE_AGENT_PROMPT}

User Request:

{message}

Agent Results:

{raw}
"""

        response = llm.invoke(
            prompt
        )

        return response.content
