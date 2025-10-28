"""
Tools that convert different source of text (pdf, epub, markdown, raw text) to Document objects
"""
import logging
import warnings
from pathlib import Path
from typing import Iterable

from langchain_community.document_loaders import PyPDFLoader, UnstructuredEPubLoader, UnstructuredMarkdownLoader
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter, MarkdownHeaderTextSplitter
from langchain_unstructured import UnstructuredLoader

from librarian import components
from librarian.utils import iter_utils

log = logging.getLogger(__name__)


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
    """

    Args:
        sources: source can be any different type, each different type of source
            yield different metadata by different loader

    """
    if text_splitter is None:
        text_splitter = create_default_text_splitter()

    _obj = iter_utils.peek(sources)
    if isinstance(_obj, tuple):
        for fname, text in sources:
            for chunk in text_splitter.split_text(text):
                yield Document(page_content=chunk, metadata={"source": fname})
    else:
        raise NotImplementedError(f"other type [{_obj}] of source is not implemented yet")


def cleanup_bad_encoding(docs: Iterable[Document]) -> Iterable[Document]:
    for d in docs:
        try:
            d.page_content.encode('utf-8')
        except UnicodeEncodeError:
            log.warning(f"Document [{d.metadata.get('source')}][{d.metadata.get('page')}] has bad encoding")
            d.page_content = d.page_content.encode('utf-8', errors='ignore').decode('utf-8', errors='ignore')
        yield d


def finalize_and_save_docs(docs: list[Document], vectorstore=None, metadata=None) -> list[Document]:
    """Finalize documents and save to vector store."""
    print(f"Split into {len(docs)} chunks")

    # Inject additional metadata if provided
    if metadata:
        docs = list(inject_metadata(docs, metadata))

    # Get vector store and add documents
    vectorstore = vectorstore or components.get_vector_store()
    vectorstore.add_documents(docs)

    return docs


def save_pdf_to_vectorstore(pdf_path, vectorstore=None, text_splitter=None, metadata=None):
    loader = PyPDFLoader(str(pdf_path))
    pages = loader.load()
    pages = list(cleanup_bad_encoding(pages))

    print(f"Loaded {len(pages)} pages from PDF")

    if text_splitter is None:
        text_splitter = create_default_text_splitter()

    docs = text_splitter.split_documents(pages)
    docs = list(docs)

    return finalize_and_save_docs(docs, vectorstore, metadata)


def save_text_to_vectorstore(file_path, vectorstore=None, text_splitter=None, metadata=None):
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


def save_epub_to_vectorstore(epub_path, vectorstore=None, text_splitter=None, metadata=None):
    print(f'debugggggg {epub_path}')
    loader = UnstructuredEPubLoader(Path(epub_path))
    try:
        pages = loader.load()
    except TypeError as e:
        # pypandoc issue, it wil raise some unexpected error
        if "'PosixPath' object is not iterable" in str(e):
            raise RuntimeError("Failed to load EPUB. This may be due to a pypandoc issue. "
                               "Please ensure pypandoc is properly installed and configured.") from e


    pages = list(cleanup_bad_encoding(pages))

    print(f"Loaded {len(pages)} pages from EPUB")

    if text_splitter is None:
        text_splitter = create_default_text_splitter()

    docs = text_splitter.split_documents(pages)
    docs = list(docs)

    return finalize_and_save_docs(docs, vectorstore, metadata)


def save_markdown_to_vectorstore(md_path, vectorstore=None, text_splitter=None, metadata=None):
    loader = UnstructuredMarkdownLoader(str(md_path))
    pages = loader.load()
    pages = list(cleanup_bad_encoding(pages))

    print(f"Loaded markdown from {md_path}")

    # Use MarkdownHeaderTextSplitter to preserve structure
    headers_to_split_on = [
        ("#", "Header 1"),
        ("##", "Header 2"),
        ("###", "Header 3"),
    ]
    markdown_splitter = MarkdownHeaderTextSplitter(headers_to_split_on=headers_to_split_on)

    # Split by headers first
    md_header_splits = []
    for page in pages:
        md_header_splits.extend(markdown_splitter.split_text(page.page_content))

    # Then apply character-level splitting if needed
    if text_splitter is None:
        text_splitter = create_default_text_splitter()

    docs = text_splitter.split_documents(md_header_splits)
    docs = list(docs)

    return finalize_and_save_docs(docs, vectorstore, metadata)


def save_any_to_vectorstore(file_path, vectorstore=None, text_splitter=None, metadata=None):
    file_path = Path(file_path)
    if not file_path.is_file():
        raise FileNotFoundError(f"File not found: {file_path}")

    suffix = file_path.suffix.lower()
    if suffix == '.pdf':
        return save_pdf_to_vectorstore(file_path, vectorstore, text_splitter, metadata)
    elif suffix == '.epub':
        return save_epub_to_vectorstore(file_path, vectorstore, text_splitter, metadata)
    elif suffix == '.md':
        return save_markdown_to_vectorstore(file_path, vectorstore, text_splitter, metadata)
    else:
        if suffix != '.txt':
            warnings.warn(f"File suffix [{suffix}] is not explicitly supported, treat it as raw text file")
        return save_text_to_vectorstore(file_path, vectorstore=vectorstore,
                                        text_splitter=text_splitter, metadata=metadata)


def inject_metadata(docs: Iterable[Document], metadata: dict = None) -> Iterable[Document]:
    if metadata is None:
        metadata = {}

    for doc in docs:
        if metadata:
            new_metadata = doc.metadata.copy() if doc.metadata else {}
            new_metadata.update(metadata)
            doc.metadata = new_metadata
        yield doc
