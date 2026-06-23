from typing import List

from pinecone import Pinecone
from pinecone import ServerlessSpec

from tqdm.auto import tqdm


class CustomVectorDb:

    def __init__(
        self,
        api_key: str,
        index_name: str,
        dimension: int
    ):

        self.pc = Pinecone(
            api_key=api_key
        )

        self.index_name = index_name

        existing_indexes = (
            self.pc
            .list_indexes()
            .names()
        )

        if index_name not in existing_indexes:

            self.pc.create_index(
                name=index_name,
                dimension=dimension,
                metric="cosine",
                spec=ServerlessSpec(
                    cloud="aws",
                    region="us-east-1"
                )
            )

        self.index = self.pc.Index(
            index_name
        )

    def upsert(
        self,
        vector_id: str,
        vector: List[float],
        metadata: dict = None
    ):

        self.index.upsert(
            vectors=[
                {
                    "id": vector_id,
                    "values": vector,
                    "metadata": metadata or {}
                }
            ]
        )

    def batch_upsert(
        self,
        dataloader,
        model
    ):

        import math

        for (
            img_feats,
            text_feats,
            item_dicts
        ) in tqdm(dataloader):

            embeddings = model.predict_emb(
                img_feats,
                text_feats
            )

            # Reconstruct list of dicts for metadata
            batch_items = []
            keys = list(item_dicts.keys())
            batch_len = len(item_dicts[keys[0]])

            for i in range(batch_len):
                item_dict = {}
                for k in keys:
                    val = item_dicts[k][i]
                    if hasattr(val, "item"):
                        val = val.item()
                    if val is None or (isinstance(val, float) and math.isnan(val)):
                        continue
                    item_dict[k] = val
                
                # Keep row_id for backward compatibility with final_chat_node
                if "id" in item_dict:
                    item_dict["row_id"] = item_dict["id"]
                    
                batch_items.append(item_dict)

            vectors = []

            for (
                emb,
                item_metadata
            ) in zip(
                embeddings,
                batch_items
            ):
                vector_id = str(item_metadata.get("id"))

                vectors.append(
                    {
                        "id": vector_id,
                        "values": emb.tolist(),
                        "metadata": item_metadata
                    }
                )

            self.index.upsert(
                vectors=vectors
            )

    def search(
        self,
        vector: List[float],
        top_k: int = 5
    ):
        if hasattr(vector, "tolist"):
            vector = vector.tolist()
        if isinstance(vector, list) and len(vector) > 0 and isinstance(vector[0], list):
            vector = vector[0]

        return self.index.query(
            vector=vector,
            top_k=top_k,
            include_metadata=True
        )

    def delete_index(self):

        self.pc.delete_index(
            self.index_name
        )

    def delete_all(self):

        self.index.delete(delete_all=True)

    
    def get_all_ids(self):

        ids = []

        for batch in self.index.list():
            ids.extend([item.id for item in batch])

        return ids    