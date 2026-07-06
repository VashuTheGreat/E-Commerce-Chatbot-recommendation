from src.core.dependencies import vectorizer
from typing import List, Literal

def _serialize_matches(matches) -> List[dict]:
    """Convert Pinecone ScoredVector objects (or plain dicts) to JSON-serializable dicts."""
    result = []
    for m in matches:
        result.append({
            "id": getattr(m, "id", None) or m.get("id", ""),
            "score": getattr(m, "score", None) or m.get("score", 0.0),
            "metadata": dict(getattr(m, "metadata", None) or m.get("metadata", {})),
        })
    return result

class SimilarProductPipeline:
    def __init__(self):
        self.vectorizer = vectorizer()

    async def initiate(self, vector: List[int], type: Literal['image', 'text']):
        if type == 'image':
            vectorized_data = await self.vectorizer.invoke(img_vec=vector, text_vec=None)
        elif type == 'text':
            vectorized_data = await self.vectorizer.invoke(img_vec=None, text_vec=vector)
        return _serialize_matches(vectorized_data)