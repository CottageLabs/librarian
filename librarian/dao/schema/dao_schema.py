from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import String, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session
from sqlalchemy.types import DateTime

from librarian import cpaths


class Base(DeclarativeBase):
    pass


class LibraryFile(Base):
    __tablename__ = "library_file"

    hash_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    file_name: Mapped[str] = mapped_column(String(255), index=True)
    collection_name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(tz=timezone.utc),
        nullable=False,
        index=True
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(tz=timezone.utc),
        nullable=False,
        index=True
    )


def main():
    if cpaths.DB_SQLITE_TMP_PATH.exists():
        cpaths.DB_SQLITE_TMP_PATH.unlink()

    engine = create_engine(f"sqlite:///{cpaths.DB_SQLITE_TMP_PATH}", echo=False, future=True)
    Base.metadata.create_all(engine)

    with Session(engine) as s:
        lib_file = LibraryFile(hash_id="test123", file_name="example.txt", collection_name="demo_collection")
        s.add(lib_file)
        s.commit()
        # s.refresh(lib_file)

        print(f"Created LibraryFile: {lib_file.hash_id}, {lib_file.file_name},"
              f" {lib_file.collection_name}, {lib_file.created_at}")

        # Query the file
        queried_file = s.get(LibraryFile, "test123")
        print(f"Queried LibraryFile: {queried_file.hash_id}, {queried_file.file_name},"
              f" {queried_file.collection_name}, {queried_file.created_at}")


def main2():
    from librarian.dao.base_dao import BaseDao

    if cpaths.DB_SQLITE_TMP_PATH.exists():
        cpaths.DB_SQLITE_TMP_PATH.unlink()

    dao = BaseDao(f"sqlite:///{cpaths.DB_SQLITE_TMP_PATH}")

    lib_file = LibraryFile(hash_id="test456", file_name="example2.txt", collection_name="demo_collection")
    created_file = dao.add(lib_file)

    print(f"Created LibraryFile: {created_file.hash_id}, {created_file.file_name},"
          f" {created_file.collection_name}, {created_file.created_at}")

    # Query the file using DAO's create_session method
    with dao.create_session() as s:
        queried_file = s.get(LibraryFile, "test456")
        print(f"Queried LibraryFile: {queried_file.hash_id}, {queried_file.file_name},"
              f" {queried_file.collection_name}, {queried_file.created_at}")


if __name__ == '__main__':
    main()
