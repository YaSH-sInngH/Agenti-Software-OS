import uuid
from datetime import datetime
from src.vectorstore.embeddings import generate_embedding
from src.vectorstore.pinecone_client import index

def store_memory(
        user_id: int,
        memory: str,
        memory_type: str = "user_memory",
): 
    embedding = generate_embedding(memory)
    memory_id = str(uuid.uuid4())
    index.upsert(
        vector=[
            {
                "id": memory_id,
                "values": embedding,
                "metadata": {
                    "user_id": user_id,
                    "memory": memory,
                    "memory_type": memory_type,
                    "created_at": datetime.utcnow().isoformat()
                }
            }
        ]
    )
    return {
        "success": True,
        "memory_id": memory_id
    }

def retrieve_memory(
        user_id: int,
        query: str,
        top_k: int = 5
): 
    query_embedding = generate_embedding(query)
    result = index.query(
        vector=query_embedding,
        top_k=top_k,
        include_metadata=True,
        filter={
            "user_id": user_id
        }
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