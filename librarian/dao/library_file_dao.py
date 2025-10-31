from librarian.dao.base_dao import BaseDao
from librarian.dao.schema.dao_schema import LibraryFile


class LibraryFileDao(BaseDao):
    def exist(self, hash_id: str, collection_name: str | None = None) -> bool:
        clauses = [LibraryFile.hash_id == hash_id]
        if collection_name is not None:
            clauses.append(LibraryFile.collection_name == collection_name)
        return self.exists(*clauses)

    def find(
        self,
        hash_prefix: str = None,
        filename: str = None,
        collection_name: str | None = None,
    ) -> list[LibraryFile]:
        """Find library files with optional filtering by collection, hash prefix, or filename."""
        with self.create_session() as session:
            query = session.query(LibraryFile)

            if collection_name is not None:
                query = query.filter(LibraryFile.collection_name == collection_name)

            if hash_prefix is not None:
                query = query.filter(LibraryFile.hash_id.startswith(hash_prefix))

            if filename is not None:
                query = query.filter(LibraryFile.file_name.like(f"%{filename}%"))

            return query.all()
