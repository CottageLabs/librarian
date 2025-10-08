from librarian.dao.base_dao import BaseDao
from librarian.dao.schema.dao_schema import LibraryFile


class LibraryFileDao(BaseDao):
    def exist(self, hash_id: str) -> bool:
        clause = LibraryFile.hash_id == hash_id
        return self.exists(clause)
