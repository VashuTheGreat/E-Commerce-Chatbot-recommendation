from src.constants import VECTOR_DB_PATH, EMBEDDING_MODEL
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from src.utils.asyncHandler import asyncHandler
import logging
import pandas as pd


class LoadVectorDB:
    def __init__(self):
        self.vector_db_path=VECTOR_DB_PATH
    
    def initiate(self,k:int=5):
        embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
        vector_db=FAISS.load_local(self.vector_db_path, embeddings=embeddings, allow_dangerous_deserialization=True)
        retriver=vector_db.as_retriever(search_kwargs={"k": k})
        return retriver
    




class Connect_data:
    def __init__(self,data_path:str):
        self.data_path:str=data_path
        self.data =pd.read_csv(self.data_path)
        
    

    @asyncHandler
    async def load_data(self)->pd.DataFrame:
        logging.info("Entered in the connect db")
        data = self.data
        logging.info("Exited from the connect db")
        data = data.sample(n=4480, random_state=42)
        return data

        
