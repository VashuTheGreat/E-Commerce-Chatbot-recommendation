import os
import pandas as pd
import pytest
import asyncio
from unittest.mock import MagicMock, patch

from src.components.data_transformation import Data_Transformator
from src.entity.config_entity import DataTransformationConfig
from src.entity.artifact_entity import DataIngestionArtifact, DataTransformationArtifact

@pytest.mark.asyncio
async def test_data_transformation_initiate_success(dummy_dataframe, temp_artifact_dir):
    """Test that Data_Transformator successfully transforms data, downloads images (mocked),
    and creates train, test, and validation csv splits.
    """
    # Create a larger dummy dataframe by repeating the dummy_dataframe to avoid stratify/split errors
    large_df = pd.concat([dummy_dataframe] * 10, ignore_index=True)
    # Ensure IDs are unique
    large_df["id"] = range(len(large_df))
    
    # Save this dataframe as the data ingestion artifact CSV
    csv_path = os.path.join(temp_artifact_dir, "ingested_large_data.csv")
    large_df.to_csv(csv_path, index=False)
    ingestion_artifact = DataIngestionArtifact(data_saved_path=csv_path)

    # Configure custom directories in temp_artifact_dir to avoid mutating production paths
    image_dir = os.path.join(temp_artifact_dir, "images")
    transformed_dir = os.path.join(temp_artifact_dir, "transformed")
    
    config = DataTransformationConfig(
        image_download_dir=image_dir,
        transformed_artifact_dir=transformed_dir,
        random_state=42,
        test_and_val_split=20.0,
        train_file_name="train.csv",
        test_file_name="test.csv",
        val_file_name="val.csv"
    )
    
    # Mock requests.get for image downloads to avoid network access
    mock_response = MagicMock()
    mock_response.content = b"mocked_image_bytes"
    mock_response.raise_for_status = MagicMock()
    
    with patch("requests.get", return_value=mock_response) as mock_get:
        transformator = Data_Transformator(
            data_ingestion_artifact=ingestion_artifact,
            data_transformation_config=config
        )
        
        # Initiate the transformation
        artifact = await transformator.initiate()
        
        # Verify the output artifact type
        assert isinstance(artifact, DataTransformationArtifact)
        
        # Verify train, test, and validation files exist
        assert os.path.isfile(artifact.train_path)
        assert os.path.isfile(artifact.test_path)
        assert os.path.isfile(artifact.val_path)
        assert os.path.isdir(artifact.images_path)
        
        # Check that mocked image files are actually written
        for image_id in large_df["id"]:
            expected_image_path = os.path.join(image_dir, f"{image_id}.png")
            assert os.path.isfile(expected_image_path)
            
        # Verify the CSV split contents
        train_df = pd.read_csv(artifact.train_path)
        test_df = pd.read_csv(artifact.test_path)
        val_df = pd.read_csv(artifact.val_path)
        
        # Check columns
        for df in [train_df, test_df, val_df]:
            assert "image_path" in df.columns
            assert "product_search_description" in df.columns
            assert "label" in df.columns
            assert set(df["label"].unique()).issubset({0.0, 1.0})
            
        # Total rows should equal large_df rows * 2 (positive + negative)
        total_rows = len(train_df) + len(test_df) + len(val_df)
        assert total_rows == len(large_df) * 2
