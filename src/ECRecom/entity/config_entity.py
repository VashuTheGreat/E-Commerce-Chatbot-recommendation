from dataclasses import dataclass
from src.ECRecom.constants import DATA_PATH,DATA_ARTIFACT_FOLDER_NAME,DATA_ARTIFACT_FILE_NAME,VECTOR_STORE_SAVING_DIR_PATH
@dataclass
class DataIngestionConfig:
    data_path:str=DATA_PATH
    data_artifact_folder_name:str=DATA_ARTIFACT_FOLDER_NAME
    data_artifact_file_name:str=DATA_ARTIFACT_FILE_NAME


@dataclass
class DataTransformationConfig:
    vector_store_saving_dir:str=VECTOR_STORE_SAVING_DIR_PATH





    
    