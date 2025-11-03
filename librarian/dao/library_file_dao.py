from librarian.dao.base_dao import BaseDao
from librarian.dao.schema.dao_schema import LibraryFile


class LibraryFileDao(BaseDao):

    @property
    def model_class(self):
        return LibraryFile

    def exist(self, hash_id: str, collection_name: str | None = None) -> bool:
        clauses = [self.model_class.hash_id == hash_id]
        if collection_name is not None:
            clauses.append(self.model_class.collection_name == collection_name)
        return self.exists(*clauses)

    def find(
            self,
            hash_prefix: str = None,
            filename: str = None,
            collection_name: str | None = None,
    ) -> list[LibraryFile]:
        """Find library files with optional filtering by collection, hash prefix, or filename."""
        with self.create_session() as session:
            query = session.query(self.model_class)

            if collection_name is not None:
                query = query.filter(self.model_class.collection_name == collection_name)

            if hash_prefix is not None:
                query = query.filter(self.model_class.hash_id.startswith(hash_prefix))

            if filename is not None:
                query = query.filter(self.model_class.file_name.like(f"%{filename}%"))

            return query.all()
