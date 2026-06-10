import uuid

from src.agents.document_agent.tools import read_document
from src.agents.knowledge_agent.chunker import chunk_text
from src.agents.knowledge_agent.retriever import retrieve_chunks

from src.vectorstore.embeddings import generate_embedding
from src.vectorstore.pinecone_client import index

from src.utils.workspace import resolve_workspace_file

from src.llm.claude import llm

class KnowledgeService:
    @staticmethod
    def index_document(
        file_path: str,
        user_id: int
    ):

        path = resolve_workspace_file(
            file_path
        )

        text = read_document(path)

        chunks = chunk_text(text)

        vectors = []

        for chunk in chunks:

            embedding = (
                generate_embedding(chunk)
            )

            vectors.append(
                {
                    "id": str(uuid.uuid4()),
                    "values": embedding,
                    "metadata": {
                        "text": chunk,
                        "file_path": file_path
                    }
                }
            )

        index.upsert(
            vectors=vectors,
            namespace=f"user_{user_id}_knowledge"
        )

        return {
            "success": True,
            "chunks": len(chunks)
        }

    @staticmethod
    def ask_document(
        file_path: str,
        question: str,
        user_id: int
    ):

        matches = retrieve_chunks(
            question,
            user_id
        )

        context = "\n\n".join(
            [
                m.metadata["text"]
                for m in matches
            ]
        )

        prompt = f"""
Answer using only the context.

Context:

{context}

Question:

{question}
"""

        result = llm.invoke(
            prompt
        )

        return {
            "success": True,
            "answer": result.content
        }