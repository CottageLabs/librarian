from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams

from librarian.constants import DEFAULT_COLLECTION_NAME
from librarian.envvars import get_qdrant_data_path
from librarian.embedding import get_embedding
import logging

log = logging.getLogger(__name__)


def get_client(location=None, path=None, **kwargs):
    final_kwargs = {}
    if path is not None:
        final_kwargs['path'] = path
    elif location is not None:
        final_kwargs['location'] = location
    else:
        qdrant_data_path = get_qdrant_data_path()
        log.info(f"Using default Qdrant data path at {qdrant_data_path}")
        final_kwargs['path'] = qdrant_data_path

    final_kwargs |= kwargs
    qdrant = QdrantClient(**final_kwargs)
    return qdrant


def get_vector_store(client=None, collection_name=DEFAULT_COLLECTION_NAME, device='cpu'):
    # KTODO use device on all caller
    if client is None:
        client = get_client()

    embedding = get_embedding(device=device)
    init_collection(embedding._client.get_sentence_embedding_dimension(),
                    client=client, collection_name=collection_name)
    vector_store = QdrantVectorStore(
        client=client,
        collection_name=collection_name,
        embedding=embedding,
    )

    return vector_store


def init_collection(
        embedding_size,
        client=None,
        collection_name=DEFAULT_COLLECTION_NAME,
):
    if client is None:
        client = get_client()

    # Create the collection if it doesn't exist
    if not client.collection_exists(collection_name):
        client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(size=embedding_size, distance=Distance.COSINE),
        )


def init_test_data():
    from librarian import text_processing

    docs_raw = [
        ("intro.txt",
         "LangChain lets you build RAG systems by chaining chunks, retrieval, and LLM prompts."),
        ("qdrant.txt",
         "Qdrant is a vector database for similarity search. It supports HNSW indexes and filtering."),
        ("chunks.txt",
         "Chunking with RecursiveCharacterTextSplitter helps keep semantic units together. "
         "Common sizes: 300-800 chars with 10-100 char overlap."),
        ("eval.txt",
         "Evaluate RAG with precision@k, hit rate, faithfulness, and answer relevancy.")
    ]

    docs = text_processing.create_docs(docs_raw)
    docs = list(docs)

    vectorstore = get_vector_store()
    vectorstore.add_documents(docs)

    return vectorstore
