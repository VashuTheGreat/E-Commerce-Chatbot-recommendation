import os
import pandas as pd
import pytest

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
