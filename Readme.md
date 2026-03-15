# 🛍️ E-Commerce Chatbot Recommendation System

An AI-powered recommendation system that identifies products and suggests similar items based on visual and textual features. Built with LangChain, FAISS, and Sentence Transformers.

---

## 🚀 Key Features

- **Semantic Product Search**: Find similar products based on natural language descriptions.
- **Visual Intelligence**: Integrate image-based discovery (via `app.py`).
- **Metadata-Rich Results**: Displays brand, price, usage, and image URLs for recommendations.
- **Efficient Vector Search**: Uses FAISS for high-performance similarity fetching.
- **Robust Pipelines**: Automated training and prediction pipelines with comprehensive logging.

---

## 🛠️ Tech Stack

- **Core**: Python
- **Orchestration**: LangChain
- **Vector Database**: FAISS
- **Embeddings**: Sentence Transformers (`all-MiniLM-L6-v2`)
- **Package Manager**: [uv](https://github.com/astral-sh/uv)
- **UI (Optional)**: Streamlit

---

## 📂 Project Structure

```text
E-Commerce-Chatbot-recommendation/
├── src/ECRecom/
│   ├── components/       # Data ingestion, transformation, similarity fetch
│   ├── data_access/      # Data loading and vector DB interface
│   ├── entity/           # Config and Artifact entities
│   ├── pipelines/        # Training and Prediction pipeline logic
│   └── constants/        # Project-wide constants (paths, models, etc.)
├── artifacts/            # Generated data and vector DB artifacts
├── logs/                 # Execution logs
├── tests/                # Test scripts for pipelines
├── app.py                # Main application UI
├── chat.py               # Chat interaction logic
└── main.py               # Entry point
```

---

## ⚙️ Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/VashuTheGreat/E-Commerce-Chatbot-recommendation.git
   cd E-Commerce-Chatbot-recommendation
   ```

2. **Install dependencies**:
   Using `uv` (recommended):
   ```bash
   uv sync
   ```
   Or using `pip`:
   ```bash
   pip install -r requirements.txt
   ```

3. **Environment Setup**:
   Create a `.env` file and add your configuration (e.g., API keys if applicable).

---

## 🏃 Usage

### 1. Training Pipeline
Rerun the data ingestion and transformation to rebuild the vector database:
```bash
uv run src/ECRecom/tests/run_training_pipeline.py
```

### 2. Prediction Pipeline
Test similarity results:
```bash
uv run src/ECRecom/tests/run_prediction_pipeline.py
```

### 3. Run the Chat App
```bash
uv run chat.py
```

---

## 🔹 License

Distributed under the [MIT License](LICENSE).

---

Made with ❤️ by [VashuTheGreat](https://github.com/VashuTheGreat)
