from dotenv import load_dotenv
load_dotenv()

import sys
import os
import asyncio
import pytest
import pandas as pd
from unittest.mock import MagicMock, patch, AsyncMock

sys.modules['pinecone'] = MagicMock()
sys.modules['pinecone'].ServerlessSpec = MagicMock()

sys.path.append(os.getcwd())
src_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
sys.path.append(src_dir)

from src.components.vectorizing_data import InferenceDataSet, Vectorizer


@pytest.fixture
def sample_csv(tmp_path):
    csv_path = tmp_path / "sample.csv"
    data = {
        "id": [1, 2, 3],
        "image_url": ["http://example.com/img1.jpg", "http://example.com/img2.jpg", "http://example.com/img3.jpg"],
        "product_search_description": ["desc1", "desc2", "desc3"],
        "label": [0, 1, 0]
    }
    df = pd.DataFrame(data)
    df.to_csv(csv_path, index=False)
    return str(csv_path)


@pytest.fixture
def mock_config():
    config = MagicMock()
    config.image_processor = MagicMock(return_value="processed_image")
    config.tokenizer = MagicMock(return_value="tokenized_text")
    return config


class TestInferenceDataSet:
    @patch("src.components.vectorizing_data.pd.read_csv")
    @patch("src.components.vectorizing_data.requests.get")
    def test_init(self, mock_get, mock_read_csv, sample_csv, mock_config):
        mock_df = pd.DataFrame({
            "id": [1, 2],
            "image_url": ["http://example.com/img1.jpg", "http://example.com/img2.jpg"],
            "product_search_description": ["desc1", "desc2"],
            "label": [0, 1]
        })
        mock_read_csv.return_value = mock_df
        dataset = InferenceDataSet(data_path=sample_csv, config=mock_config)
        assert len(dataset) == 2

    @patch("src.components.vectorizing_data.pd.read_csv")
    @patch("src.components.vectorizing_data.requests.get")
    def test_getitem(self, mock_get, mock_read_csv, sample_csv, mock_config):
        mock_df = pd.DataFrame({
            "id": [1],
            "image_url": ["http://example.com/img1.jpg"],
            "product_search_description": ["desc1"],
            "label": [0]
        })
        mock_read_csv.return_value = mock_df

        mock_response = MagicMock()
        mock_response.content = b"fake_image_data"
        mock_get.return_value = mock_response

        dataset = InferenceDataSet(data_path=sample_csv, config=mock_config)
        with patch("PIL.Image.open") as mock_open_image:
            mock_open_image.return_value.convert.return_value = MagicMock()
            result = dataset[0]

        assert len(result) == 4
        assert result[2] == 0
        assert result[3] == 1

    @patch("src.components.vectorizing_data.pd.read_csv")
    @patch("src.components.vectorizing_data.requests.get")
    def test_getitem_retry_on_fail(self, mock_get, mock_read_csv, sample_csv, mock_config):
        mock_df = pd.DataFrame({
            "id": [1],
            "image_url": ["http://example.com/img1.jpg"],
            "product_search_description": ["desc1"],
            "label": [0]
        })
        mock_read_csv.return_value = mock_df

        mock_get.side_effect = [Exception("fail"), MagicMock(content=b"retry_image")]

        dataset = InferenceDataSet(data_path=sample_csv, config=mock_config)
        with patch("PIL.Image.open") as mock_open_image:
            mock_open_image.return_value.convert.return_value = MagicMock()
            result = dataset[0]

        assert len(result) == 4
        assert result[2] == 0


class TestVectorizer:
    @patch("src.components.vectorizing_data.download_artifacts")
    @patch("src.components.vectorizing_data.MyModel")
    @patch("src.components.vectorizing_data.CustomVectorDb")
    def test_vectorizer_init(self, mock_vec_db, mock_model, mock_download, sample_csv):
        mock_download.return_value = "/mock/path"
        vectorizer = Vectorizer(data_path=sample_csv)
        assert vectorizer.data_path == sample_csv
        assert vectorizer.model is not None

    @patch("src.components.vectorizing_data.download_artifacts")
    @patch("src.components.vectorizing_data.MyModel")
    @patch("src.components.vectorizing_data.CustomVectorDb")
    @patch("src.components.vectorizing_data.pd.read_csv")
    def test_ingest_vec(self, mock_read_csv, mock_vec_db, mock_model, mock_download, sample_csv):
        mock_download.return_value = "/mock/path"
        mock_read_csv.return_value = pd.DataFrame({
            "id": [1, 2],
            "label": [0, 1]
        })
        vectorizer = Vectorizer(data_path=sample_csv)
        mock_vec_db.get_all_ids.return_value = []
        asyncio.run(vectorizer.ingest_vec())

    @patch("src.components.vectorizing_data.download_artifacts")
    @patch("src.components.vectorizing_data.MyModel")
    @patch("src.components.vectorizing_data.CustomVectorDb")
    @patch("src.components.vectorizing_data.pd.read_csv")
    def test_ingest_vec_override(self, mock_read_csv, mock_vec_db, mock_model, mock_download, sample_csv):
        mock_download.return_value = "/mock/path"
        mock_read_csv.return_value = pd.DataFrame({
            "id": [1, 2],
            "label": [0, 1]
        })
        vectorizer = Vectorizer(data_path=sample_csv)
        asyncio.run(vectorizer.ingest_vec(override=True))
