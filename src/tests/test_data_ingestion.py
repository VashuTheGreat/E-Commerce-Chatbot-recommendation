import os
import pandas as pd
import pytest
import asyncio
from unittest.mock import AsyncMock, patch

from src.components.data_ingestion import Data_Ingestor
from src.entity.config_entity import DataIngestionConfig
from src.entity.artifact_entity import DataIngestionArtifact


@pytest.mark.asyncio
async def test_data_ingestor_initiate_success(dummy_dataframe, temp_artifact_dir, monkeypatch):
    # Patch the Connect_data to return dummy dataframe
    with patch("src.components.data_ingestion.Connect_data") as MockConnect:
        mock_instance = MockConnect.return_value
        mock_instance.load_data = AsyncMock(return_value=dummy_dataframe)
        # Patch ARTIFACT_FOLDER constant to point to temp_artifact_dir
        monkeypatch.setattr("src.components.data_ingestion.ARTIFACT_FOLDER", str(temp_artifact_dir))
        # Use default config which uses default paths
        config = DataIngestionConfig()
        ingestor = Data_Ingestor(data_ingestion_config=config)
        artifact: DataIngestionArtifact = await ingestor.initiate()
        # Verify artifact path exists and file is created
        assert isinstance(artifact, DataIngestionArtifact)
        assert os.path.isfile(artifact.data_saved_path)
        # Verify saved csv content matches dummy dataframe
        saved_df = pd.read_csv(artifact.data_saved_path)
        pd.testing.assert_frame_equal(saved_df, dummy_dataframe)
