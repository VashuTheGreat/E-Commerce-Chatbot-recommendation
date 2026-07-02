from functools import lru_cache
from src.entity.model import MyModel
from src.entity.data_access import Connect_data
from src.entity.config_entity import ModelTrainingConfig
from src.components.vectorizing_data import Vectorizer
from torchvision.transforms import v2
from src.constants import DEVICE, DATA_PATH
from src.models.muti_model import ImageEncoder,TextEncoder
import torch
from src.constants import TEXT_MODEL_NAME
from src.config.app_config import app_config
from transformers import AutoTokenizer, BlipProcessor, BlipForConditionalGeneration
from src.constants import IMAGE_ANALYSIS_MODEL_NAME
import logging
import pandas as pd


# Model training Pipeline
@lru_cache
def my_model():
    return MyModel(ModelTrainingConfig())


@lru_cache
def vectorizer():
    return Vectorizer()



@lru_cache
def get_img_transformer():
    return v2.Compose([
        v2.ToImage(),
        v2.ToDtype(torch.float32, scale=True),
        v2.Resize(size=(224, 224), antialias=True),
        v2.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])

@lru_cache
def image_encoder_eval():
    return ImageEncoder(ModelTrainingConfig()).to(DEVICE).eval()


@lru_cache
def text_encoder_eval():
    return TextEncoder(ModelTrainingConfig()).to(DEVICE).eval()



@lru_cache
def text_tokenizer():
    return AutoTokenizer.from_pretrained(TEXT_MODEL_NAME, token=app_config.huggingface_api_key)


@lru_cache
def connect_data():
    return Connect_data(data_path=DATA_PATH)

@lru_cache
def df_schema() -> dict:
    logging.info("df_schema - cache miss. loading csv from %s", DATA_PATH)
    df = pd.read_csv(DATA_PATH)
    df = df[:10]
    return {
        "columns": df.columns.tolist(),
        "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()},
        "shape": tuple(df.shape),
        "sample": df.head(1).to_dict(orient="records"),
    }
    



@lru_cache
def blip_processor() -> BlipProcessor:
    logging.info(f"[BLIP] Loading processor '{IMAGE_ANALYSIS_MODEL_NAME}'…")
    return BlipProcessor.from_pretrained(IMAGE_ANALYSIS_MODEL_NAME)


@lru_cache
def blip_model() -> BlipForConditionalGeneration:
    logging.info(f"[BLIP] Loading model '{IMAGE_ANALYSIS_MODEL_NAME}'…")
    return BlipForConditionalGeneration.from_pretrained(
        IMAGE_ANALYSIS_MODEL_NAME,
        low_cpu_mem_usage=True,
    )


# loading all the heavy files before the system starts
_ = my_model()
_ = vectorizer()
_ = get_img_transformer()
_ = image_encoder_eval()
_ = text_encoder_eval()
_ = text_tokenizer()
_ = connect_data()
_ = df_schema()
_ = blip_processor()
_ = blip_model()
