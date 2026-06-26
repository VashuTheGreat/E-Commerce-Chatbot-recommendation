import os
import pandas as pd
import pytest
import asyncio
from unittest.mock import AsyncMock, patch

from src.components.data_validation import Data_Validator
from src.entity.config_entity import DataValidationConfig, DataIngestionConfig
from src.entity.artifact_entity import DataValidationArtifact


@pytest.mark.asyncio
async def test_data_validation_initiate_success(dummy_dataframe, data_ingestion_artifact, monkeypatch):
    """Test that Data_Validator validates a dummy dataframe and writes a yaml report.

    The test patches ``pandas.read_csv`` used inside ``Data_Validator`` to return the
    ``dummy_dataframe`` fixture, avoiding any file‑system I/O.
    """
    # Patch pandas.read_csv to return the dummy dataframe
    with patch("pandas.read_csv", return_value=dummy_dataframe) as mock_read_csv:
        # Initialise validator with required configs and the ingestion artifact
        data_validation_config = DataValidationConfig()
        validator = Data_Validator(data_validation_config=data_validation_config,
                                 data_ingestion_artifact=data_ingestion_artifact)
        # Execute validation
        artifact: DataValidationArtifact = await validator.initiate()

        # Verify we got a proper artifact
        assert isinstance(artifact, DataValidationArtifact)
        # The validator writes a yaml report; ensure the file exists
        assert os.path.isfile(artifact.validation_report_file_path)
        # Optional sanity check: the yaml should contain a "status" key
        with open(artifact.validation_report_file_path) as f:
            yaml_content = f.read()
        assert "status" in yaml_content
