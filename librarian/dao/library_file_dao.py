from librarian.dao.base_dao import BaseDao
from librarian.dao.schema.dao_schema import LibraryFile


class LibraryFileDao(BaseDao):

    @classmethod
    def from_collection(cls, collection_name: str):
        from librarian import cpaths
        url = f"sqlite:///{cpaths.DB_SQLITE_PATH}-{collection_name}"
        return cls(url=url)

    @property
    def model_class(self):
        return LibraryFile

    def exist(self, hash_id: str) -> bool:
        return self.exists(self.model_class.hash_id == hash_id)

    def find(
            self,
            hash_prefix: str = None,
            filename: str = None,
    ) -> list[LibraryFile]:
        """Find library files with optional filtering by hash prefix or filename."""
        with self.create_session() as session:
            query = session.query(self.model_class)

            if hash_prefix is not None:
                query = query.filter(self.model_class.hash_id.startswith(hash_prefix))

            if filename is not None:
                query = query.filter(self.model_class.file_name.like(f"%{filename}%"))

            return query.all()
