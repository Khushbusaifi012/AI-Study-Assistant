import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions

from app.config import CHROMA_DIR, USE_LOCAL_EMBEDDINGS

COLLECTION_API = "study_material"
COLLECTION_LOCAL = "study_material_local"


def use_local_embeddings() -> bool:
    return USE_LOCAL_EMBEDDINGS


def get_collection():
    client = chromadb.PersistentClient(
        path=str(CHROMA_DIR),
        settings=Settings(anonymized_telemetry=False),
    )
    if USE_LOCAL_EMBEDDINGS:
        return client.get_or_create_collection(
            name=COLLECTION_LOCAL,
            embedding_function=embedding_functions.DefaultEmbeddingFunction(),
            metadata={"hnsw:space": "cosine"},
        )
    return client.get_or_create_collection(
        name=COLLECTION_API,
        metadata={"hnsw:space": "cosine"},
    )
