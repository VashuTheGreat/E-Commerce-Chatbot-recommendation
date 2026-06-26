import sys
from unittest.mock import MagicMock, patch, AsyncMock
import pytest

# -------------------------------------------------------------------------
# 1. Global Module Mocks (Setup globally, but started/stopped via fixture)
# -------------------------------------------------------------------------
mock_mymodel_class = MagicMock()
mock_vectorizer_class = MagicMock()
mock_image_encoder_class = MagicMock()
mock_text_encoder_class = MagicMock()
mock_tokenizer_class = MagicMock()
mock_chat_groq_class = MagicMock()
mock_read_csv = MagicMock()

# Setup default dummy returns for pandas read_csv (for df_schema load)
mock_df = MagicMock()
mock_df.columns.tolist.return_value = ["id", "image_url", "product_search_description", "label"]
mock_df.dtypes.items.return_value = [
    ("id", "int64"),
    ("image_url", "object"),
    ("product_search_description", "object"),
    ("label", "float64")
]
mock_df.shape = (10, 4)
mock_df.head.return_value.to_dict.return_value = []
mock_read_csv.return_value = mock_df

# Register patches for heavy dependencies to prevent download/DB init at import time
patches = [
    patch("src.entity.model.MyModel", mock_mymodel_class),
    patch("src.components.vectorizing_data.Vectorizer", mock_vectorizer_class),
    patch("src.models.muti_model.ImageEncoder", mock_image_encoder_class),
    patch("src.models.muti_model.TextEncoder", mock_text_encoder_class),
    patch("transformers.AutoTokenizer", mock_tokenizer_class),
    patch("langchain_groq.ChatGroq", mock_chat_groq_class),
    patch("pandas.read_csv", mock_read_csv)
]

@pytest.fixture(scope="module", autouse=True)
def setup_graph_mocks():
    """Autouse fixture that starts all global patches at the start of the module
    and stops them at the end, preventing mock leakage to other test files.
    """
    for p in patches:
        p.start()
    yield
    for p in patches:
        p.stop()

# -------------------------------------------------------------------------
# 2. Pytest Test Cases
# -------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_graph_runner_pipeline_casual_chat():
    """Test that GraphRunnerPipeline correctly routes to casual chat and returns response."""
    # Import locally to ensure patches are already active
    import json
    from langchain_core.messages import AIMessage
    from src.pipelines.graph_runner_pipeline import GraphRunnerPipeline
    from src.models.agent_models import Orchastrator_Output

    # Reset mocks
    mock_chat_groq_class.reset_mock()
    mock_llm = mock_chat_groq_class.return_value
    
    # Configure the Orchestrator output to route to chat_node (casual conversation)
    mock_structured_output = AsyncMock()
    mock_structured_output.ainvoke.return_value = Orchastrator_Output(
        redirect_to="chat_node",
        querie=""
    )
    mock_llm.with_structured_output.return_value = mock_structured_output
    
    # Configure the Chat LLM output
    mock_chat_output = AsyncMock()
    mock_chat_output.ainvoke.return_value = AIMessage(content="Hello! How can I help you today?")
    mock_llm.bind_tools.return_value = mock_chat_output
    
    pipeline = GraphRunnerPipeline()
    
    chunks = []
    # Execute the pipeline query
    async for chunk in pipeline.initiate(thread_id="test_thread_1", query="Hello"):
        chunks.append(chunk)
        
    assert len(chunks) > 0
    # The pipeline yields SSE-formatted json lines starting with "data: "
    first_chunk_str = chunks[0].replace("data: ", "").strip()
    first_chunk = json.loads(first_chunk_str)
    
    # The chunk output should reflect updates from orchestrator or chat nodes
    assert "orchestrator" in first_chunk or "chat" in first_chunk
    
    # Verify mock invokations
    mock_llm.with_structured_output.assert_called_once_with(Orchastrator_Output)
    mock_structured_output.ainvoke.assert_called_once()
    mock_llm.bind_tools.assert_called_once()
    mock_chat_output.ainvoke.assert_called_once()


@pytest.mark.asyncio
async def test_graph_runner_pipeline_retrieval():
    """Test that GraphRunnerPipeline correctly routes to retriever, queries vector db, and returns recommendations."""
    # Import locally to ensure patches are already active
    import torch
    from langchain_core.messages import AIMessage
    from src.pipelines.graph_runner_pipeline import GraphRunnerPipeline
    from src.models.agent_models import Orchastrator_Output

    # Reset mocks
    mock_chat_groq_class.reset_mock()
    mock_mymodel_class.reset_mock()
    mock_vectorizer_class.reset_mock()
    
    mock_llm = mock_chat_groq_class.return_value
    
    # Configure the Orchestrator output to route to retreiver_node
    mock_structured_output = AsyncMock()
    mock_structured_output.ainvoke.return_value = Orchastrator_Output(
        redirect_to="retreiver_node",
        querie="blue jeans"
    )
    mock_llm.with_structured_output.return_value = mock_structured_output
    
    # Configure MyModel instance predict_emb mock
    mock_mymodel_inst = mock_mymodel_class.return_value
    mock_mymodel_inst.predict_emb.return_value = torch.zeros((1, 512))
    mock_mymodel_inst.load_model = MagicMock()
    
    # Configure Vectorizer (vector database) mock query result
    mock_vectorizer_inst = mock_vectorizer_class.return_value
    mock_match_1 = MagicMock()
    mock_match_1.id = "101"
    mock_match_1.score = 0.95
    mock_match_1.metadata = {"name": "Sleek Blue Jeans", "price": 1200.0}
    
    mock_vectorizer_inst.get_similar_data = AsyncMock(return_value={
        "matches": [mock_match_1]
    })
    
    # Configure Chat LLM output to recommend the product
    mock_chat_output = AsyncMock()
    mock_chat_output.ainvoke.return_value = AIMessage(content="I found these Sleek Blue Jeans for you.")
    mock_llm.bind_tools.return_value = mock_chat_output
    
    pipeline = GraphRunnerPipeline()
    
    chunks = []
    # Execute the pipeline retrieval query
    async for chunk in pipeline.initiate(thread_id="test_thread_2", query="Show me blue jeans"):
        chunks.append(chunk)
        
    assert len(chunks) > 0
    
    # Verify the vectorizer was queried
    mock_vectorizer_inst.get_similar_data.assert_called_once()
    assert mock_mymodel_inst.predict_emb.called
    
    # Verify chat was called
    mock_chat_output.ainvoke.assert_called_once()
