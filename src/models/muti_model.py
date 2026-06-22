import torchvision.models as models
import torch
import torch.nn as nn
from torch.utils.data import Dataset
from torchvision.transforms import v2
from transformers import AutoTokenizer, AutoModel
import cv2
from dataclasses import dataclass
import random
import os
from tqdm.auto import tqdm
from src.entity.config_entity import Config

class ImageEncoder(nn.Module):
    def __init__(self, config):
        super().__init__()
        self.config = config
        resnet = models.resnet50(weights=models.ResNet50_Weights.DEFAULT)
        self.image_encoder = nn.Sequential(*list(resnet.children())[:-1])

        for param in self.image_encoder.parameters():
            param.requires_grad = False

    def forward(self, x):
        with torch.no_grad():
            x = self.image_encoder(x)
            x = torch.flatten(x, 1)
        return x

class TextEncoder(nn.Module):
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.text_model = AutoModel.from_pretrained("sentence-transformers/all-mpnet-base-v2")

        for param in self.text_model.parameters():
            param.requires_grad = False

    def forward(self, input_ids, attention_mask):
        with torch.no_grad():
            outputs = self.text_model(input_ids=input_ids, attention_mask=attention_mask)
            text_vector = outputs.last_hidden_state[:, 0, :]
        return text_vector

class MLPModel(nn.Module):
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.model = nn.Sequential(
            nn.Linear(self.config.image_feature_output + self.config.text_feature_output, self.config.image_feature_output // 2),
            nn.ReLU(),
            nn.Dropout(self.config.dropout),
            nn.Linear(self.config.image_feature_output // 2, self.config.final_feature_output),
            nn.ReLU()
        )
        self.classifier = nn.Linear(self.config.final_feature_output, 1)

    def forward(self, x, return_embedding=False):
        embedding = self.model(x)
        if return_embedding:
            return nn.functional.normalize(embedding, p=2, dim=1)
        return self.classifier(embedding)

class Multimodal(nn.Module):
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.mlp = MLPModel(config=config)

    def forward(self, img_feats, text_feats, return_embedding=False):
        combined = torch.cat((img_feats, text_feats), dim=1)
        return self.mlp(combined, return_embedding=return_embedding)


class MultimodalDataset(Dataset):
    def __init__(self, data_frame, config=Config(), indices=None, device=None):
        super().__init__()
        self.data_frame = data_frame.reset_index(drop=True)
        self.config = config
        self.indices = indices if indices is not None else list(range(len(self.data_frame)))

        # Explicit device allocation (Default to CUDA if active)
        self.device = device if device is not None else torch.device("cuda" if torch.cuda.is_available() else "cpu")

        self.img_cache_path = os.path.join(self.config.cache_dir, "img_feats.pt")
        self.txt_cache_path = os.path.join(self.config.cache_dir, "txt_feats.pt")
        self.lbl_cache_path = os.path.join(self.config.cache_dir, "labels.pt")

        # Build cache globally once if it doesn't exist
        if not (os.path.exists(self.img_cache_path) and os.path.exists(self.txt_cache_path) and os.path.exists(self.lbl_cache_path)):
            self._build_global_cache()

        # CUDA FIX: map_location ko self.device kar diya taaki tensors direct GPU RAM par load hon
        print(f"Loading cached tensors directly onto {self.device}...")
        self.img_features = torch.load(self.img_cache_path, map_location=self.device)
        self.text_features = torch.load(self.txt_cache_path, map_location=self.device)
        self.labels = torch.load(self.lbl_cache_path, map_location=self.device)

    def _build_global_cache(self):
        os.makedirs(self.config.cache_dir, exist_ok=True)

        tokenizer = AutoTokenizer.from_pretrained("sentence-transformers/all-mpnet-base-v2")
        image_encoder = ImageEncoder(self.config).to(self.device).eval()
        text_encoder = TextEncoder(self.config).to(self.device).eval()

        transforms = v2.Compose([
            v2.ToImage(),
            v2.ToDtype(torch.float32, scale=True),
            v2.Resize(size=(224, 224), antialias=True),
            v2.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])

        num_samples = len(self.data_frame)
        all_img_feats = torch.zeros((num_samples, self.config.image_feature_output), dtype=torch.float32)
        all_txt_feats = torch.zeros((num_samples, self.config.text_feature_output), dtype=torch.float32)
        all_labels = torch.tensor(self.data_frame['label'].values, dtype=torch.float32)

        print(f"--- Cache matrix not found. Building block arrays for {num_samples} samples on {self.device} ---")
        for i in tqdm(range(num_samples), desc="Caching Features"):
            img_path = self.data_frame.loc[i, 'image_path']
            text = str(self.data_frame.loc[i, 'product_search_description'])

            try:
                img = cv2.imread(img_path)
                img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                img_tensor = transforms(img).unsqueeze(0).to(self.device)
                img_feat = image_encoder(img_tensor).cpu()
            except Exception:
                img_feat = torch.zeros((1, self.config.image_feature_output), dtype=torch.float32)

            tokens = tokenizer(
                text,
                padding='max_length',
                max_length=self.config.max_len,
                truncation=True,
                return_tensors="pt"
            ).to(self.device)

            txt_feat = text_encoder(tokens['input_ids'], tokens['attention_mask']).cpu()

            all_img_feats[i] = img_feat.squeeze(0)
            all_txt_feats[i] = txt_feat.squeeze(0)

        torch.save(all_img_feats, self.img_cache_path)
        torch.save(all_txt_feats, self.txt_cache_path)
        torch.save(all_labels, self.lbl_cache_path)
        print("--- Global embedding matrix cached successfully! ---")

    def __len__(self):
        return len(self.indices)

    def __getitem__(self, index):
        actual_idx = self.indices[index]

        img_tensor = self.img_features[actual_idx].clone()
        txt_tensor = self.text_features[actual_idx].clone()
        label = self.labels[actual_idx]

        if label == 1.0:
            dropout_rand = random.random()
            if dropout_rand < 0.15:
                # Modality dropout zeroes are allocated on the exact same tensor device configuration
                img_tensor = torch.zeros(self.config.image_feature_output, dtype=torch.float32, device=self.device)
            elif dropout_rand < 0.30:
                txt_tensor = torch.zeros(self.config.text_feature_output, dtype=torch.float32, device=self.device)

        return img_tensor, txt_tensor, label