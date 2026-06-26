FROM python:3.12-slim

WORKDIR /app

# Install system dependencies required for OpenCV (cv2)
RUN apt-get update && apt-get install -y \
    libxcb1 \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency files first (better caching)
COPY requirements.txt pyproject.toml ./

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy rest of the application
COPY . .

# --- Build-time secrets (passed via --build-arg in CI/CD) ---
ARG PINECONE_API_KEY
ARG GROQ_API_KEY
ARG MLFLOW_API_KEY
ARG DAGSHUB_OWNER
ARG DAGSHUB_REPO
ARG HUGGINGFACE_API_KEY

# Make them available as environment variables for the shell script
ENV PINECONE_API_KEY=${PINECONE_API_KEY}
ENV GROQ_API_KEY=${GROQ_API_KEY}
ENV MLFLOW_API_KEY=${MLFLOW_API_KEY}
ENV DAGSHUB_OWNER=${DAGSHUB_OWNER}
ENV DAGSHUB_REPO=${DAGSHUB_REPO}
ENV HUGGINGFACE_API_KEY=${HUGGINGFACE_API_KEY}

# uploading vectordb
RUN chmod 777 scripts/vec_ingest_data.sh && ./scripts/vec_ingest_data.sh

EXPOSE 7860

# Run FastAPI app
CMD ["python", "main.py"]