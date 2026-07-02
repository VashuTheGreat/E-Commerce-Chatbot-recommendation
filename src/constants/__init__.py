import os
DATA_PATH="hf://datasets/VashuTheGreat2/E-Commerce-Product-Recommendation/data.csv"
ARTIFACT_FOLDER="artifacts"
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
DATA_ARTIFACT_FOLDER_NAME = "data_ingestion"
DATA_ARTIFACT_FILE_NAME = "data.csv"
VECTOR_STORE_SAVING_DIR_PATH = os.path.join(ARTIFACT_FOLDER, "transformation", "vector_db")
VECTOR_DB_PATH=os.path.join(VECTOR_STORE_SAVING_DIR_PATH, "fiase")
LOGS_DIR = "logs"
BATCH_SIZE = 500
SCHEMA_FILE_PATH = os.path.join("src", "config", "data_validation.yml")
DATA_VALIDATION_ARTIFACT_DIR_NAME = "validation"
DATA_VALIDATION_ARTIFACT_FILE_NAME = "output.yaml"
IMAGE_DOWNLOAD_DIR = os.path.join(ARTIFACT_FOLDER, "data_transformation", "images")
RANDOM_STATE = 142
TRANSFORMED_ARTIFACT_DIR = os.path.join(ARTIFACT_FOLDER, "data_transformation")
TEST_AND_VAL_SPLIT = 0.3
TRAIN_FILE_NAME = "train.csv"
TEST_FILE_NAME = "test.csv"
VAL_FILE_NAME = "val.csv"

CHAT_MODEL_NAME = "llama-3.3-70b-versatile"
GEMINI_MODEL_NAME = "gemini-2.0-flash"
DB_FETCH_URL = "http://localhost:7860/api/retreive/"
PUBLIC_TEMP_DIR = "public"


IMAGE_ANALYSIS_MODEL_NAME = "Salesforce/blip-image-captioning-base"
INDEX_NAME = "multimodal-search"
NUM_WORKERS = 8
COOKIE_MAX_AGE_SECONDS=60*5

TEXT_IMAGE_ANALYSIS_PROMPT = """Describe this product image in detail for an e-commerce search system. Include: product type, dominant colors, brand (if visible), material or fabric, style, gender (men/women/unisex/boys/girls), category (apparel/footwear/accessories/etc.), subcategory, season suitability, usage (casual/formal/sports/ethnic), and any other visible attributes. Be specific and concise."""

TEXT_MODEL_NAME:str = "sentence-transformers/all-mpnet-base-v2"
MODEL_URI:str = "models:/E-Commerce-Recommendation_Model/1"
import torch
DEVICE:str = "cuda" if torch.cuda.is_available() else "cpu"
