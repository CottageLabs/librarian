from librarian import components


# KTODO


class VectorStoreService:
    """
    High level vector store wrapper function
    """

    def __init__(self, vector_store=None):
        self.vector_store = vector_store or components.get_vector_store()

    def count(self, metadata_filter: dict = None):
        from qdrant_client import models
        client = self.vector_store.client

        filters = []
        for k, v in metadata_filter.items():
            filters.append(models.FieldCondition(key=k, match=models.MatchValue(value=v)))
        f = models.Filter(must=filters) if filters else None
        collection_name = self.vector_store.collection_name
        size = client.count(collection_name, count_filter=f, exact=True).count
        return size

    def delete_collection(self):
        collection_name = self.vector_store.collection_name
        self.vector_store.client.delete_collection(collection_name)


def main():
    store_manager = VectorStoreService()
    print('Count:', store_manager.count({'metadata.source': 'intro.txt'}))

    points = store_manager.vector_store.client.scroll(
        collection_name=store_manager.vector_store.collection_name,
        limit=100,  # Adjust limit as needed
        with_payload=True,
        with_vectors=False  # Set to True if you want to see vectors too
    )
    print(points)


def main2():
    store_manager = VectorStoreService()
    store_manager.delete_collection()


if __name__ == '__main__':
    # main2()
    main()
