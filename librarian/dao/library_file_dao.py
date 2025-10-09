from librarian.dao.base_dao import BaseDao
from librarian.dao.schema.dao_schema import LibraryFile


class LibraryFileDao(BaseDao):
    def exist(self, hash_id: str) -> bool:
        clause = LibraryFile.hash_id == hash_id
        return self.exists(clause)

    def find(self, hash_prefix: str = None, filename: str = None) -> list[LibraryFile]:
        """Find library files with optional filtering by hash prefix or filename."""
        with self.create_session() as session:
            query = session.query(LibraryFile)

            if hash_prefix is not None:
                query = query.filter(LibraryFile.hash_id.startswith(hash_prefix))

            if filename is not None:
                query = query.filter(LibraryFile.file_name.like(f"%{filename}%"))

            return query.all()
