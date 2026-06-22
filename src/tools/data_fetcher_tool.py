import logging
import json
import httpx
from langchain_core.tools import StructuredTool
from pydantic import BaseModel, Field
from src.LLMResponse.constants import DB_FETCH_URL

class DataFetcherInput(BaseModel):
    query: str = Field(description="A descriptive product search query (e.g. 'men navy blue casual shirt').")
    k: int | str = Field(default=5, description="Number of recommendations to retrieve (default 5).")

class DataFetcherTool:
    def __init__(self, max_calls: int = 3):
        self.max_calls = max_calls
        self.call_count = 0

    def reset(self):
        self.call_count = 0

    async def _run(self, query: str, k: int | str = 5) -> str:
        if self.call_count >= self.max_calls:
            logging.warning("fetch_recommendations_from_db — tool calling limit crossed")
            return json.dumps({"status": "error", "message": "Tool calling limit crossed. Use the data already fetched."})
        
        self.call_count += 1
        
        try:
            k = int(k)
        except (ValueError, TypeError):
            k = 5
            
        logging.info(f"fetch_recommendations_from_db called — query='{query}', k={k}, call_count={self.call_count}")

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    DB_FETCH_URL,
                    json={"query": query, "k": k}
                )
                response.raise_for_status()
                data = response.json()
                results_len = len(data.get("results", [])) if isinstance(data, dict) else "unknown"
                logging.info(f"fetch_recommendations_from_db — received {results_len} results from DB")
                return json.dumps(data)

        except httpx.HTTPStatusError as e:
            logging.error(f"fetch_recommendations_from_db — HTTP error: {e.response.status_code} — {e.response.text}")
            return json.dumps({"status": "error", "message": f"HTTP {e.response.status_code}", "detail": str(e)})

        except Exception as e:
            logging.error(f"fetch_recommendations_from_db — unexpected error: {e}")
            return json.dumps({"status": "error", "message": str(e)})

fetcher_instance = DataFetcherTool(max_calls=3)

fetch_recommendations_from_db = StructuredTool.from_function(
    coroutine=fetcher_instance._run,
    name="fetch_recommendations_from_db",
    description="Fetch product recommendations from the database given a search query.",
    args_schema=DataFetcherInput
)