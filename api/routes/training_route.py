from dataclasses import asdict
from fastapi import APIRouter,Depends
from fastapi.responses import JSONResponse
from fastapi.exceptions import HTTPException
from src.pipelines.training_pipeline import TrainingPipeline
from src.entity.config_entity import DataIngestionConfig,DataTransformationConfig,ModelTrainingConfig,ModelEvaluationConfig
from api.middlewares.authenticate_user_middleware import authenticate_user

router = APIRouter()


@router.get("/train",dependencies=[Depends(authenticate_user)])
async def train_model():
    """Use this route for model training"""

    data_ingestion_config=DataIngestionConfig()
    data_transformation_config=DataTransformationConfig()
    model_training_config=ModelTrainingConfig()
    model_evaluation_config=ModelEvaluationConfig()
    
    training_pipeliine= TrainingPipeline(
        data_ingestion_config=data_ingestion_config,
        data_transformation_config=data_transformation_config,
        model_training_config=model_training_config,
        model_evaluation_config=model_evaluation_config
    )

    r = await training_pipeliine.initiate()
    if not r:
        raise HTTPException(status_code=500, detail={"data":None,"message":"training failed","success":False})
    

    return JSONResponse(status_code=200,content={"data":asdict(r),"message":"model Trained Succesfully","success":True})




