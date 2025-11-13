from mcp.server.fastmcp import FastMCP
from librarian.librarian import Librarian
from librarian.envvars import get_qdrant_data_path

mcp = FastMCP("librarian")


@mcp.tool()
def get_status() -> dict:
    """Get library status including Qdrant path, collection name, and all collections info.

    Returns:
        Dict with keys:
            - qdrant_path: Path to Qdrant data directory
            - current_collection: Name of the current collection
            - collections: Dict mapping collection name to points count
    """
    lib = Librarian()
    qdrant_path = get_qdrant_data_path()
    collections_info = lib.get_collections_info()

    return {
        "qdrant_path": str(qdrant_path),
        "current_collection": lib.collection_name,
        "collections": collections_info
    }


@mcp.tool()
def list_documents(limit: int = 10) -> list[dict]:
    """List latest documents added to the library.

    Args:
        limit: Number of latest documents to show (default: 10)

    Returns:
        List of dicts with keys:
            - hash_id: Document hash ID
            - file_name: File name
            - created_at: Creation timestamp
    """
    lib = Librarian()
    files = lib.find_latest_files(limit)

    return [
        {
            "hash_id": file.hash_id,
            "file_name": file.file_name,
            "created_at": file.created_at.isoformat()
        }
        for file in files
    ]


@mcp.tool()
def search_documents(query: str, limit: int = 5) -> list[dict]:
    """Search documents by similarity to query text.

    Args:
        query: Search query text
        limit: Maximum number of results to return (default: 5)

    Returns:
        List of dicts with keys:
            - content: Document text content
            - metadata: Document metadata dict
            - score: Similarity score (float)
    """
    lib = Librarian()
    return lib.search(query, limit=limit)


@mcp.tool()
def count_documents() -> dict:
    """Count total number of documents in the library.

    Returns:
        Dict with keys:
            - collection_name: Name of the current collection
            - total_count: Total number of documents
    """
    lib = Librarian()
    total_count = lib.count_files()

    return {
        "collection_name": lib.collection_name,
        "total_count": total_count
    }


@mcp.tool()
def switch_collection(collection_name: str) -> dict:
    """Switch to a different collection.

    Args:
        collection_name: Name of the collection to switch to

    Returns:
        Dict with keys:
            - previous_collection: Previous collection name
            - current_collection: New collection name
    """
    lib = Librarian()
    previous = lib.collection_name

    if previous == collection_name:
        return {
            "previous_collection": previous,
            "current_collection": collection_name,
            "message": f"Already using collection '{collection_name}'"
        }

    lib.switch_collection(collection_name)

    return {
        "previous_collection": previous,
        "current_collection": collection_name,
        "message": f"Switched from '{previous}' to '{collection_name}'"
    }


def main():
    mcp.run(transport='stdio')


if __name__ == "__main__":
    main()
