from sqlalchemy import create_engine, select, exists
from sqlalchemy.orm import Session

from librarian.dao.schema.dao_schema import Base


class BaseDao:

    def __init__(self, url=None):
        if url is None:
            from librarian import cpaths
            url = f"sqlite:///{cpaths.DB_SQLITE_PATH}"

        self.engine = create_engine(url, echo=False, future=True)
        Base.metadata.create_all(self.engine)

    def create_session(self):
        return Session(self.engine)

    def add(self, obj):
        with Session(self.engine) as s:
            s.add(obj)
            s.commit()
            s.refresh(obj)
            return obj

    def exists(self, *clause):
        with self.create_session() as s:
            stmt = select(exists().where(*clause))
            is_exist = s.execute(stmt).scalar()
            return is_exist
