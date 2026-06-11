from pydantic import BaseModel


class KnowledgeSearchRequest(BaseModel):
    query: str
    top_k: int = 10


class KnowledgeIndexRequest(BaseModel):
    file_path: str
