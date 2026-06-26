from src.utils.asyncHandler import asyncHandler
from src.entity.config_entity import DataValidationConfig
from src.entity.artifact_entity import DataIngestionArtifact, DataValidationArtifact
from src.constants import ARTIFACT_FOLDER
import pandas as pd
import os
import yaml
import logging

class Data_Validator:
    def __init__(self, data_validation_config: DataValidationConfig, data_ingestion_artifact: DataIngestionArtifact):
        self.data_validation_config = data_validation_config
        self.data_ingestion_artifact = data_ingestion_artifact
        logging.info("Data_Validator initialized.")

    @asyncHandler
    async def initiate(self) -> DataValidationArtifact:
        logging.info("Starting data validation...")
        
        validation_status = True
        message = "Pass"
        primary_file_path = ""

        try:
            with open(self.data_validation_config.schema_file_path, "r") as f:
                schema = yaml.safe_load(f)
            
            required_columns = schema.get("required_columns", [])
            data = pd.read_csv(self.data_ingestion_artifact.data_saved_path)
            
            missing_cols = []
            for col in required_columns:
                if col not in data.columns:
                    missing_cols.append(col)
            
            if missing_cols:
                validation_status = False
                message = f"Missing columns: {', '.join(missing_cols)}"
                logging.error(message)

        except Exception as e:
            validation_status = False
            message = str(e)
            logging.error(message)

        output_data = {
            "status": validation_status,
            "message": message
        }

        artifact_dir = os.path.join(ARTIFACT_FOLDER, self.data_validation_config.validation_artifact_dir_name)
        os.makedirs(artifact_dir, exist_ok=True)
        file_path = os.path.join(artifact_dir, self.data_validation_config.validation_artifact_file_name)

        with open(file_path, "w") as f:
            yaml.dump(output_data, f)
        
        logging.info(f"Validation report saved.")

        return DataValidationArtifact(
            validation_status=validation_status,
            message=message,
            validation_report_file_path=file_path
        )
