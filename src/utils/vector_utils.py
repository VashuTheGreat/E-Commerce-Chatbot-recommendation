
import logging
import cv2
from src.core.dependencies import get_img_transformer, image_encoder_eval, text_encoder_eval, text_tokenizer
import torch
import os
def _get_image_feat(image_path, config, device):
    logging.info(f"entering _get_image_feat with image_path: {image_path}, device: {device}")
    if not image_path or not os.path.exists(image_path):
        logging.warning(f"image path not provided or does not exist: {image_path}. returning zero features.")
        feat = torch.zeros((1, config.image_feature_output), device=device)
        logging.info(f"exiting _get_image_feat with zero features tensor shape: {feat.shape}")
        return feat
    img = cv2.imread(image_path)
    if img is None:
        logging.warning(f"failed to read image at path: {image_path}. returning zero features.")
        feat = torch.zeros((1, config.image_feature_output), device=device)
        logging.info(f"exiting _get_image_feat with zero features tensor shape: {feat.shape}")
        return feat
    logging.info(f"successfully loaded image from path: {image_path}. image shape: {img.shape}")
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    
    transforms = get_img_transformer()
    img_tensor = transforms(img).unsqueeze(0).to(device)
    logging.info(f"transformed image into tensor. shape: {img_tensor.shape}, device: {img_tensor.device}")
    image_encoder = image_encoder_eval()
    logging.info("running image encoder forward pass")
    with torch.no_grad():
        img_feat = image_encoder(img_tensor)
    logging.info(f"exiting _get_image_feat with shape: {img_feat.shape}")
    return img_feat

def _get_text_feat(text, config, device):
    logging.info(f"entering _get_text_feat with text: {text}, device: {device}")
    
    text_encoder = text_encoder_eval()
    tokenizer = text_tokenizer()
    tokens = tokenizer(
        text,
        padding="max_length",
        max_length=config.max_len,
        truncation=True,
        return_tensors="pt"
    ).to(device)
    logging.info(f"tokenized text. tokens shape: {tokens['input_ids'].shape}")
    with torch.no_grad():
        txt_feat = text_encoder(tokens["input_ids"], tokens["attention_mask"])
    logging.info(f"exiting _get_text_feat with shape: {txt_feat.shape}")
    return txt_feat
