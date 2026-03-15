

from src.ECRecom.data_access.load_vector_db import LoadVectorDB
class Predict_similar:
    def __init__(self):
        self.load_vector_db=LoadVectorDB()
    
    def initiate(self,query:str,k=5):
        retriver=self.load_vector_db.initiate(k=k)
        docs=retriver.invoke(query)
        return docs
        