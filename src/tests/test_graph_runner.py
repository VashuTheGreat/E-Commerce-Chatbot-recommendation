import sys
import os
import asyncio
import pytest
import torch
from unittest.mock import MagicMock, patch, AsyncMock
from langchain_core.messages import AIMessage, HumanMessage

sys.path.append(os.getcwd())
src_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
sys.path.append(src_dir)

from src.models.orchastrator_state import State
from src.components.graph_runner import (
    router_node,
    router_router,
    simple_chat_node,
    generate_query_node,
    retriever_node,
    final_chat_node,
    graph
)

class TestGraphRunner:

    @pytest.mark.asyncio
    async def test_router_node_simple(self):
        state = State(messages=[HumanMessage(content="hello")])
        result = await router_node(state)
        assert result["query_type"] == "simple"

    @pytest.mark.asyncio
    async def test_router_node_complex(self):
        state = State(messages=[HumanMessage(content="find me mens black watch")])
        result = await router_node(state)
        assert result["query_type"] == "complex"

    @pytest.mark.asyncio
    async def test_router_node_image(self):
        state = State(
            messages=[HumanMessage(content="hello")],
            analyse_content_paths=["image.png"]
        )
        result = await router_node(state)
        assert result["query_type"] == "complex"

    @pytest.mark.asyncio
    async def test_router_node_dummy_image(self):
        state = State(
            messages=[HumanMessage(content="hello")],
            analyse_content_paths=["000"]
        )
        result = await router_node(state)
        assert result["query_type"] == "simple"

    def test_router_router(self):
        state = {"query_type": "simple"}
        assert router_router(state) == "simple"
        state = {"query_type": "complex"}
        assert router_router(state) == "complex"

    @pytest.mark.asyncio
    async def test_simple_chat_node(self):
        state = State(messages=[HumanMessage(content="hello")])
        result = await simple_chat_node(state)
        assert "final_response" in result
        assert result["final_response"] == "Hello! How can I help you today?"

    @pytest.mark.asyncio
    async def test_generate_query_node_empty_text(self):
        state = State(
            messages=[HumanMessage(content="")],
            analyse_content_paths=["image.png"]
        )
        result = await generate_query_node(state)
        assert result["search_query"] == ""

    @pytest.mark.asyncio
    @patch("src.nodes.recommendation_generate_query_node.llm")
    async def test_generate_query_node_with_text(self, mock_llm):
        mock_response = MagicMock()
        mock_response.content = "men accessories watches black"
        mock_llm.ainvoke = AsyncMock(return_value=mock_response)

        state = State(
            messages=[HumanMessage(content="Show me black watches for men")]
        )
        result = await generate_query_node(state)
        assert result["search_query"] == "men accessories watches black"

    @pytest.mark.asyncio
    @patch("src.nodes.recommendation_retriever_node._get_search_components")
    @patch("src.nodes.recommendation_retriever_node.CustomVectorDb")
    @patch("src.nodes.recommendation_retriever_node.AutoTokenizer")
    async def test_retriever_node(self, mock_tokenizer_class, mock_vec_db_class, mock_get_components):
        mock_img_enc = MagicMock(return_value=torch.zeros(1, 256))
        mock_txt_enc = MagicMock(return_value=torch.zeros(1, 256))
        mock_mlp = MagicMock(return_value=torch.zeros(1, 512))
        mock_get_components.return_value = (mock_img_enc, mock_txt_enc, mock_mlp, "cpu", 128)

        mock_tokenizer = MagicMock()
        mock_tokenizer.return_value = {
            "input_ids": torch.zeros(1, 128, dtype=torch.long),
            "attention_mask": torch.zeros(1, 128, dtype=torch.long)
        }
        mock_tokenizer_class.from_pretrained.return_value = mock_tokenizer

        mock_db = MagicMock()
        mock_db.search.return_value = {"matches": [{"metadata": {"row_id": 123}, "score": 0.95}]}
        mock_vec_db_class.return_value = mock_db

        state = State(
            search_query="men black watch",
            analyse_content_paths=["000"]
        )
        result = await retriever_node(state)
        assert len(result["db_results"]) == 1
        assert result["db_results"][0]["metadata"]["row_id"] == 123

    @pytest.mark.asyncio
    @patch("src.nodes.recommendation_final_chat_node.llm")
    async def test_final_chat_node_with_results(self, mock_llm):
        mock_response = MagicMock()
        mock_response.content = "Here is the product 123"
        mock_llm.ainvoke = AsyncMock(return_value=mock_response)

        state = State(
            messages=[HumanMessage(content="find me a watch")],
            db_results=[{"metadata": {"row_id": 123}, "score": 0.95}],
            search_query="men watch"
        )
        result = await final_chat_node(state)
        assert result["final_response"] == "Here is the product 123"

    @pytest.mark.asyncio
    @patch("src.nodes.recommendation_final_chat_node.llm")
    async def test_final_chat_node_no_results(self, mock_llm):
        mock_response = MagicMock()
        mock_response.content = "No products found."
        mock_llm.ainvoke = AsyncMock(return_value=mock_response)

        state = State(
            messages=[HumanMessage(content="find me a watch")],
            db_results=[],
            search_query="men watch"
        )
        result = await final_chat_node(state)
        assert result["final_response"] == "No products found."
