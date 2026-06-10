from langchain_anthropic import ChatAnthropic
from src.config.settings import settings

llm = ChatAnthropic(
    model=settings.MODEL_NAME,
    anthropic_api_key=settings.ANTHROPIC_API_KEY,
    temperature=0,
    max_tokens=2000,
)