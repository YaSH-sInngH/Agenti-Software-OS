import uuid

from src.agents.document_agent.tools import read_document
from src.agents.knowledge_agent.chunker import chunk_text
from src.agents.knowledge_agent.retriever import retrieve_chunks

from src.core.vectorstore.embeddings import generate_embeddings
from src.core.vectorstore.pinecone_client import index
from src.core.vectorstore.namespaces import knowledge_namespace

from src.core.utils.workspace import resolve_workspace_file

from src.core.llm.claude import llm

class KnowledgeService:
    @staticmethod
    def index_document(
        file_path: str,
        workspace_id: int
    ):

        path = resolve_workspace_file(
            workspace_id,
            file_path
        )

        text = read_document(path)

        chunks = chunk_text(text)

        # Batch-embed all chunks (few calls), then build vectors.
        embeddings = generate_embeddings(chunks)

        vectors = [
            {
                "id": str(uuid.uuid4()),
                "values": embedding,
                "metadata": {
                    "text": chunk,
                    "file_path": file_path,
                },
            }
            for chunk, embedding in zip(chunks, embeddings)
        ]

        # Upsert in batches to stay under Pinecone request-size limits.
        namespace = knowledge_namespace(workspace_id)
        for start in range(0, len(vectors), 100):
            index.upsert(
                vectors=vectors[start:start + 100],
                namespace=namespace,
            )

        return {
            "success": True,
            "file_path": file_path,
            "chunks": len(chunks)
        }

    @staticmethod
    def ask_document(
        file_path: str,
        question: str,
        workspace_id: int
    ):

        matches = retrieve_chunks(
            question,
            workspace_id,
            file_path=file_path
        )

        context = "\n\n".join(
            [
                m.metadata["text"]
                for m in matches
            ]
        )

        prompt = f"""
You are answering a question about the document "{file_path}".
The context below contains excerpts taken directly from that document.
Answer the question using only this context.
If the context does not contain the answer, say you don't have that information.

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
            "file_path": file_path,
            "answer": result.content
        }

    @staticmethod
    def ask_workspace(
        question: str,
        workspace_id: int
    ):

        matches = retrieve_chunks(
            question,
            workspace_id
        )

        context = "\n\n".join(
            [
                m.metadata["text"]
                for m in matches
            ]
        )

        sources = list(
            {
                m.metadata.get("file_path")
                for m in matches
            }
        )

        prompt = f"""
You are answering a question using the user's indexed documents.
The context below contains excerpts taken from those documents.
Answer the question using only this context.
If the context does not contain the answer, say you don't have that information.

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
            "answer": result.content,
            "sources": sources
        }

    @staticmethod
    def search_workspace(
        query: str,
        workspace_id: int,
        top_k: int = 10
    ):

        matches = retrieve_chunks(
            query,
            workspace_id,
            top_k=top_k
        )

        best_per_file = {}

        for m in matches:

            file_path = m.metadata.get("file_path")

            snippet = (
                m.metadata.get("text", "")[:200]
            )

            existing = best_per_file.get(file_path)

            if not existing or m.score > existing["score"]:

                best_per_file[file_path] = {
                    "file_path": file_path,
                    "score": m.score,
                    "snippet": snippet
                }

        results = sorted(
            best_per_file.values(),
            key=lambda r: r["score"],
            reverse=True
        )

        return {
            "success": True,
            "query": query,
            "results": results
        }

    @staticmethod
    def delete_document(
        file_path: str,
        workspace_id: int
    ):

        index.delete(
            filter={
                "file_path": file_path
            },
            namespace=knowledge_namespace(workspace_id)
        )

        return {
            "success": True,
            "file_path": file_path,
            "message": "Document removed from knowledge index"
        }

    @staticmethod
    def reindex_document(
        file_path: str,
        workspace_id: int
    ):

        KnowledgeService.delete_document(
            file_path,
            workspace_id
        )

        return KnowledgeService.index_document(
            file_path,
            workspace_id
        )
