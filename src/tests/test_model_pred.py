import torch
import pytest
from src.entity.model import MyModel
from src.entity.config_entity import ModelTrainingConfig

def test_mymodel_predict_success():
    """Test that MyModel.predict returns probability values in [0, 1]
    with the correct shape matching the batch size.
    """
    config = ModelTrainingConfig(
        image_feature_output=2048,
        text_feature_output=768,
        final_feature_output=512,
        train_file_path=None  # Ensure we bypass any local dataset file reading during init
    )
    
    model = MyModel(config=config)
    
    batch_size = 4
    dummy_img_feats = torch.randn((batch_size, config.image_feature_output))
    dummy_txt_feats = torch.randn((batch_size, config.text_feature_output))
    
    # Run predict
    probs = model.predict(dummy_img_feats, dummy_txt_feats)
    
    # Assertions
    assert probs.shape == (batch_size, 1)
    assert torch.all(probs >= 0.0) and torch.all(probs <= 1.0)


def test_mymodel_predict_emb_success():
    """Test that MyModel.predict_emb returns L2-normalized embedding tensors
    with the correct final feature output shape.
    """
    config = ModelTrainingConfig(
        image_feature_output=2048,
        text_feature_output=768,
        final_feature_output=512,
        train_file_path=None
    )
    
    model = MyModel(config=config)
    
    batch_size = 3
    dummy_img_feats = torch.randn((batch_size, config.image_feature_output))
    dummy_txt_feats = torch.randn((batch_size, config.text_feature_output))
    
    # Run predict_emb
    embeddings = model.predict_emb(dummy_img_feats, dummy_txt_feats)
    
    # Assertions
    assert embeddings.shape == (batch_size, config.final_feature_output)
    
    # Verify embeddings are L2 normalized (magnitude equals 1.0)
    magnitudes = torch.norm(embeddings, p=2, dim=1)
    assert torch.allclose(magnitudes, torch.ones_like(magnitudes), atol=1e-5)
