from src.utils.asyncHandler import asyncHandler
from src.entity.config_entity import DataIngestionConfig,DataTransformationConfig,DataValidationConfig,ModelTrainingConfig,ModelEvaluationConfig
from src.components.data_ingestion import Data_Ingestor
from src.components.data_validation import Data_Validator
from src.components.data_transformation import Data_Transformator
from src.components.model_trainer import Model_Trainer
from src.components.model_evaluation import Model_Evaluation
from src.entity.artifact_entity import TrainingPipelineArtifact
import logging

class TrainingPipeline:
    def __init__(self,data_ingestion_config:DataIngestionConfig,data_transformation_config:DataTransformationConfig,data_validation_config:DataValidationConfig=DataValidationConfig(),model_training_config:ModelTrainingConfig=ModelTrainingConfig(),model_evaluation_config:ModelEvaluationConfig=ModelEvaluationConfig()):
        self.data_ingestion_config=data_ingestion_config
        self.data_transformation_config=data_transformation_config
        self.data_validation_config=data_validation_config
        self.model_training_config=model_training_config
        self.model_evaluation_config=model_evaluation_config
        logging.info("TrainingPipeline initialized.")

    @asyncHandler
    async def initiate(self)->TrainingPipelineArtifact:
        logging.info("Starting Training Pipeline...")
        data_ingestor=Data_Ingestor(
            data_ingestion_config=self.data_ingestion_config
        )
        data_ingestion_artifact=await data_ingestor.initiate()
        data_validator=Data_Validator(
            data_validation_config=self.data_validation_config,
            data_ingestion_artifact=data_ingestion_artifact
        )
        validation_artifact = await data_validator.initiate()
        if not validation_artifact.validation_status:
            raise Exception(f"Data Validation failed: {validation_artifact.message}")
        data_transformation = Data_Transformator(
            data_ingestion_artifact=data_ingestion_artifact,
            data_transformation_config=self.data_transformation_config
        )
        data_transformation_artifact = await data_transformation.initiate()
        model_trainer = Model_Trainer(
            data_transformation_artifact=data_transformation_artifact,
            model_training_config=self.model_training_config
        )
        model_training_artifact = await model_trainer.initiate()
        if not model_training_artifact.is_trained:
            raise Exception(f"Model Training failed: {model_training_artifact.message}")
        model_evaluation = Model_Evaluation(
            model_evaluation_config=self.model_evaluation_config,
            data_transformation_artifact=data_transformation_artifact,
            model_training_artifact=model_training_artifact,
            model_training_config=self.model_training_config
        )
        model_evaluation_artifact = await model_evaluation.initiate()
        if not model_evaluation_artifact.is_evaluated:
            raise Exception("Model Evaluation failed.")
        logging.info("Training Pipeline completed successfully.")
        return TrainingPipelineArtifact(
            train_path=data_transformation_artifact.train_path,
            test_path=data_transformation_artifact.test_path,
            val_path=data_transformation_artifact.val_path,
            images_path=data_transformation_artifact.images_path,
            model_path=model_training_artifact.model_path,
            evaluation_dir=model_evaluation_artifact.evaluation_dir
        )