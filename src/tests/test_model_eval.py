import os
import pandas as pd
import pytest
import torch
from unittest.mock import MagicMock, patch
from src.components.model_evaluation import Model_Evaluation
from src.entity.config_entity import ModelEvaluationConfig, ModelTrainingConfig
from src.entity.artifact_entity import DataTransformationArtifact, ModelTrainingArtifact, ModelEvaluationArtifact

@pytest.mark.asyncio
async def test_model_evaluation_initiate_success(dummy_dataframe_transformed, temp_artifact_dir):
    """Test that Model_Evaluation successfully runs evaluation on test data,
    saves metrics, plots, and logs to MLflow (mocked) without hitting remote servers.
    """
    # 1. Prepare file paths in the temporary artifact directory
    train_path = os.path.join(temp_artifact_dir, "train.csv")
    val_path = os.path.join(temp_artifact_dir, "val.csv")
    test_path = os.path.join(temp_artifact_dir, "test.csv")
    images_path = os.path.join(temp_artifact_dir, "images")
    
    # Save the transformed dataframe to test_path
    dummy_dataframe_transformed.to_csv(test_path, index=False)
    
    # 2. Create mock artifacts
    data_transformation_artifact = DataTransformationArtifact(
        train_path=train_path,
        test_path=test_path,
        val_path=val_path,
        images_path=images_path
    )
    
    model_training_artifact = ModelTrainingArtifact(
        model_path=os.path.join(temp_artifact_dir, "checkpoints", "test_model.pt"),
        is_trained=True,
        message="Model trained"
    )
    
    # 3. Setup configurations
    eval_dir = os.path.join(temp_artifact_dir, "model_evaluation")
    model_evaluation_config = ModelEvaluationConfig(
        evaluation_artifact_dir=eval_dir,
        metrics_file_name="metrics.yaml",
        loss_plot_file_name="loss_plot.png",
        confusion_matrix_file_name="confusion_matrix.png",
        mlflow_experiment_name="test-experiment",
        mlflow_run_name="test-run"
    )
    
    cache_dir = os.path.join(temp_artifact_dir, "cache")
    os.makedirs(cache_dir, exist_ok=True)
    
    model_training_config = ModelTrainingConfig(
        epochs=1,
        patience=1,
        batch_size=2,
        model_name="test_model.pt",
        model_dir=os.path.join(temp_artifact_dir, "checkpoints"),
        cache_dir=cache_dir
    )
    
    # 4. Pre-create the cached features to skip actual image/text encoders
    num_samples = len(dummy_dataframe_transformed)
    img_feats = torch.randn((num_samples, model_training_config.image_feature_output))
    txt_feats = torch.randn((num_samples, model_training_config.text_feature_output))
    labels = torch.tensor(dummy_dataframe_transformed['label'].values, dtype=torch.float32)
    
    torch.save(img_feats, os.path.join(cache_dir, "img_feats.pt"))
    torch.save(txt_feats, os.path.join(cache_dir, "txt_feats.pt"))
    torch.save(labels, os.path.join(cache_dir, "labels.pt"))
    
    # 5. Patch dagshub and mlflow to prevent any remote API requests/hosting
    with patch("dagshub.auth.add_app_token") as mock_add_token, \
         patch("dagshub.init") as mock_dag_init, \
         patch("src.components.model_evaluation.mlflow") as mock_mlflow:
        
        # Setup mlflow mock context manager for start_run
        mock_run = MagicMock()
        mock_mlflow.start_run.return_value = mock_run
        
        # Patch load_model to bypass reading checkpoint from disk
        with patch("src.entity.model.MyModel.load_model") as mock_load_model:
            evaluator = Model_Evaluation(
                model_evaluation_config=model_evaluation_config,
                data_transformation_artifact=data_transformation_artifact,
                model_training_artifact=model_training_artifact,
                model_training_config=model_training_config
            )
            
            # Set dummy losses on the model to test loss plotting and log extraction
            evaluator.model.train_loss = [0.5, 0.4]
            evaluator.model.val_loss = [0.6, 0.45]
            
            # 6. Run evaluation
            artifact = await evaluator.initiate()
            
            # 7. Assertions on output artifact and generated files
            assert isinstance(artifact, ModelEvaluationArtifact)
            assert artifact.is_evaluated is True
            assert os.path.isfile(artifact.metrics_file_path)
            assert os.path.isfile(artifact.loss_plot_path)
            assert os.path.isfile(artifact.confusion_matrix_path)
            
            # Verify MLflow interaction was triggered locally via mock
            mock_mlflow.set_experiment.assert_called_once()
            mock_mlflow.start_run.assert_called_once_with(run_name=model_evaluation_config.mlflow_run_name)
            mock_mlflow.log_params.assert_called_once()
            
            # Verify yaml metrics structure
            with open(artifact.metrics_file_path, "r") as f:
                import yaml
                metrics = yaml.safe_load(f)
                for key in ["train_loss", "val_loss", "test_accuracy", "test_precision", "test_recall", "test_f1_score"]:
                    assert key in metrics
