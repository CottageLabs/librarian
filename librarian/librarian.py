import hashlib
import shutil
import subprocess
from pathlib import Path

import tqdm
from unstructured.errors import UnprocessableEntityError

from librarian import components, librarian_config
from librarian import document_ingestion
from librarian.constants import MAX_FILE_SIZE_BYTES
from librarian.cpaths import GITREPO_DIR
from librarian.dao.base_dao import BaseDao
from librarian.dao.library_file_dao import LibraryFileDao
from librarian.dao.schema.dao_schema import LibraryFile
from librarian.librarian_config import get_collection_name
from librarian.vector_store_service import VectorStoreService


def calculate_file_hash(file_path: Path) -> str:
    """Calculate SHA256 hash of a file."""
    with open(file_path, 'rb') as f:
        return hashlib.sha256(f.read()).hexdigest()


def clone_git_repo(git_url: str) -> Path:
    """Clone a git repository to PROJ_HOME/gitrepo directory.

    Args:
        git_url: Git repository URL (must end with .git)

    Returns:
        Path to the cloned repository

    Raises:
        RuntimeError: If git command is not found or cloning fails
    """
    if not shutil.which('git'):
        raise RuntimeError("git command not found in system")

    GITREPO_DIR.mkdir(parents=True, exist_ok=True)

    repo_name = git_url.rstrip('/').split('/')[-1].replace('.git', '')
    target_path = GITREPO_DIR / repo_name

    if target_path.exists():
        print(f"Repository already exists at: {target_path}")
        return target_path

    print(f"Cloning {git_url} to {target_path}")
    result = subprocess.run(
        ['git', 'clone', git_url, str(target_path)],
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        raise RuntimeError(f"Failed to clone repository: {result.stderr}")

    print(f"Successfully cloned to: {target_path}")
    return target_path


class Librarian:
    """
    Manage files in the library
    - manage both in DB and in Vector Store
    - avoid duplicate files by hash
    """

    def __init__(self, vector_store=None):
        self.vector_store = vector_store or components.get_vector_store(
            collection_name=librarian_config.get_collection_name()
        )

    @property
    def collection_name(self) -> str:
        """Get collection name from vector store or default config."""
        return self.vector_store.collection_name

    def switch_collection(self, collection_name: str) -> None:
        """Switch to a different collection in the vector store."""
        librarian_config.save_collection_name(collection_name)
        self.vector_store.client.close()
        self.vector_store = components.get_vector_store(
            collection_name=librarian_config.get_collection_name()
        )

    def add_file(self, file_path: str | Path, additional_metadata: dict = None) -> None:
        """Add a single file to the library.

        Args:
            file_path: Path to the file to add
            additional_metadata: Optional dict of additional metadata to store with the file
        """
        file_path = Path(file_path)
        print(f'Working on file: {file_path}')

        # Check if file exists
        if not file_path.is_file():
            raise FileNotFoundError(f"File not found: {file_path}")

        # Check file size
        file_size = file_path.stat().st_size
        if file_size > MAX_FILE_SIZE_BYTES:
            raise ValueError(
                f"File size ({file_size} bytes) exceeds maximum allowed size ({MAX_FILE_SIZE_BYTES} bytes)")

        file_hash = calculate_file_hash(file_path)
        print(f"File hash: {file_hash}")

        # Check hash existence in DB
        file_dao = LibraryFileDao.from_collection(self.collection_name)
        if file_dao.exist(file_hash):
            raise ValueError(f"File with hash {file_hash} already exists in library")

        # Merge metadata
        metadata = {"hash_id": file_hash}
        if additional_metadata:
            metadata.update(additional_metadata)

        # Add to Vector Store
        document_ingestion.save_any(
            file_path,
            vectorstore=self.vector_store,
            metadata=metadata,
        )

        # Add to DB
        library_file = LibraryFile(
            hash_id=file_hash,
            file_name=file_path.name,
        )
        file_dao.add(library_file)

    def add_by_path(self, path: str | Path):
        """Add file(s) from a path (can be a file or directory).

        For directories, recursively finds all files and adds them.
        If path ends with .git and doesn't exist locally, clones the git repository.

        Yields:
            tuple: (status, file_path, error_msg) where:
                - status: 'added', 'skipped', or 'error'
                - file_path: Path object
                - error_msg: error message string if status is not 'added', None otherwise
        """
        path_str = str(path)
        path_obj = Path(path)
        cloned_from_git = False

        metadata = {}

        # Check if it's a git URL that needs to be cloned
        if path_str.endswith('.git') and not path_obj.exists():
            try:
                path_obj = clone_git_repo(path_str)
                cloned_from_git = True
                metadata['source_root'] = path_str
            except RuntimeError as e:
                yield 'error', Path(path_str), str(e)
                return
        elif not path_obj.exists():
            raise FileNotFoundError(f"Path not found: {path_obj}")


        try:
            if path_obj.is_file():
                file_paths = [path_obj]
            else:
                file_formats = document_ingestion.get_supported_suffixes()
                file_paths = [f for f in path_obj.rglob('*') if f.is_file()]
                file_paths = [f for f in file_paths if f.suffix.lower() in file_formats]
                metadata['source_root'] = str(path_obj.resolve())

            if len(file_paths) > 1:
                file_paths = tqdm.tqdm(file_paths, desc="Adding files", unit="file", leave=True)

            for file_path in file_paths:
                try:
                    self.add_file(file_path, additional_metadata=metadata)
                    yield 'added', file_path, None
                except ValueError as e:
                    yield 'skipped', file_path, str(e)
                except  Exception as e:
                    yield 'error', file_path, str(e)
        finally:
            if cloned_from_git:
                shutil.rmtree(path_obj)

    def find_all_files(self) -> list[LibraryFile]:
        return LibraryFileDao.from_collection(self.collection_name).find_all()

    def count_files(self) -> int:
        """Count total number of documents in the library."""
        return LibraryFileDao.from_collection(self.collection_name).count()

    def find_latest_files(self, limit: int = 10) -> list[LibraryFile]:
        """Find the latest n documents ordered by creation date."""
        with LibraryFileDao.from_collection(self.collection_name).create_session() as session:
            return list(session.query(LibraryFile)
                        .order_by(LibraryFile.created_at.desc())
                        .limit(limit)
                        .all())

    def drop_collection(self):
        """Drop the entire vector store collection and clear database records."""
        vector_service = VectorStoreService(self.vector_store)
        vector_service.delete_collection()

        # Clear all library file records from database
        LibraryFileDao.from_collection(self.collection_name).delete()

    def remove(self, hash_prefix: str = None, filename: str = None) -> bool:
        """Remove a library file by hash prefix or filename from both vector store and database."""
        from qdrant_client import models

        # Check if file exists in database
        file_dao = LibraryFileDao.from_collection(self.collection_name)

        files = file_dao.find(
            hash_prefix=hash_prefix,
            filename=filename,
        )

        if len(files) == 0:
            return False

        if len(files) > 1:
            raise ValueError(f"Found {len(files)} matching files. Please provide more specific criteria.")

        file_to_remove = files[0]
        hash_id = file_to_remove.hash_id

        # Delete from vector store using metadata filter
        client = self.vector_store.client

        # Create filter for hash_id
        filter_condition = models.Filter(
            must=[
                models.FieldCondition(
                    key="metadata.hash_id",
                    match=models.MatchValue(value=hash_id)
                )
            ]
        )

        # Delete from vector store
        client.delete(
            collection_name=self.collection_name,
            points_selector=models.FilterSelector(filter=filter_condition)
        )

        # Delete from database
        LibraryFileDao.from_collection(self.collection_name).delete(LibraryFile.hash_id == hash_id)

        return True

    def search(self, query: str, limit: int = 5) -> list[dict]:
        """Search documents by similarity to query text.

        Args:
            query: Search query text
            limit: Maximum number of results to return

        Returns:
            List of dicts with keys:
                - content: Document text content
                - metadata: Document metadata dict
                - score: Similarity score (float)
        """
        results = self.vector_store.similarity_search_with_score(query, k=limit)

        return [
            {
                'content': doc.page_content,
                'metadata': doc.metadata,
                'score': score
            }
            for doc, score in results
        ]


def main__add_test_file():
    librarian = Librarian()
    librarian.add_file(Path.home() / 'tmp/test-file/deep-learning.pdf')
    librarian.add_file(Path.home() / 'tmp/test-file/rl1.pdf')
    librarian.add_file(Path.home() / 'tmp/test-file/rl2.pdf')
    files = librarian.find_all_files()
    for f in files:
        print(f"{f.hash_id}, {f.file_name}, {f.created_at}")


if __name__ == '__main__':
    main__add_test_file()
