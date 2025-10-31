"""Utilities for splitting text into LangChain Document chunks."""
from typing import Iterable

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from librarian.utils import iter_utils


def create_text_splitter():
    # return RecursiveCharacterTextSplitter(
    #     chunk_size=500, chunk_overlap=80, separators=["\n\n", "\n", " ", ""]
    # )

    return RecursiveCharacterTextSplitter.from_tiktoken_encoder(
        chunk_size=300, chunk_overlap=50, separators=["\n\n", "\n", " ", ""]
    )


def create_default_text_splitter():
    return create_text_splitter()


def create_docs(sources: Iterable, text_splitter=None) -> Iterable[Document]:
    """Convert an iterable of (source, text) tuples into Documents."""
    if text_splitter is None:
        text_splitter = create_default_text_splitter()

    _obj = iter_utils.peek(sources)
    if isinstance(_obj, tuple):
        for fname, text in sources:
            for chunk in text_splitter.split_text(text):
                yield Document(page_content=chunk, metadata={"source": fname})
    else:
        raise NotImplementedError(f"other type [{_obj}] of source is not implemented yet")
