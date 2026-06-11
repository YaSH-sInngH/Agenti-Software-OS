from src.core.vectorstore.embeddings import generate_embedding
from src.core.vectorstore.pinecone_client import index
from src.core.vectorstore.namespaces import knowledge_namespace


def retrieve_chunks(
    query: str,
    workspace_id: int,
    file_path: str = None,
    top_k: int = 5
):

    embedding = generate_embedding(
        query,
        input_type="search_query"
    )
    query_params = {
        "vector": embedding,
        "top_k": top_k,
        "include_metadata": True,
        "namespace": knowledge_namespace(workspace_id)
    }
    if file_path:
        query_params["filter"] = {
            "file_path": file_path
        }

    results = index.query(**query_params)

    return results.matches
