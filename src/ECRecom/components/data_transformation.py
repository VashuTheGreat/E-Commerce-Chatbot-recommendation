from utils.asyncHandler import asyncHandler
from src.ECRecom.data_access.connect_data import Connect_data
from src.ECRecom.entity.config_entity import DataIngestionConfig,DataTransformationConfig
from src.ECRecom.constants import ARTIFACT_FOLDER,BATCH_SIZE
from src.ECRecom.entity.artifact_entity import DataIngestionArtifact,DataTransformationArtifact
import pandas as pd
import faiss
from pathlib import Path
from src.ECRecom.constants import EMBEDDING_MODEL,VECTOR_DB_PATH
from langchain_community.docstore.in_memory import InMemoryDocstore
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document
from tqdm import tqdm
import os
import logging

class Data_Transformator:
    def __init__(self,data_ingestion_artifact:DataIngestionArtifact,data_transformation_config:DataTransformationConfig):
        self.data_ingestion_artifact=data_ingestion_artifact
        self.data_transformation_config=data_transformation_config
        logging.info(f"Data_Transformator initialized.")
        
    @asyncHandler
    async def get_vector_db(self):
        logging.info(f"Initializing vector DB with model: {EMBEDDING_MODEL}")
        embedding_model = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
        embedding_dim = len(embedding_model.embed_query("hello world"))
        index = faiss.IndexFlatL2(embedding_dim)
        docstore = InMemoryDocstore()
        index_to_docstore_id = {}
        vector_store = FAISS(
            embedding_function=embedding_model,
            index=index,
            docstore=docstore,
            index_to_docstore_id=index_to_docstore_id,
        )
        return vector_store
    
    @asyncHandler
    async def get_documents(self,data:pd.DataFrame):
        logging.info("Creating documents from dataframe...")
        import ast
        docs=[]

        for _, i in tqdm(data.iterrows(), total=len(data), desc="Creating Documents"):
            metadata = {}
            if 'meta_data' in i and pd.notna(i['meta_data']):
                try:
                    metadata = ast.literal_eval(i['meta_data'])
                except Exception as e:
                    logging.warning(f"Failed to parse metadata: {e}. Using raw string.")
                    metadata = {"raw": i['meta_data']}
            
            docs.append(Document(page_content=i['product_search_description'], metadata=metadata))

        logging.info(f"Created {len(docs)} documents.")
        return docs

    @asyncHandler
    async def initiate(self)->DataTransformationArtifact:
        logging.info("Starting data transformation...")
        data:pd.DataFrame= pd.read_csv(self.data_ingestion_artifact.data_saved_path)
        vector_db=await self.get_vector_db()

        docs=await self.get_documents(data=data)
        
        logging.info("Adding documents to vector DB in batches...")
        batch_size = BATCH_SIZE
        for i in tqdm(range(0, len(docs), batch_size), desc="Adding to Vector DB"):
            batch = docs[i : i + batch_size]
            vector_db.add_documents(batch)

        os.makedirs(os.path.dirname(VECTOR_DB_PATH), exist_ok=True)
        vector_db.save_local(VECTOR_DB_PATH)
        logging.info(f"Vector DB saved to {VECTOR_DB_PATH}")

        data_transformation_artifact:DataTransformationArtifact=DataTransformationArtifact(
            vector_db_path=VECTOR_DB_PATH
        )
        return data_transformation_artifact
