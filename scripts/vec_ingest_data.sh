#!/bin/bash

echo "Starting Vector Storing (dual-index mode)"
echo "Ingesting image + text embeddings into separate Pinecone indexes..."

cd "$(dirname "$0")/.." || exit 1

python3 -c "
import asyncio
import sys
from dotenv import load_dotenv
load_dotenv()
from src.logger import *
from src.components.vectorizing_data import Vectorizer


async def main():
    override = False
    if '--override' in sys.argv:
        idx = sys.argv.index('--override')
        if idx + 1 < len(sys.argv):
            override = sys.argv[idx + 1].lower() in ('true', '1', 'yes')
        else:
            override = True
    # ingest_vectors: new dual-index approach
    # ImageEncoder -> image Pinecone index
    # TextEncoder  -> text  Pinecone index
    # (ingest_vec is deprecated - used old MyModel.predict_emb single merged embedding)
    await Vectorizer().ingest_vectors(override=override)

asyncio.run(main())
" "$@"
