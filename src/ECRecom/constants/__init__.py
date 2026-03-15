import os
DATA_PATH=os.path.join("data","final_filtered_data.csv")
ARTIFACT_FOLDER="artifacts"
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
DATA_ARTIFACT_FOLDER_NAME = "data_ingestion"
DATA_ARTIFACT_FILE_NAME = "data.csv"
VECTOR_STORE_SAVING_DIR_PATH = os.path.join(ARTIFACT_FOLDER, "transformation", "vector_db")
VECTOR_DB_PATH=os.path.join(VECTOR_STORE_SAVING_DIR_PATH, "fiase")
LOGS_DIR = "logs"



BATCH_SIZE = 500
