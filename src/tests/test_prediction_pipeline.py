import torch
import asyncio
import os
import sys
import torch
sys.path.append(os.getcwd())
import random
from dotenv import load_dotenv

load_dotenv()

from src.components.vectorizing_data import Vectorizer

async def test_search():
    print("Initializing Vectorizer...", flush=True)
    v = Vectorizer()
    
    # Generate a random query vector matching the index dimension
    query_vector = torch.randn(size=(1, v.config.final_feature_output))
    
    print(f"Running vector search with random {v.config.final_feature_output}d vector...", flush=True)
    results = await v.get_similar_data(vector=query_vector, top_k=5)
    
    print("\n--- Search Results ---", flush=True)
    matches = results.get("matches", [])
    if not matches:
        print("No matches found.", flush=True)
    else:
        for idx, match in enumerate(matches):
            print(f"\nMatch {idx+1}:", flush=True)
            print(f"  ID: {match.get('id')}", flush=True)
            print(f"  Score: {match.get('score'):.4f}", flush=True)
            print(f"  Metadata: {match.get('metadata')}", flush=True)

if __name__ == "__main__":
    asyncio.run(test_search())
