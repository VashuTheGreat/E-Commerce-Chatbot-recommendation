import os
import logging
import functools
import torch
import requests
from io import BytesIO
from PIL import Image
from transformers import AutoTokenizer

from src.models.orchastrator_state import State
from src.entity.config_entity import ModelTrainingConfig
from src.utils.asyncHandler import asyncHandler
from src.retreiver.custom_vec_db import CustomVectorDb
from src.models.muti_model import ImageEncoder, TextEncoder, MLPModel

logger = logging.getLogger(__name__)

@functools.lru_cache(maxsize=1)
def _get_search_components():
    config = ModelTrainingConfig()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    image_encoder = ImageEncoder(config).to(device).eval()
    text_encoder = TextEncoder(config).to(device).eval()
    mlp_model = MLPModel(config).to(device).eval()

    checkpoint_path = os.environ.get("MODEL_CHECKPOINT_PATH", "")
    if not checkpoint_path or not os.path.exists(checkpoint_path):
        artifact_dir = os.path.join(os.environ.get("ARTIFACT_FOLDER", "artifacts"), "model_training", "checkpoints")
        default_path = os.path.join(artifact_dir, config.model_name)
        if os.path.exists(default_path):
            checkpoint_path = default_path

    if checkpoint_path and os.path.exists(checkpoint_path):
        try:
            checkpoint = torch.load(checkpoint_path, map_location=device, weights_only=True)
            if "model_state_dict" in checkpoint:
                state_dict = {}
                for k, v in checkpoint["model_state_dict"].items():
                    if k.startswith("mlp."):
                        state_dict[k[4:]] = v
                mlp_model.load_state_dict(state_dict, strict=False)
            else:
                mlp_model.load_state_dict(checkpoint, strict=False)
        except Exception:
            pass

    return image_encoder, text_encoder, mlp_model, device, config.max_len

@asyncHandler
async def retriever_node(state: State):
    search_query = state.get("search_query", "")
    image_paths = state.get("analyse_content_paths", [])
    has_image = bool(image_paths) and image_paths != ["000"] and "000" not in image_paths

    db_results = []

    try:
        image_encoder, text_encoder, mlp_model, device, max_len = _get_search_components()
        tokenizer = AutoTokenizer.from_pretrained("sentence-transformers/all-mpnet-base-v2")

        with torch.no_grad():
            tokens = tokenizer(
                search_query,
                padding="max_length",
                max_length=max_len,
                truncation=True,
                return_tensors="pt"
            )
            text_feats = text_encoder(
                tokens["input_ids"].to(device),
                tokens["attention_mask"].to(device)
            )

            if has_image and image_paths:
                img_raw = image_paths[0]
                if img_raw.startswith("http"):
                    resp = requests.get(img_raw, timeout=10)
                    resp.raise_for_status()
                    img = Image.open(BytesIO(resp.content)).convert("RGB")
                else:
                    img = Image.open(img_raw).convert("RGB")

                from torchvision import transforms
                trans = transforms.Compose([
                    transforms.ToTensor(),
                    transforms.Resize((224, 224)),
                    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
                ])
                img_tensor = trans(img).unsqueeze(0).to(device)
                img_feats = image_encoder(img_tensor)
            else:
                config = ModelTrainingConfig()
                img_feats = torch.zeros(1, config.image_feature_output, device=device)

            combined = torch.cat((img_feats, text_feats), dim=1)
            embedding = mlp_model(combined, return_embedding=True)

        vec_db = CustomVectorDb(
            api_key=os.environ.get("PINECONE_API_KEY", ""),
            index_name="multimodal-search",
            dimension=ModelTrainingConfig().final_feature_output
        )

        results = vec_db.search(vector=embedding[0].cpu().tolist(), top_k=5)
        db_results = results.get("matches", [])

    except Exception:
        db_results = []

    return {
        "db_results": db_results,
        "messages": state.get("messages", [])
    }
