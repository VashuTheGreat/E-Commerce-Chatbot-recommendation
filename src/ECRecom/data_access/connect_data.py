from utils.asyncHandler import asyncHandler
import logging
import pandas as pd


class Connect_data:
    def __init__(self,data_path:str):
        self.data_path:str=data_path
        
    

    @asyncHandler
    async def load_data(self)->pd.DataFrame:
        logging.info("Entered in the connect db")
        data=pd.read_csv(self.data_path)
        logging.info("Exited from the connect db")
        return data

        