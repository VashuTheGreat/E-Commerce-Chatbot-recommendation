from src.ECRecom.constants import VECTOR_DB_PATH, EMBEDDING_MODEL
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

class LoadVectorDB:
    def __init__(self):
        self.vector_db_path=VECTOR_DB_PATH
    
    def initiate(self,k:int=5):
        embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
        vector_db=FAISS.load_local(self.vector_db_path, embeddings=embeddings, allow_dangerous_deserialization=True)
        retriver=vector_db.as_retriever(search_kwargs={"k": k})
        return retriver