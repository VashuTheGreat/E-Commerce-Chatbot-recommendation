from tqdm.auto import tqdm
import torch
import os
from src.models.muti_model import Multimodal

import pandas as pd

class MyModel:
    def __init__(self, config):
        self.config = config
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        self.model = Multimodal(config=config).to(self.device)
        self.optimizer = torch.optim.Adam(params=self.model.parameters(), lr=self.config.learning_rate)

        pos_weight_tensor = None
        if config.train_file_path and os.path.exists(config.train_file_path):
            train_df = pd.read_csv(config.train_file_path)
            pos_weight_val = train_df[train_df['label'] == 0].shape[0] / (train_df[train_df['label'] == 1].shape[0] + 1e-5)
            pos_weight_tensor = torch.tensor([pos_weight_val], dtype=torch.float32).to(self.device)
        self.loss_fn = torch.nn.BCEWithLogitsLoss(pos_weight=pos_weight_tensor)

        self.train_loss = []
        self.val_loss = []
        self.best_val_loss = float('inf')
        self.patience_counter = 0

    def train(self, train_data_loader, val_data_loader):
        self.load_model()
        for epoch in range(self.config.epochs):
            self.model.train()
            train_loss = 0.0

            train_pbar = tqdm(train_data_loader, desc=f"Epoch {epoch+1}/{self.config.epochs} [Train]", leave=False)
            for img_feats, text_feats, labels in train_pbar:
                img_feats = img_feats.to(self.device)
                text_feats = text_feats.to(self.device)
                labels = labels.to(self.device).unsqueeze(1)

                self.optimizer.zero_grad()
                outputs = self.model(img_feats, text_feats)
                loss = self.loss_fn(outputs, labels)

                loss.backward()
                self.optimizer.step()

                train_loss += loss.item()
                train_pbar.set_postfix({"batch_loss": f"{loss.item():.4f}"})

            avg_train_loss = train_loss / len(train_data_loader)
            avg_val_loss = self.validate(val_data_loader)

            self.train_loss.append(avg_train_loss)
            self.val_loss.append(avg_val_loss)

            print(f"Epoch [{epoch+1}/{self.config.epochs}] -> Train Loss: {avg_train_loss:.4f} | Val Loss: {avg_val_loss:.4f}")

            if avg_val_loss < self.best_val_loss:
                self.best_val_loss = avg_val_loss
                self.patience_counter = 0
                self.save_model()
            else:
                self.patience_counter += 1
                if self.patience_counter >= self.config.patience:
                    print(f"Early stopping triggered at epoch {epoch+1}")
                    break

    def validate(self, val_data_loader):
        self.model.eval()
        val_loss = 0.0

        val_pbar = tqdm(val_data_loader, desc="Validating", leave=False)
        with torch.no_grad():
            for img_feats, text_feats, labels in val_pbar:
                img_feats = img_feats.to(self.device)
                text_feats = text_feats.to(self.device)
                labels = labels.to(self.device).unsqueeze(1)

                outputs = self.model(img_feats, text_feats)
                loss = self.loss_fn(outputs, labels)

                val_loss += loss.item()
                val_pbar.set_postfix({"val_batch_loss": f"{loss.item():.4f}"})

        return val_loss / len(val_data_loader)

    def predict(self, img_feats, text_feats):
        self.model.eval()
        with torch.no_grad():
            img_feats = img_feats.to(self.device)
            text_feats = text_feats.to(self.device)

            logits = self.model(img_feats, text_feats)
            probs = torch.sigmoid(logits)
        return probs

        
    def predict_emb(self, img_feats, text_feats):
        self.model.eval()

        with torch.no_grad():
            img_feats = img_feats.to(self.device)
            text_feats = text_feats.to(self.device)

            embedding = self.model(
                img_feats,
                text_feats,
                return_embedding=True
            )

        return embedding    

    def save_model(self):
        os.makedirs(self.config.model_dir, exist_ok=True)
        checkpoint_path = os.path.join(self.config.model_dir, self.config.model_name)
        torch.save({
            'model_state_dict': self.model.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict(),
            'best_val_loss': self.best_val_loss,
            'train_loss': self.train_loss,
            'val_loss': self.val_loss
        }, checkpoint_path)

    def load_model(self):
        checkpoint_path = os.path.join(self.config.model_dir, self.config.model_name)
        if os.path.exists(checkpoint_path):
            checkpoint = torch.load(checkpoint_path, map_location=self.device)
            self.model.load_state_dict(checkpoint['model_state_dict'])
            self.optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
            self.best_val_loss = checkpoint.get('best_val_loss', float('inf'))
            self.train_loss = checkpoint.get('train_loss', [])
            self.val_loss = checkpoint.get('val_loss', [])