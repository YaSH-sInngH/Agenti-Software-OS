import cohere
from src.config.settings import settings

co = cohere.ClientV2(
    api_key=settings.COHERE_API_KEY
)

def generate_embedding(
    text: str,
    input_type: str = "search_document"
):

    print("Embedding text:", text)

    response = co.embed(
        model="embed-english-v3.0",
        texts=[text],
        input_type=input_type
    )

    vector = response.embeddings.float_[0]

    print("Vector dimension:", len(vector))

    return vector