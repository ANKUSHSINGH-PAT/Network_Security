import sys
import os
import certifi

ca=certifi.where()
from dotenv import load_dotenv
load_dotenv()

mongo_db_url=os.getenv("MONGODB_URL")
print(mongo_db_url)

import pymongo

from networksecurity.exception.exceptions import NetworkSecurityException
from networksecurity.logging.logger import logging
from networksecurity.pipeline.training_pipeline import TrainingPipeline

from fastapi import FastAPI,File,UploadFile,Request
from fastapi.middleware.cors import CORSMiddleware
from uvicorn import run as app_run
from fastapi.responses import Response
from starlette.responses import RedirectResponse
import pandas as pd

from networksecurity.utils.main_utils.utils import load_object

from networksecurity.constant.training_pipeline import DATA_INGESTION_COLLECTION_NAME,DATA_INGESTION_DATABASE_NAME

app=FastAPI()
origins=["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
@app.get("/")
async def root():
    return RedirectResponse(url="/docs")




from fastapi import BackgroundTasks

@app.post("/train")
async def train_model(background_tasks: BackgroundTasks):
    try:
        pipeline = TrainingPipeline()

        
        # ✅ Run in background thread to avoid blocking the request
        background_tasks.add_task(pipeline.run_pipeline)

        return {"message": "Training pipeline started in the background."}

    except NetworkSecurityException as ne:
        logging.error(str(ne))
        #raise HTTPException(status_code=500, detail=f"Pipeline error: {str(ne)}")

    except Exception as e:
        logging.error(str(e))
        #raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


# Run the app
if __name__ == "__main__":
    app_run("main:app", host="0.0.0.0", port=8000, reload=True)