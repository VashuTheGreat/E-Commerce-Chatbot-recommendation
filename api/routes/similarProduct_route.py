from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from fastapi import HTTPException

from typing import List,Literal
from src.pipelines.similarProduct_pipeline import SimilarProductPipeline
from src.core.dependencies import data_frame,df_schema
from api.middlewares.multer_middleware import multer_middleware_no_save
from src.utils.vector_utils import _get_image_feat, _get_text_feat
from src.entity.config_entity import ModelTrainingConfig
from src.constants import DEVICE
similarProduct_pipeline = SimilarProductPipeline()
config = ModelTrainingConfig()
router = APIRouter()

@router.post("/similar-products-im")
async def get_similar_products_im(product_vec= Depends(multer_middleware_no_save)):
    """Endpoint to retrieve similar products based on the provided product vector and type (image or text)."""
    # Logic to retrieve similar products based on the product_id
    # This is a placeholder implementation; replace with actual logic
    try:
        type = 'image'
        product_vec = _get_image_feat(product_vec,config=config,device=DEVICE)
        similar_products = await similarProduct_pipeline.initiate(product_vec,type)
        return JSONResponse(status_code=200, content={"data": similar_products,"success": True, "message": "Similar products retrieved successfully."})
    except Exception as e:
        return HTTPException(status_code=500, detail={"data": [],"success": False, "message": f"Error retrieving similar products: {str(e)}"})

@router.post("/similar-products-txt")
async def get_similar_products_txt(product_vec:str):
    """Endpoint to retrieve similar products based on the provided product vector and type (image or text)."""
    # Logic to retrieve similar products based on the product_id
    # This is a placeholder implementation; replace with actual logic
    try:
        type = 'text'
        product_vec = _get_text_feat(product_vec,config=config,device=DEVICE)

        similar_products = await similarProduct_pipeline.initiate(product_vec,type)
        return JSONResponse(status_code=200, content={"data": similar_products,"success": True, "message": "Similar products retrieved successfully."})
    except Exception as e:
        return HTTPException(status_code=500, detail={"data": [],"success": False, "message": f"Error retrieving similar products: {str(e)}"})



@router.get("/all-id")
async def get_all_product_ids():
    """Endpoint to retrieve all product IDs."""
    try:
        df = data_frame()
        product_ids = df['id'].tolist()
        return JSONResponse(status_code=200, content={"data": product_ids,"success": True, "message": "Product IDs retrieved successfully."})
    except Exception as e:
        return HTTPException(status_code=500, detail={"data": [],"success": False, "message": f"Error retrieving product IDs: {str(e)}"})


@router.get("/schema")
async def get_data_schema():
    """Endpoint to retrieve the schema of the data frame."""
    try:
        schema = df_schema()
        return JSONResponse(status_code=200, content={"data": schema,"success": True, "message": "Data schema retrieved successfully."})
    except Exception as e:
        return HTTPException(status_code=500, detail={"data": [],"success": False, "message": f"Error retrieving data schema: {str(e)}"})


@router.get("/{product_id}")
async def get_product_by_id(product_id: int):
    """Endpoint to retrieve product details based on the provided product ID."""
    try:
        df = data_frame()
        product_details = df.loc[df['id'] == product_id]
        if product_details.empty:
            return HTTPException(status_code=404, detail={"data": [], "success": False, "message": "Product not found."})
        return JSONResponse(status_code=200, content={"data": product_details.to_dict(orient="records"), "success": True, "message": "Product details retrieved successfully."})
    except Exception as e:
        return HTTPException(status_code=500, detail={"data": [], "success": False, "message": f"Error retrieving product details: {str(e)}"})