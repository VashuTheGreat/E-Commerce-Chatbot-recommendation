import pytest
import json
from unittest.mock import MagicMock, AsyncMock, patch
import torch
from langchain_core.messages import AIMessage
from src.pipelines.graph_runner_pipeline import GraphRunnerPipeline
from src.models.agent_models import Orchastrator_Output

@pytest.mark.asyncio
async def test_graph_runner_pipeline_casual_chat():
    """Test that GraphRunnerPipeline correctly routes to casual chat and returns response."""
    # Configure mock LLM response
    mock_structured_output = AsyncMock()
    mock_structured_output.ainvoke.return_value = Orchastrator_Output(
        redirect_to="chat_node",
        querie=""
    )
    
    mock_chat_output = AsyncMock()
    mock_chat_output.ainvoke.return_value = AIMessage(content="Hello! How can I help you today?")
    
    mock_llm = MagicMock()
    mock_llm.with_structured_output.return_value = mock_structured_output
    mock_llm.bind_tools.return_value = mock_chat_output
    
    # Patch the llm inside agents_nodes directly
    with patch("src.nodes.agents_nodes.llm", mock_llm):
        pipeline = GraphRunnerPipeline()
        
        chunks = []
        async for chunk in pipeline.initiate(thread_id="test_thread_1", query="Hello"):
            chunks.append(chunk)
            
        assert len(chunks) > 0
        first_chunk_str = chunks[0].replace("data: ", "").strip()
        first_chunk = json.loads(first_chunk_str)
        
        # Verify execution path
        assert "orchestrator" in first_chunk or "chat" in first_chunk
        mock_llm.with_structured_output.assert_called_once_with(Orchastrator_Output)
        mock_structured_output.ainvoke.assert_called_once()
        mock_llm.bind_tools.assert_called_once()
        mock_chat_output.ainvoke.assert_called_once()


@pytest.mark.skip(
    reason=(
        "Written against the deprecated retreiver_node which used "
        "vectorizer.get_similar_data() + MyModel.predict_emb(). "
        "The active node is now retriever_node_v2 which calls "
        "vectorizer.invoke() directly. Update this test for the new node."
    )
)
@pytest.mark.asyncio
async def test_graph_runner_pipeline_retrieval():

    """Test that GraphRunnerPipeline correctly routes to retriever, queries vector db, and returns recommendations."""
    # Configure mock LLM response for orchestrator (routes to retreiver)
    mock_structured_output = AsyncMock()
    mock_structured_output.ainvoke.return_value = Orchastrator_Output(
        redirect_to="retreiver_node",
        querie="blue jeans"
    )
    
    # Configure mock LLM response for chat (recommendation response)
    mock_chat_output = AsyncMock()
    mock_chat_output.ainvoke.return_value = AIMessage(content="I found these Sleek Blue Jeans for you.")
    
    mock_llm = MagicMock()
    mock_llm.with_structured_output.return_value = mock_structured_output
    mock_llm.bind_tools.return_value = mock_chat_output
    
    # Configure MyModel instance predict_emb mock
    mock_mymodel_inst = MagicMock()
    mock_mymodel_inst.predict_emb.return_value = torch.zeros((1, 512))
    mock_mymodel_inst.load_model = MagicMock()
    
    # Configure Vectorizer (vector database) mock query result
    mock_vectorizer_inst = MagicMock()
    mock_match_1 = MagicMock()
    mock_match_1.id = "101"
    mock_match_1.score = 0.95
    mock_match_1.metadata = {"name": "Sleek Blue Jeans", "price": 1200.0}
    mock_vectorizer_inst.get_similar_data = AsyncMock(return_value={
        "matches": [mock_match_1]
    })
    
    # Patch all the dependencies in agents_nodes directly
    with patch("src.nodes.agents_nodes.llm", mock_llm), \
         patch("src.nodes.agents_nodes.my_model", return_value=mock_mymodel_inst), \
         patch("src.nodes.agents_nodes.vectorizer", return_value=mock_vectorizer_inst), \
         patch("src.nodes.agents_nodes._get_image_feat", return_value=torch.zeros((1, 2048))), \
         patch("src.nodes.agents_nodes._get_text_feat", return_value=torch.zeros((1, 768))):
         
        pipeline = GraphRunnerPipeline()
        
        chunks = []
        async for chunk in pipeline.initiate(thread_id="test_thread_2", query="Show me blue jeans"):
            chunks.append(chunk)
            
        assert len(chunks) > 0
        
        # Verify vector db call and model predictions
        mock_vectorizer_inst.get_similar_data.assert_called_once()
        mock_mymodel_inst.predict_emb.assert_called_once()
        mock_chat_output.ainvoke.assert_called_once()


@pytest.mark.asyncio
async def test_graph_runner_pipeline_retrieval_v2():
    """Test that GraphRunnerPipeline correctly routes to retriever_node_v2,
    calls vectorizer.invoke(), and returns product recommendations."""

    # ── Orchestrator: route to retriever ────────────────────────────────
    mock_structured_output = AsyncMock()
    mock_structured_output.ainvoke.return_value = Orchastrator_Output(
        redirect_to="retreiver_node",
        querie="blue jeans"
    )

    # ── Chat: final recommendation response ─────────────────────────────
    mock_chat_output = AsyncMock()
    mock_chat_output.ainvoke.return_value = AIMessage(
        content="I found these Sleek Blue Jeans for you."
    )

    mock_llm = MagicMock()
    mock_llm.with_structured_output.return_value = mock_structured_output
    mock_llm.bind_tools.return_value = mock_chat_output

    # ── Vectorizer mock: invoke() returns list of plain dicts (retriever_node_v2 format) ──
    mock_vectorizer_inst = MagicMock()
    mock_vectorizer_inst.invoke = AsyncMock(return_value=[
        {
            "id": "101",
            "score": 0.95,
            "metadata": {"name": "Sleek Blue Jeans", "price": 1200.0}
        }
    ])

    with patch("src.nodes.agents_nodes.llm", mock_llm), \
         patch("src.nodes.agents_nodes.vectorizer", return_value=mock_vectorizer_inst), \
         patch("src.nodes.agents_nodes._get_text_feat", return_value=torch.zeros((1, 768))), \
         patch("src.nodes.agents_nodes._get_image_feat", return_value=torch.zeros((1, 2048))):

        pipeline = GraphRunnerPipeline()

        chunks = []
        async for chunk in pipeline.initiate(thread_id="test_thread_v2", query="Show me blue jeans"):
            chunks.append(chunk)

        assert len(chunks) > 0

        # retriever_node_v2 must have called invoke() once
        mock_vectorizer_inst.invoke.assert_called_once()

        # chat LLM must have been invoked for the final response
        mock_chat_output.ainvoke.assert_called_once()

