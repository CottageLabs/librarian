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
    vec = emb.embed_query(text)  # generate once
    return len(vec)


def main():
    size = get_embedding_size(get_embedding())
    print(f"Embedding size: {size}")


if __name__ == '__main__':
    main()
