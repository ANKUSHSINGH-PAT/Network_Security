from networksecurity.componenets.data_ingestion import DataIngestion
from networksecurity.componenets.data_validation import DataValidation
from networksecurity.entity.config_entity import DataIngestionConfig,DataValidationConfig,DataTransformationConfig,TrainingPipelineConfig
from networksecurity.entity.artifact_entity import ArtifactEntity
from networksecurity.componenets.data_transformation import DataTransformation
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
        data_validation_config = DataValidationConfig(training_pipeline_config)
        data_validation = DataValidation(artifact_entity, data_validation_config)
        logger.logging.info("Starting data validation process")
        data_validation_artifact = data_validation.initiate_data_validation()
        logger.logging.info(f"Data validation completed successfully. Artifacts: {data_validation_artifact}")

        data_transformation_config = DataTransformationConfig(training_pipeline_config)
        dataTransformation= DataTransformation(data_validation_artifact, data_transformation_config)
        dataTransformation_artificat=dataTransformation.initiate_data_transformation()
        print(f"Data transformation artifacts: {dataTransformation_artificat}")
        logger.logging.info("Data transformation completed successfully")
  
    except Exception as e:
        logger.logging.error(f"Error during data ingestion: {e}")
        raise NetworkSecurityException(e, sys)