from dotenv import load_dotenv
load_dotenv()

import sys
import os
import asyncio

import pytest

sys.path.append(os.getcwd())
src_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
sys.path.append(src_dir)

from src.pipelines.training_pipeline import TrainingPipeline
from entity.config_entity import DataIngestionConfig, DataTransformationConfig, ModelTrainingConfig, ModelEvaluationConfig


@pytest.fixture
def data_ingestion_config():
    return DataIngestionConfig()

@pytest.fixture
def data_transformation_config():
    return DataTransformationConfig()

@pytest.fixture
def model_training_config():
    config = ModelTrainingConfig()
    config.epochs = 1
    return config

@pytest.fixture
def model_evaluation_config():
    return ModelEvaluationConfig()

@pytest.fixture
def training_pipeline(data_ingestion_config, data_transformation_config, model_training_config, model_evaluation_config):
    return TrainingPipeline(
        data_ingestion_config=data_ingestion_config,
        data_transformation_config=data_transformation_config,
        model_training_config=model_training_config,
        model_evaluation_config=model_evaluation_config
    )

def test_training_pipeline_data_ingestion(training_pipeline):
    training_artifact = asyncio.run(training_pipeline.initiate())
    assert training_artifact is not None
