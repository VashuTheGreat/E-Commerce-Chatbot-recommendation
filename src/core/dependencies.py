from functools import lru_cache
from src.entity.model import MyModel
from src.entity.data_access import Connect_data
from src.entity.config_entity import ModelTrainingConfig
from src.components.vectorizing_data import Vectorizer
from torchvision.transforms import v2
from src.constants import DEVICE
from src.models.muti_model import ImageEncoder,TextEncoder
import torch
from src.constants import TEXT_MODEL_NAME
from src.config.app_config import app_config
from transformers import AutoTokenizer


# Model training Pipeline
@lru_cache
def my_model():
    return MyModel(ModelTrainingConfig())


@lru_cache
def connect_data():
    return Connect_data()

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
    