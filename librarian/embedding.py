from langchain_huggingface import HuggingFaceEmbeddings

from librarian.constants import DEFAULT_EMBEDDING


def get_embedding(device='cpu'):
    embedding = HuggingFaceEmbeddings(
        model_name=DEFAULT_EMBEDDING,
        model_kwargs={"device": device}
    )
    return embedding


def get_embedding_size(emb):
    text = "test akdjalskj lkajsdlk ajslkdj alksjl kajs"
    text = """
    Use the same size: Pick models that output the same dimension (e.g., both 384) so you can interchange them freely.

Create multi-vector collections: When first creating the collection, define multiple named vectors with different sizes. Example
    """
    text = """
    Yes — in Qdrant, **`vectors_config` is fixed after you create the collection**.

That means:

* If you change to an embedding model with a **different vector size**, you can’t just “update” the config.
* You must **create a new collection** (or delete & recreate the old one) with the correct `size`.

---

### Why?

Qdrant’s index structure is built specifically for the vector length you define.
Changing it would mean rebuilding the index from scratch — so Qdrant doesn’t allow resizing in place.

---

### If you want to swap models without recreating

You have two options:

1. **Use the same size**: Pick models that output the same dimension (e.g., both 384) so you can interchange them freely.
2. **Create multi-vector collections**: When first creating the collection, define **multiple named vectors** with different sizes. Example:

   ```python
   client.create_collection(
       collection_name="multi_embeddings",
       vectors_config={
           "minilm": VectorParams(size=384, distance=Distance.COSINE),
           "mpnet": VectorParams(size=768, distance=Distance.COSINE),
       }
   )
   ```

   Then you can store/query whichever vector you need later.

---

If you’re switching between **arbitrary models** in RAG, option 2 is safer — you define all possible vector sizes at the start, and don’t need to recreate collections when swapping.

I can give you a **dynamic collection creator** that reads sizes for all your models and builds `vectors_config` automatically so you can hot-swap models later.

    """
    vec = emb.embed_query(text)  # generate once
    return len(vec)


def main():
    size = get_embedding_size(get_embedding())
    print(f"Embedding size: {size}")


if __name__ == '__main__':
    main()
