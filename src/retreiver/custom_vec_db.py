from typing import List, Dict, Any

from pinecone import Pinecone
from pinecone import ServerlessSpec

from tqdm.auto import tqdm
from warnings import deprecated

def _reciprocal_rank_fusion(
    img_results: List[Any],
    txt_results: List[Any],
    rrf_k: float = 60,
    top_k: int = 5
) -> List[Dict]:
    """Merge image-index and text-index matches using Reciprocal Rank Fusion."""
    scores: Dict[str, float] = {}
    metadata_store: Dict[str, Any] = {}

    for rank, match in enumerate(img_results, start=1):
        mid = getattr(match, "id", None) or match.get("id", "")
        scores[mid] = scores.get(mid, 0.0) + 1.0 / (rrf_k + rank)
        metadata_store.setdefault(mid, getattr(match, "metadata", {}) or match.get("metadata", {}))

    for rank, match in enumerate(txt_results, start=1):
        mid = getattr(match, "id", None) or match.get("id", "")
        scores[mid] = scores.get(mid, 0.0) + 1.0 / (rrf_k + rank)
        metadata_store.setdefault(mid, getattr(match, "metadata", {}) or match.get("metadata", {}))

    sorted_ids = sorted(scores, key=lambda x: scores[x], reverse=True)[:top_k]
    return [
        {"id": mid, "score": scores[mid], "metadata": metadata_store[mid]}
        for mid in sorted_ids
    ]


class CustomVectorDb:

    def __init__(
        self,
        api_key: str,
        index_name: str,
        img_dimension: int,
        txt_dimension: int
    ):

        self.pc = Pinecone(
            api_key=api_key
        )

        # ================= Image index =================
        _img_index_name = index_name + "-image"

        existing_indexes = (
            self.pc
            .list_indexes()
            .names()
        )

        if _img_index_name not in existing_indexes:
            self.pc.create_index(
                name=_img_index_name,
                dimension=img_dimension,
                metric="cosine",
                spec=ServerlessSpec(
                    cloud="aws",
                    region="us-east-1"
                )
            )

        # Pinecone Index object for image embeddings
        self.img_index = self.pc.Index(_img_index_name)

        # =========== Text index ===============
        _txt_index_name = index_name + "-txt"

        existing_indexes = (
            self.pc
            .list_indexes()
            .names()
        )

        if _txt_index_name not in existing_indexes:
            self.pc.create_index(
                name=_txt_index_name,
                dimension=txt_dimension,
                metric="cosine",
                spec=ServerlessSpec(
                    cloud="aws",
                    region="us-east-1"
                )
            )

        # Pinecone Index object for text embeddings
        self.txt_index = self.pc.Index(_txt_index_name)

    @deprecated("Use upsert_img / upsert_txt for the new dual-index approach")
    def upsert(
        self,
        vector_id: str,
        vector: List[float],
        metadata: dict = None
    ):
        """[DEPRECATED] Single-index upsert (old unified approach)."""
        self.img_index.upsert(
            vectors=[
                {
                    "id": vector_id,
                    "values": vector,
                    "metadata": metadata or {}
                }
            ]
        )

    def upsert_img(
        self,
        vector_id: str,
        vector: List[float],
        metadata: dict = None
    ):
        """Upsert a single image embedding into the image index."""
        self.img_index.upsert(
            vectors=[
                {
                    "id": vector_id,
                    "values": vector,
                    "metadata": metadata or {}
                }
            ]
        )

    def upsert_txt(
        self,
        vector_id: str,
        vector: List[float],
        metadata: dict = None
    ):
        """Upsert a single text embedding into the text index."""
        self.txt_index.upsert(
            vectors=[
                {
                    "id": vector_id,
                    "values": vector,
                    "metadata": metadata or {}
                }
            ]
        )
    @deprecated("This method is deprecated use batch_upload instead")
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

    def batch_upload(
        self,
        dataloader,
    ):
        """Batch-upload image and text embeddings into their respective Pinecone indexes.

        Expects the dataloader to yield ``(img_feats, text_feats, item_dicts)`` tuples
        where ``img_feats`` and ``text_feats`` are already-encoded embedding tensors
        produced by ``ImageEncoder`` and ``TextEncoder`` respectively.
        """
        import math

        for (
            img_feats,
            text_feats,
            item_dicts
        ) in tqdm(dataloader):

            # ── build shared metadata list ──────────────────────────────────
            batch_items: List[dict] = []
            keys = list(item_dicts.keys())
            batch_len = len(item_dicts[keys[0]])

            for i in range(batch_len):
                item_dict: dict = {}
                for k in keys:
                    val = item_dicts[k][i]
                    if hasattr(val, "item"):
                        val = val.item()
                    if val is None or (isinstance(val, float) and math.isnan(val)):
                        continue
                    item_dict[k] = val

                # Preserve row_id for downstream chat node compatibility
                if "id" in item_dict:
                    item_dict["row_id"] = item_dict["id"]

                batch_items.append(item_dict)

            # ── upsert image embeddings ─────────────────────────────────────
            img_vectors = [
                {
                    "id": str(meta.get("id")),
                    "values": emb.tolist(),
                    "metadata": meta
                }
                for emb, meta in zip(img_feats, batch_items)
            ]
            self.img_index.upsert(vectors=img_vectors)

            # ── upsert text embeddings ──────────────────────────────────────
            txt_vectors = [
                {
                    "id": str(meta.get("id")),
                    "values": emb.tolist(),
                    "metadata": meta
                }
                for emb, meta in zip(text_feats, batch_items)
            ]
            self.txt_index.upsert(vectors=txt_vectors)
    

             
    @deprecated("This method is deprecated user query instead")
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

    def query(
        self,
        img_vec: List[float] | None,
        text_vec: List[float] | None,
        top_k: int = 5
    ) -> List[Dict]:
        """Query the dual indexes and fuse results.

        - Both vectors provided  → query both indexes, merge with RRF.
        - Only ``img_vec``       → query image index only.
        - Only ``text_vec``      → query text index only.
        """

        def _normalise(vec):
            """Convert tensor / nested list to a flat Python list."""
            if vec is None:
                return None
            if hasattr(vec, "tolist"):
                vec = vec.tolist()
            if isinstance(vec, list) and len(vec) > 0 and isinstance(vec[0], list):
                vec = vec[0]
            return vec

        img_vec = _normalise(img_vec)
        text_vec = _normalise(text_vec)

        if img_vec and text_vec:
            img_res = self.img_index.query(
                vector=img_vec,
                top_k=top_k,
                include_metadata=True
            ).get("matches", [])

            txt_res = self.txt_index.query(
                vector=text_vec,
                top_k=top_k,
                include_metadata=True
            ).get("matches", [])

            return _reciprocal_rank_fusion(
                img_results=img_res,
                txt_results=txt_res,
                rrf_k=60,
                top_k=top_k
            )

        if img_vec:
            return self.img_index.query(
                vector=img_vec,
                top_k=top_k,
                include_metadata=True
            ).get("matches", [])

        if text_vec:
            return self.txt_index.query(
                vector=text_vec,
                top_k=top_k,
                include_metadata=True
            ).get("matches", [])

        return []

    def delete_index(self):
        """Delete both image and text indexes from Pinecone."""
        self.pc.delete_index(self.img_index.name)
        self.pc.delete_index(self.txt_index.name)

    def delete_all(self):
        """Wipe all vectors from both indexes."""
        self.img_index.delete(delete_all=True)
        self.txt_index.delete(delete_all=True)

    def get_all_ids(self) -> List[str]:
        """Return the union of all vector IDs from both indexes."""
        ids: List[str] = []
        for batch in self.img_index.list():
            ids.extend([item.id for item in batch])
        return ids