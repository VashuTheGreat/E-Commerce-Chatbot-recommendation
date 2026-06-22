from src.entity.artifact_entity import DataTransformationArtifact, ModelTrainingArtifact
from src.entity.config_entity import ModelTrainingConfig
from src.entity.model import MyModel
from src.utils.asyncHandler import asyncHandler
import pandas as pd
import os
import logging
from torch.utils.data import DataLoader
from src.models.muti_model import MultimodalDataset

class Model_Trainer:
    def __init__(self, data_transformation_artifact: DataTransformationArtifact, model_training_config: ModelTrainingConfig):
        self.data_transformation_artifact = data_transformation_artifact
        self.model_training_config = model_training_config
        self.model_training_config.train_file_path = self.data_transformation_artifact.train_path
        self.model = MyModel(config=self.model_training_config)

    @asyncHandler
    async def initiate(self) -> ModelTrainingArtifact:
        logging.info("Entered model training step")
        try:
            
            train_df = pd.read_csv(self.data_transformation_artifact.train_path)
            val_df = pd.read_csv(self.data_transformation_artifact.val_path)

            train_dataset = MultimodalDataset(
                data_frame=train_df,
                config=self.model_training_config
            )
            val_dataset = MultimodalDataset(
                data_frame=val_df,
                config=self.model_training_config
            )

            train_loader = DataLoader(
                train_dataset,
                batch_size=self.model_training_config.batch_size,
                shuffle=True
            )
            val_loader = DataLoader(
                val_dataset,
                batch_size=self.model_training_config.batch_size,
                shuffle=False
            )

            self.model.train(train_data_loader=train_loader, val_data_loader=val_loader)
            
            model_path = os.path.join(self.model_training_config.model_dir, self.model_training_config.model_name)
            logging.info("Exited model training step")

            return ModelTrainingArtifact(
                model_path=model_path,
                is_trained=True,
                message="Model training completed successfully"
            )
        except Exception as e:
            logging.error(f"Model training failed: {str(e)}")
            return ModelTrainingArtifact(
                model_path="",
                is_trained=False,
                message=f"Model training failed: {str(e)}"
            )