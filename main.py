from networksecurity.componenets.data_ingestion import DataIngestion
from networksecurity.entity.config_entity import DataIngestionConfig,DataValidationConfig
from networksecurity.entity.artifact_entity import ArtifactEntity
from networksecurity.entity.config_entity import TrainingPipelineConfig
import numpy as np
import os
import sys
from dotenv import load_dotenv
load_dotenv()
from networksecurity.logging import logger
from networksecurity.exception.exceptions import NetworkSecurityException

if __name__ == "__main__":
    try:
        logger.logging.info("Starting data ingestion process")
        training_pipeline_config = TrainingPipelineConfig()
        logger.logging.info(f"Training pipeline config: {training_pipeline_config}")
        data_ingestion_config = DataIngestionConfig(training_pipeline_config)
        data_ingestion = DataIngestion(data_ingestion_config)
        artifact_entity = data_ingestion.initiate_data_ingestion()
        logger.logging.info(f"Data ingestion completed successfully. Artifacts: {artifact_entity}")
        data

        
    except Exception as e:
        logger.logging.error(f"Error during data ingestion: {e}")
        raise NetworkSecurityException(e, sys)