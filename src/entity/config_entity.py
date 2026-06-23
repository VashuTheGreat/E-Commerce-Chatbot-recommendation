from dataclasses import dataclass
import os
from src.constants import ARTIFACT_FOLDER, DATA_PATH,DATA_ARTIFACT_FOLDER_NAME,DATA_ARTIFACT_FILE_NAME,VECTOR_STORE_SAVING_DIR_PATH,SCHEMA_FILE_PATH,DATA_VALIDATION_ARTIFACT_DIR_NAME,DATA_VALIDATION_ARTIFACT_FILE_NAME,IMAGE_DOWNLOAD_DIR,RANDOM_STATE,TRANSFORMED_ARTIFACT_DIR,TEST_AND_VAL_SPLIT,TRAIN_FILE_NAME,TEST_FILE_NAME,VAL_FILE_NAME
@dataclass
class DataIngestionConfig:
    data_path:str=DATA_PATH
    data_artifact_folder_name:str=DATA_ARTIFACT_FOLDER_NAME
    data_artifact_file_name:str=DATA_ARTIFACT_FILE_NAME


@dataclass
class DataValidationConfig:
    schema_file_path:str=SCHEMA_FILE_PATH
    validation_artifact_dir_name:str=DATA_VALIDATION_ARTIFACT_DIR_NAME
    validation_artifact_file_name:str=DATA_VALIDATION_ARTIFACT_FILE_NAME


@dataclass
class DataTransformationConfig:
    vector_store_saving_dir:str=VECTOR_STORE_SAVING_DIR_PATH
    image_download_dir:str=IMAGE_DOWNLOAD_DIR
    random_state:int=RANDOM_STATE
    transformed_artifact_dir:str=TRANSFORMED_ARTIFACT_DIR
    test_and_val_split:float=TEST_AND_VAL_SPLIT
    train_file_name:str=TRAIN_FILE_NAME
    test_file_name:str=TEST_FILE_NAME
    val_file_name:str=VAL_FILE_NAME


@dataclass
class ModelTrainingConfig:
    max_len: int = 128
    image_feature_output: int = 2048
    text_feature_output: int = 768
    feature_expand_dim: int = (2048 + 768) * 2
    final_feature_output: int = 512
    learning_rate: float = 0.0001
    model_name: str = "multimodal_model.pt"
    model_dir: str = os.path.join(ARTIFACT_FOLDER, "model_training", "checkpoints")
    epochs: int = 20
    patience: int = 3
    batch_size: int = 32
    dropout: float = 0.6
    cache_dir: str = os.path.join(ARTIFACT_FOLDER, "model_training", "cache")
    train_file_path: str = os.path.join(TRANSFORMED_ARTIFACT_DIR, TRAIN_FILE_NAME)

Config = ModelTrainingConfig


@dataclass
class ModelEvaluationConfig:
    evaluation_artifact_dir: str = os.path.join(ARTIFACT_FOLDER, "model_evaluation")
    metrics_file_name: str = "metrics.yaml"
    loss_plot_file_name: str = "loss_plot.png"
    confusion_matrix_file_name: str = "confusion_matrix.png"
    mlflow_experiment_name: str = "E-Commerce-Chatbot-Recommendation"
    mlflow_run_name: str = "Multimodal_Training_Run"
    mlflow_model_name: str = "multimodal_model_registry"



    
    