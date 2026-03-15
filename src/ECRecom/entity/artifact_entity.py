from dataclasses import dataclass
import os
from src.ECRecom.constants import ARTIFACT_FOLDER


os.makedirs(ARTIFACT_FOLDER,exist_ok=True)
@dataclass
class DataIngestionArtifact:
    data_saved_path:str


@dataclass
class DataTransformationArtifact:
    vector_db_path:str    



@dataclass
class TrainingPipelineArtifact:
    vector_db_path:str
