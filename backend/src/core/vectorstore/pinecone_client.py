from pinecone import Pinecone
from src.core.config.settings import settings

pc = Pinecone (
    api_key=settings.PINECONE_API_KEY
)

index = pc.Index(
    settings.PINECONE_INDEX_NAME
)