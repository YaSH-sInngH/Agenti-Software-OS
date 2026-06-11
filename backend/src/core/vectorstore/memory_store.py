import uuid
from datetime import datetime
from src.core.vectorstore.embeddings import generate_embedding
from src.core.vectorstore.pinecone_client import index
from src.core.vectorstore.namespaces import memory_namespace

def store_memory(
        user_id: int,
        workspace_id: int,
        memory: str,
        memory_type: str = "user_memory",
):
    embedding = generate_embedding(memory)
    memory_id = str(uuid.uuid4())
    index.upsert(
        vectors=[
            {
                "id": memory_id,
                "values": embedding,
                "metadata": {
                    "user_id": user_id,
                    "workspace_id": workspace_id,
                    "memory": memory,
                    "memory_type": memory_type,
                    "created_at": datetime.utcnow().isoformat()
                }
            }
        ],
        namespace=memory_namespace(workspace_id),
    )
    return {
        "success": True,
        "memory_id": memory_id
    }

def retrieve_memory(
        user_id: int,
        workspace_id: int,
        query: str,
        top_k: int = 5
):
    query_embedding = generate_embedding(query)
    result = index.query(
        vector=query_embedding,
        top_k=top_k,
        include_metadata=True,
        namespace=memory_namespace(workspace_id),
    )

    memories = []
    for match in result.matches:
        memories.append(
            {
                "score": match.score,
                "memory": match.metadata.get(
                    "memory"
                ),
                "memory_type": match.metadata.get(
                    "memory_type"
                )
            }
        )

    return {
        "success": True,
        "memories": memories
    }


def delete_memory_vector(workspace_id: int, vector_id: str):
    index.delete(
        ids=[vector_id],
        namespace=memory_namespace(workspace_id),
    )
    return {"success": True}
