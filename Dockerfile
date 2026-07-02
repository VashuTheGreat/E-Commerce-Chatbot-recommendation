FROM python:3.13-slim

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


EXPOSE 7860

# Run FastAPI app
CMD ["python", "main.py"]
