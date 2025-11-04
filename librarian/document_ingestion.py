"""
Utilities for loading documents from various sources and saving them to the vector store.
"""
import logging
import warnings
from pathlib import Path
from typing import Iterable

from langchain_community.document_loaders import (
    PyPDFLoader,
    UnstructuredEPubLoader,
    UnstructuredMarkdownLoader,
)
from langchain_core.documents import Document
from langchain_text_splitters import MarkdownHeaderTextSplitter
from langchain_unstructured import UnstructuredLoader

from librarian import components
from librarian.text_processing import create_default_text_splitter

log = logging.getLogger(__name__)


def cleanup_bad_encoding(docs: Iterable[Document]) -> Iterable[Document]:
    for d in docs:
        try:
            d.page_content.encode("utf-8")
        except UnicodeEncodeError:
            log.warning(
                f"Document [{d.metadata.get('source')}][{d.metadata.get('page')}] has bad encoding",
            )
            d.page_content = d.page_content.encode("utf-8", errors="ignore").decode(
                "utf-8",
                errors="ignore",
            )
        yield d


def finalize_and_save_docs(
        docs: list[Document],
        vectorstore=None,
        metadata=None,
) -> list[Document]:
    """Finalize documents and save to vector store."""
    print(f"Split into {len(docs)} chunks")

    if metadata:
        docs = list(inject_metadata(docs, metadata))

    vectorstore = vectorstore or components.get_vector_store()
    vectorstore.add_documents(docs)

    return docs


def save_pdf(pdf_path, vectorstore=None, text_splitter=None, metadata=None):
    loader = PyPDFLoader(str(pdf_path))
    pages = loader.load()
    pages = list(cleanup_bad_encoding(pages))

    print(f"Loaded {len(pages)} pages from PDF")

    if text_splitter is None:
        text_splitter = create_default_text_splitter()

    docs = text_splitter.split_documents(pages)
    docs = list(docs)

    return finalize_and_save_docs(docs, vectorstore, metadata)


def save_text(file_path, vectorstore=None, text_splitter=None, metadata=None):
    file_path = Path(file_path)
    if not file_path.is_file():
        raise FileNotFoundError(f"File not found: {file_path}")

    loader = UnstructuredLoader(str(file_path))
    pages = loader.load()
    pages = list(cleanup_bad_encoding(pages))

    print(f"Loaded text from {file_path}")

    if text_splitter is None:
        text_splitter = create_default_text_splitter()

    docs = text_splitter.split_documents(pages)
    docs = list(docs)

    return finalize_and_save_docs(docs, vectorstore, metadata)


def save_epub(epub_path, vectorstore=None, text_splitter=None, metadata=None):
    loader = UnstructuredEPubLoader(Path(epub_path))
    try:
        pages = loader.load()
    except TypeError as e:
        if "'PosixPath' object is not iterable" in str(e):
            raise RuntimeError(
                "Failed to load EPUB. This may be due to a pypandoc issue. "
                "Please ensure pypandoc is properly installed and configured.",
            ) from e

    pages = list(cleanup_bad_encoding(pages))

    print(f"Loaded {len(pages)} pages from EPUB")

    if text_splitter is None:
        text_splitter = create_default_text_splitter()

    docs = text_splitter.split_documents(pages)
    docs = list(docs)

    return finalize_and_save_docs(docs, vectorstore, metadata)


def save_markdown(md_path, vectorstore=None, text_splitter=None, metadata=None):
    loader = UnstructuredMarkdownLoader(str(md_path))
    pages = loader.load()
    pages = list(cleanup_bad_encoding(pages))

    print(f"Loaded markdown from {md_path}")

    headers_to_split_on = [
        ("#", "Header 1"),
        ("##", "Header 2"),
        ("###", "Header 3"),
    ]
    markdown_splitter = MarkdownHeaderTextSplitter(headers_to_split_on=headers_to_split_on)

    md_header_splits = []
    for page in pages:
        md_header_splits.extend(markdown_splitter.split_text(page.page_content))

    if text_splitter is None:
        text_splitter = create_default_text_splitter()

    docs = text_splitter.split_documents(md_header_splits)
    docs = list(docs)

    return finalize_and_save_docs(docs, vectorstore, metadata)


def save_any(path, vectorstore=None, text_splitter=None, metadata=None):
    path = Path(path)
    suffix_map = get_suffix_saver_map()

    if not path.is_file():
        raise FileNotFoundError(f"File not found: {path}")

    suffix = path.suffix.lower()
    saver_fn = suffix_map.get(suffix)

    if saver_fn is None:
        if suffix != ".txt":
            warnings.warn(
                f"File suffix [{suffix}] is not explicitly supported, treat it as raw text file",
            )
        saver_fn = save_text

    return saver_fn(
        path,
        vectorstore=vectorstore,
        text_splitter=text_splitter,
        metadata=metadata,
    )


def inject_metadata(docs: Iterable[Document], metadata: dict = None) -> Iterable[Document]:
    if metadata is None:
        metadata = {}

    for doc in docs:
        if metadata:
            new_metadata = doc.metadata.copy() if doc.metadata else {}
            new_metadata.update(metadata)
            doc.metadata = new_metadata
        yield doc


def get_suffix_saver_map():
    """Return mapping of file suffix to the corresponding save function."""
    return {
        ".pdf": save_pdf,
        ".epub": save_epub,
        ".md": save_markdown,
        ".txt": save_text,
    }


def get_supported_suffixes():
    """Return a list of supported file suffixes."""
    return list(get_suffix_saver_map().keys())
