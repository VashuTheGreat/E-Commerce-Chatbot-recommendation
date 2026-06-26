import os
import pandas as pd
import pytest
import torch
from src.components.model_trainer import Model_Trainer
from src.entity.config_entity import ModelTrainingConfig
from src.entity.artifact_entity import DataTransformationArtifact, ModelTrainingArtifact

@pytest.mark.asyncio
async def test_model_trainer_initiate_success(dummy_dataframe_transformed, temp_artifact_dir):
    """Test that Model_Trainer initializes, trains the model for 1 epoch using the
    transformed dummy dataset, and saves a checkpoint successfully.
    """
    # 1. Prepare file paths in the temporary artifact directory
    train_path = os.path.join(temp_artifact_dir, "train.csv")
    val_path = os.path.join(temp_artifact_dir, "val.csv")
    test_path = os.path.join(temp_artifact_dir, "test.csv")
    images_path = os.path.join(temp_artifact_dir, "images")
    
    # Save the transformed dataframe to the paths (used both for training and testing)
    dummy_dataframe_transformed.to_csv(train_path, index=False)
    dummy_dataframe_transformed.to_csv(val_path, index=False)
    dummy_dataframe_transformed.to_csv(test_path, index=False)
    
    # 2. Create the data transformation artifact
    data_transformation_artifact = DataTransformationArtifact(
        train_path=train_path,
        test_path=test_path,
        val_path=val_path,
        images_path=images_path
    )
    
    # 3. Configure custom model training paths in temp_artifact_dir
    model_dir = os.path.join(temp_artifact_dir, "checkpoints")
    cache_dir = os.path.join(temp_artifact_dir, "cache")
    os.makedirs(cache_dir, exist_ok=True)
    
    config = ModelTrainingConfig(
        epochs=1,
        patience=1,
        batch_size=2,
        model_name="test_model.pt",
        model_dir=model_dir,
        cache_dir=cache_dir
    )
    
    # 4. Pre-create the cached features to skip downloading heavy weights (ResNet, transformers)
    num_samples = len(dummy_dataframe_transformed)
    
    img_feats = torch.randn((num_samples, config.image_feature_output))
    txt_feats = torch.randn((num_samples, config.text_feature_output))
    labels = torch.tensor(dummy_dataframe_transformed['label'].values, dtype=torch.float32)
    
    torch.save(img_feats, os.path.join(cache_dir, "img_feats.pt"))
    torch.save(txt_feats, os.path.join(cache_dir, "txt_feats.pt"))
    torch.save(labels, os.path.join(cache_dir, "labels.pt"))
    
    # 5. Initialize and run the Model_Trainer
    trainer = Model_Trainer(
        data_transformation_artifact=data_transformation_artifact,
        model_training_config=config
    )
    
    artifact = await trainer.initiate()
    
    # 6. Verify training artifact status and output files
    assert isinstance(artifact, ModelTrainingArtifact)
    assert artifact.is_trained is True
    assert os.path.isfile(artifact.model_path)
    
    # Load the checkpoint and verify the contents
    checkpoint = torch.load(artifact.model_path, weights_only=False)
    assert "model_state_dict" in checkpoint
    assert "optimizer_state_dict" in checkpoint
    assert "best_val_loss" in checkpoint
    assert len(checkpoint["train_loss"]) == 1
    assert len(checkpoint["val_loss"]) == 1
