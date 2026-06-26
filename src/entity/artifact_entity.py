from dataclasses import dataclass
import os
from src.constants import ARTIFACT_FOLDER


os.makedirs(ARTIFACT_FOLDER,exist_ok=True)
@dataclass
class DataIngestionArtifact:
    data_saved_path:str


@dataclass
class DataValidationArtifact:
    validation_status:bool
    message:str
    validation_report_file_path:str


@dataclass
class DataTransformationArtifact:
    train_path:str
    test_path:str
    val_path:str
    images_path:str



@dataclass
class ModelTrainingArtifact:
    model_path:str
    is_trained:bool
    message:str



@dataclass
class ModelEvaluationArtifact:
    evaluation_dir:str
    metrics_file_path:str
    loss_plot_path:str
    confusion_matrix_path:str
    is_evaluated:bool



@dataclass
class TrainingPipelineArtifact:
    train_path:str
    test_path:str
    val_path:str
    images_path:str
    model_path:str
    evaluation_dir:str
