from src.entity.artifact_entity import DataTransformationArtifact, ModelTrainingArtifact, ModelEvaluationArtifact
from src.entity.config_entity import ModelEvaluationConfig, ModelTrainingConfig
from src.entity.model import MyModel
from src.utils.asyncHandler import asyncHandler
import pandas as pd
import os
import logging
import torch
import mlflow
import mlflow.pytorch
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
from torch.utils.data import DataLoader
from src.models.muti_model import MultimodalDataset
import yaml
from dataclasses import asdict
from datetime import datetime
from src.config.app_config import app_config

class Model_Evaluation:
    def __init__(self, model_evaluation_config: ModelEvaluationConfig, data_transformation_artifact: DataTransformationArtifact, model_training_artifact: ModelTrainingArtifact, model_training_config: ModelTrainingConfig):
        logging.info("Model_Evaluation - initializing")
        self.model_evaluation_config = model_evaluation_config
        self.data_transformation_artifact = data_transformation_artifact
        self.model_training_artifact = model_training_artifact
        self.model_training_config = model_training_config
        self.model_training_config.train_file_path = self.data_transformation_artifact.train_path
        logging.info(f"Model_Evaluation - loading model with train file path: {self.model_training_config.train_file_path}")
        self.model = MyModel(config=self.model_training_config)

    @asyncHandler
    async def initiate(self) -> ModelEvaluationArtifact:
        logging.info("Model_Evaluation.initiate - entered model evaluation step")
        try:
            import dagshub
            try:
                logging.info("Model_Evaluation.initiate - initializing DagsHub with app config key")
                dagshub.auth.add_app_token(app_config.mlflow_api_key)
                dagshub.init(repo_owner=app_config.dagshub_owner, repo_name=app_config.dagshub_repo, mlflow=True)
                logging.info("Model_Evaluation.initiate - DagsHub initialized successfully")
            except Exception as ex:
                logging.warning(f"Model_Evaluation.initiate - DagsHub initialization failed: {ex}")

            logging.info("Model_Evaluation.initiate - loading model weights")
            self.model.load_model()
            os.makedirs(self.model_evaluation_config.evaluation_artifact_dir, exist_ok=True)
            loss_plot_path = os.path.join(self.model_evaluation_config.evaluation_artifact_dir, self.model_evaluation_config.loss_plot_file_name)
            confusion_matrix_path = os.path.join(self.model_evaluation_config.evaluation_artifact_dir, self.model_evaluation_config.confusion_matrix_file_name)
            metrics_file_path = os.path.join(self.model_evaluation_config.evaluation_artifact_dir, self.model_evaluation_config.metrics_file_name)
            logging.info(f"Model_Evaluation.initiate - loss plot destination: {loss_plot_path}")
            logging.info(f"Model_Evaluation.initiate - confusion matrix destination: {confusion_matrix_path}")
            logging.info(f"Model_Evaluation.initiate - metrics file destination: {metrics_file_path}")

            if len(self.model.train_loss) > 0:
                logging.info(f"Model_Evaluation.initiate - plotting training loss for {len(self.model.train_loss)} epochs")
                plt.figure(figsize=(10, 6))
                plt.plot(self.model.train_loss, label='Train Loss')
                if len(self.model.val_loss) > 0:
                    plt.plot(self.model.val_loss, label='Validation Loss')
                plt.xlabel('Epoch')
                plt.ylabel('Loss')
                plt.title('Training and Validation Loss Over Epochs')
                plt.legend()
                plt.savefig(loss_plot_path)
                plt.close()
                logging.info("Model_Evaluation.initiate - training loss plot saved successfully")

            logging.info(f"Model_Evaluation.initiate - reading test dataset from path: {self.data_transformation_artifact.test_path}")
            test_df = pd.read_csv(self.data_transformation_artifact.test_path)
            test_dataset = MultimodalDataset(data_frame=test_df, config=self.model_training_config)
            test_loader = DataLoader(
                test_dataset,
                batch_size=self.model_training_config.batch_size,
                shuffle=False
            )

            self.model.model.eval()
            all_preds = []
            all_labels = []
            logging.info("Model_Evaluation.initiate - starting test inference loop")
            with torch.no_grad():
                for img_feats, text_feats, labels in test_loader:
                    img_feats = img_feats.to(self.model.device)
                    text_feats = text_feats.to(self.model.device)
                    logits = self.model.model(img_feats, text_feats)
                    probs = torch.sigmoid(logits)
                    preds = (probs > 0.5).int().cpu().numpy().flatten()
                    all_preds.extend(preds)
                    all_labels.extend(labels.cpu().numpy().flatten())

            logging.info("Model_Evaluation.initiate - test inference loop finished. calculating metrics.")
            accuracy = accuracy_score(all_labels, all_preds)
            precision = precision_score(all_labels, all_preds, zero_division=0)
            recall = recall_score(all_labels, all_preds, zero_division=0)
            f1 = f1_score(all_labels, all_preds, zero_division=0)
            cm = confusion_matrix(all_labels, all_preds)
            logging.info(f"Model_Evaluation.initiate - test accuracy: {accuracy:.4f}, precision: {precision:.4f}, recall: {recall:.4f}, f1: {f1:.4f}")

            plt.figure(figsize=(6, 5))
            sns.heatmap(
                cm,
                annot=True,
                fmt='d',
                cmap='Blues',
                xticklabels=['Predicted 0', 'Predicted 1'],
                yticklabels=['Actual 0', 'Actual 1']
            )
            plt.title('Confusion Matrix - Test Data')
            plt.ylabel('Actual Labels')
            plt.xlabel('Predicted Labels')
            plt.savefig(confusion_matrix_path, bbox_inches='tight')
            plt.close()
            logging.info("Model_Evaluation.initiate - confusion matrix plot saved")

            avg_train_loss = self.model.train_loss[-1] if len(self.model.train_loss) > 0 else 0.0
            avg_val_loss = self.model.val_loss[-1] if len(self.model.val_loss) > 0 else 0.0
            metrics_data = {
                "train_loss": float(avg_train_loss),
                "val_loss": float(avg_val_loss),
                "test_accuracy": float(accuracy),
                "test_precision": float(precision),
                "test_recall": float(recall),
                "test_f1_score": float(f1)
            }
            with open(metrics_file_path, "w") as f:
                yaml.dump(metrics_data, f)
            logging.info("Model_Evaluation.initiate - metrics file written successfully")

            experiment_name = f"{self.model_evaluation_config.mlflow_experiment_name}-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
            logging.info(f"Model_Evaluation.initiate - starting MLflow run inside experiment: {experiment_name}")
            mlflow.set_experiment(experiment_name)
            with mlflow.start_run(run_name=self.model_evaluation_config.mlflow_run_name):
                mlflow.log_params(asdict(self.model_training_config))
                mlflow.log_metric("train_loss", avg_train_loss)
                if len(self.model.val_loss) > 0:
                    mlflow.log_metric("val_loss", avg_val_loss)
                mlflow.log_metric("test_accuracy", accuracy)
                mlflow.log_metric("test_precision", precision)
                mlflow.log_metric("test_recall", recall)
                mlflow.log_metric("test_f1_score", f1)
                
                if os.path.exists(loss_plot_path):
                    mlflow.log_artifact(loss_plot_path)
                if os.path.exists(confusion_matrix_path):
                    mlflow.log_artifact(confusion_matrix_path)
                mlflow.log_artifact(metrics_file_path)

                try:
                    logging.info("Model_Evaluation.initiate - registering model into MLflow registry")
                    mlflow.pytorch.log_model(
                        pytorch_model=self.model.model,
                        name="multimodal_model_registry",
                        serialization_format="pickle"
                    )
                    logging.info("Model_Evaluation.initiate - model registered successfully")
                except Exception as register_ex:
                    logging.warning(f"Model_Evaluation.initiate - Model logging failed: {register_ex}")

            logging.info("Model_Evaluation.initiate - exiting model evaluation step successfully")
            return ModelEvaluationArtifact(
                evaluation_dir=self.model_evaluation_config.evaluation_artifact_dir,
                metrics_file_path=metrics_file_path,
                loss_plot_path=loss_plot_path,
                confusion_matrix_path=confusion_matrix_path,
                is_evaluated=True
            )
        except Exception as e:
            logging.error(f"Model_Evaluation.initiate - model evaluation failed: {e}", exc_info=True)
            return ModelEvaluationArtifact(
                evaluation_dir="",
                metrics_file_path="",
                loss_plot_path="",
                confusion_matrix_path="",
                is_evaluated=False
            )