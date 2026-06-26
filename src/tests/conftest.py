import os
import sys
import pandas as pd
import pytest
from unittest.mock import MagicMock

# --------------------------------------------------------------------
# Global Dummy Dependencies registration to prevent heavy import-time side-effects
# --------------------------------------------------------------------
class DummyDependencies:
    def my_model(self):
        return MagicMock()
    def vectorizer(self):
        return MagicMock()
    def get_img_transformer(self):
        return MagicMock()
    def image_encoder_eval(self):
        return MagicMock()
    def text_encoder_eval(self):
        return MagicMock()
    def text_tokenizer(self):
        return MagicMock()
    def connect_data(self):
        return MagicMock()
    def df_schema(self) -> dict:
        return {
            "columns": ["id", "name", "price"],
            "dtypes": {"id": "int64", "name": "object", "price": "float64"},
            "shape": (10, 3),
            "sample": []
        }

sys.modules["src.core.dependencies"] = DummyDependencies()

from src.entity.artifact_entity import DataIngestionArtifact


# --------------------------------------------------------------------
# Simple dummy dataframe used across ingestion and validation tests
# --------------------------------------------------------------------
@pytest.fixture
def dummy_dataframe():
    """Return a small DataFrame that matches the validation schema."""
    return pd.DataFrame({
        "id": [15970, 39386, 59263],
        "product_search_description": [
            "men apparel topwear shirts navy blue fall casual turtle check men navy blue shirt",
            "men apparel bottomwear jeans blue summer casual peter england men party blue jeans",
            "women accessories watches watches silver winter casual titan women silver watch",
        ],
        "name": [
            "Turtle Check Men Navy Blue Shirt",
            "Peter England Men Party Blue Jeans",
            "Titan Women Silver Watch",
        ],
        "variant": ["Check", "Peter England Party Jeans", "Titan Watches"],
        "brand": ["Turtle", "Peter England", "Titan"],
        "price": [1195.0, 1499.0, 6500.0],
        "discounted_price": [1195.0, 1499.0, 6500.0],
        "usage": ["Casual", "Casual", "Casual"],
        "image_url": [
            "http://assets.myntassets.com/v1/images/style/properties/7a5b82d1372a7a5c6de67ae7a314fd91_images.jpg",
            "http://assets.myntassets.com/v1/images/style/properties/4850873d0c417e6480a26059f83aac29_images.jpg",
            "http://assets.myntassets.com/v1/images/style/properties/Titan-Women-Silver-Watch_b4ef04538840c0020e4829ecc042ead1_images.jpg",
        ],
    })




@pytest.fixture
def dummy_dataframe_transformed():
    """Return a small transformed DataFrame for testing."""

    return pd.DataFrame({
        "image_path": [
            "artifacts/data_transformation/images/15970.png",
            "artifacts/data_transformation/images/30805.png",
            "artifacts/data_transformation/images/59263.png",
            "artifacts/data_transformation/images/39386.png",
            "artifacts/data_transformation/images/30039.png",
            "artifacts/data_transformation/images/21379.png",
        ],
        "product_search_description": [
            "men accessories watches watches black winter casual skagen men black watch",
            "men apparel topwear tshirts grey summer casual inkfruit mens chain reaction t-shirt",
            "men apparel bottomwear jeans blue summer casual peter england men party blue jeans",
            "men apparel bottomwear jeans blue summer casual peter england men party blue jeans",
            "men accessories watches watches black winter casual skagen men black watch",
            "women accessories watches watches silver winter casual titan women silver watch",
        ],
        "label": [
            0.0,
            0.0,
            0.0,
            1.0,
            1.0,
            0.0,
        ],
    })
# --------------------------------------------------------------------
# Temporary directory fixture – reusable across tests
# --------------------------------------------------------------------
@pytest.fixture
def temp_artifact_dir(tmp_path):
    return tmp_path

# --------------------------------------------------------------------
# Fixture that creates a DataIngestionArtifact pointing to a CSV file
# --------------------------------------------------------------------
@pytest.fixture
def data_ingestion_artifact(temp_artifact_dir, dummy_dataframe):
    """Write ``dummy_dataframe`` to a CSV and return a DataIngestionArtifact.

    The validator reads this CSV during its ``initiate`` method.
    """
    csv_path = os.path.join(temp_artifact_dir, "data.csv")
    dummy_dataframe.to_csv(csv_path, index=False)
    return DataIngestionArtifact(data_saved_path=csv_path)


# --------------------------------------------------------------------
# FastAPI TestClient Fixture with Mocked Pipelines and Helpers
# --------------------------------------------------------------------
@pytest.fixture
def api_client():
    """Create a FastAPI TestClient with GraphRunnerPipeline, TrainingPipeline,
    and background thread deletion mocked to ensure fast, offline execution.
    """
    from unittest.mock import MagicMock, patch, AsyncMock
    from src.entity.artifact_entity import TrainingPipelineArtifact

    # 1. Setup mock functions/generators
    async def mock_graph_initiate(self, thread_id: str, query: str, image_path: str = ""):
        yield "data: {\"chat\": {\"messages\": [{\"content\": \"Mocked agent response\"}]}}\n\n"

    async def mock_train_initiate(self):
        return TrainingPipelineArtifact(
            train_path="dummy_train.csv",
            test_path="dummy_test.csv",
            val_path="dummy_val.csv",
            images_path="dummy_images",
            model_path="dummy_model.pt",
            evaluation_dir="dummy_eval"
        )

    # 2. Patch the pipelines and helpers before importing the FastAPI app
    p_graph = patch("src.pipelines.graph_runner_pipeline.GraphRunnerPipeline.initiate", mock_graph_initiate)
    p_train = patch("src.pipelines.training_pipeline.TrainingPipeline.initiate", mock_train_initiate)
    p_delete = patch("api.routes.user_routes.delete_thread", AsyncMock())

    p_graph.start()
    p_train.start()
    p_delete.start()

    try:
        from fastapi.testclient import TestClient
        from api.main import app
        with TestClient(app) as client:
            yield client
    finally:
        p_graph.stop()
        p_train.stop()
        p_delete.stop()

