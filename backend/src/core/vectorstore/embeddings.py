import cohere
from src.core.config.settings import settings

co = cohere.ClientV2(
    api_key=settings.COHERE_API_KEY
)

EMBED_MODEL = "embed-english-v3.0"
MAX_BATCH = 96  # Cohere's per-call text limit


def generate_embedding(
    text: str,
    input_type: str = "search_document"
):
    response = co.embed(
        model=EMBED_MODEL,
        texts=[text],
        input_type=input_type
    )
    return response.embeddings.float_[0]


def generate_embeddings(
    texts: list,
    input_type: str = "search_document"
):
    # Batch many texts per call (max 96) instead of one call per chunk.
    # Drastically cuts API calls and avoids trial-key rate limits.
    vectors = []
    for start in range(0, len(texts), MAX_BATCH):
        batch = texts[start:start + MAX_BATCH]
        response = co.embed(
            model=EMBED_MODEL,
            texts=batch,
            input_type=input_type,
        )
        vectors.extend(response.embeddings.float_)
    return vectors
