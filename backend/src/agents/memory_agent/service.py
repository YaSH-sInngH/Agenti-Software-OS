from src.vectorstore.memory_store import store_memory, retrieve_memory

class MemoryService:

    @staticmethod
    def store(
        user_id: int,
        memory: str,
        memory_type: str
    ):
        return store_memory(
            user_id,
            memory,
            memory_type
        )

    @staticmethod
    def retrieve(
        user_id: int,
        query: str
    ):
        return retrieve_memory(
            user_id,
            query
        )