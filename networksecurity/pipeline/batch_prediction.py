import os
import sys
import pandas as pd
import numpy as np
from datetime import datetime
from typing import List, Dict, Any

from networksecurity.exception.exceptions import NetworkSecurityException
from networksecurity.logging.logger import logging

from networksecurity.entity.config_entity import TrainingPipelineConfig
from networksecurity.entity.artifact_entity import ModelTrainerArtifact

from networksecurity.utils.main_utils.utils import load_object
from networksecurity.utils.model.estimator import NetworkModel

from networksecurity.constant.training_pipeline import (
    SAVED_MODEL_DIR,
    MODEL_FILE_NAME,
    PREPROCESSING_OBJECT_FILE_NAME,
    TARGET_COLUMN
)


class BatchPredictionConfig:
    """Configuration class for batch prediction pipeline"""
    
    def __init__(self, training_pipeline_config: TrainingPipelineConfig):
        self.training_pipeline_config = training_pipeline_config
        self.model_file_path = os.path.join(SAVED_MODEL_DIR, MODEL_FILE_NAME)
        self.preprocessor_file_path = os.path.join(
            training_pipeline_config.artifact_dir,
            "data_transformation",
            "transformed_object",
            PREPROCESSING_OBJECT_FILE_NAME
        )
        self.prediction_dir = os.path.join(
            training_pipeline_config.artifact_dir,
            "batch_prediction"
        )
        self.prediction_file_path = os.path.join(
            self.prediction_dir,
            "predictions.csv"
        )
        self.prediction_log_file_path = os.path.join(
            self.prediction_dir,
            "prediction_log.txt"
        )


class BatchPredictionArtifact:
    """Artifact class to store batch prediction results"""
    
    def __init__(self, prediction_file_path: str, prediction_log_file_path: str):
        self.prediction_file_path = prediction_file_path
        self.prediction_log_file_path = prediction_log_file_path


class BatchPrediction:
    """Main class for batch prediction pipeline"""
    
    def __init__(self, batch_prediction_config: BatchPredictionConfig):
        self.batch_prediction_config = batch_prediction_config
        self.model = None
        self.preprocessor = None
        
    def load_model_and_preprocessor(self):
        """Load the trained model and preprocessor"""
        try:
            logging.info("Loading trained model and preprocessor")
            
            # Load the model
            if os.path.exists(self.batch_prediction_config.model_file_path):
                self.model = load_object(self.batch_prediction_config.model_file_path)
                logging.info(f"Model loaded successfully from {self.batch_prediction_config.model_file_path}")
            else:
                raise NetworkSecurityException(
                    f"Model file not found at {self.batch_prediction_config.model_file_path}",
                    sys
                )
            
            # Load the preprocessor
            if os.path.exists(self.batch_prediction_config.preprocessor_file_path):
                self.preprocessor = load_object(self.batch_prediction_config.preprocessor_file_path)
                logging.info(f"Preprocessor loaded successfully from {self.batch_prediction_config.preprocessor_file_path}")
            else:
                raise NetworkSecurityException(
                    f"Preprocessor file not found at {self.batch_prediction_config.preprocessor_file_path}",
                    sys
                )
                
        except Exception as e:
            raise NetworkSecurityException(e, sys)
    
    def validate_input_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """Validate and clean input data for prediction"""
        try:
            logging.info("Validating input data for prediction")
            
            # Check if data is empty
            if data.empty:
                raise NetworkSecurityException("Input data is empty", sys)
            
            # Remove target column if present
            if TARGET_COLUMN in data.columns:
                data = data.drop(columns=[TARGET_COLUMN])
                logging.info(f"Removed target column '{TARGET_COLUMN}' from input data")
            
            # Check for missing values
            missing_values = data.isnull().sum().sum()
            if missing_values > 0:
                logging.warning(f"Found {missing_values} missing values in input data")
                # You can implement imputation strategy here if needed
            
            # Check data types and convert if necessary
            for column in data.columns:
                if data[column].dtype == 'object':
                    try:
                        data[column] = pd.to_numeric(data[column], errors='coerce')
                        logging.info(f"Converted column '{column}' to numeric")
                    except:
                        logging.warning(f"Could not convert column '{column}' to numeric")
            
            logging.info(f"Data validation completed. Shape: {data.shape}")
            return data
            
        except Exception as e:
            raise NetworkSecurityException(e, sys)
    
    def predict_batch(self, data: pd.DataFrame) -> np.ndarray:
        """Perform batch prediction on the input data"""
        try:
            logging.info("Starting batch prediction")
            
            # Validate input data
            validated_data = self.validate_input_data(data)
            
            # Create NetworkModel instance
            network_model = NetworkModel(preprocessor=self.preprocessor, model=self.model)
            
            # Perform predictions
            predictions = network_model.predict(validated_data)
            
            logging.info(f"Batch prediction completed. Predictions shape: {predictions.shape}")
            return predictions
            
        except Exception as e:
            raise NetworkSecurityException(e, sys)
    
    def save_predictions(self, data: pd.DataFrame, predictions: np.ndarray) -> str:
        """Save predictions to file along with input data"""
        try:
            logging.info("Saving predictions to file")
            
            # Create prediction directory
            os.makedirs(self.batch_prediction_config.prediction_dir, exist_ok=True)
            
            # Create results dataframe
            results_df = data.copy()
            results_df['predicted_result'] = predictions
            
            # Save to CSV
            results_df.to_csv(self.batch_prediction_config.prediction_file_path, index=False)
            
            logging.info(f"Predictions saved to {self.batch_prediction_config.prediction_file_path}")
            return self.batch_prediction_config.prediction_file_path
            
        except Exception as e:
            raise NetworkSecurityException(e, sys)
    
    def log_prediction_summary(self, data: pd.DataFrame, predictions: np.ndarray):
        """Log prediction summary statistics"""
        try:
            logging.info("Creating prediction summary log")
            
            # Create prediction directory
            os.makedirs(self.batch_prediction_config.prediction_dir, exist_ok=True)
            
            # Calculate summary statistics
            unique_predictions, counts = np.unique(predictions, return_counts=True)
            prediction_summary = dict(zip(unique_predictions, counts))
            
            # Create log content
            log_content = f"""
            ========================================
            BATCH PREDICTION SUMMARY
            ========================================
            Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            
            Input Data:
            - Total records: {len(data)}
            - Features: {len(data.columns)}
            - Shape: {data.shape}
            
            Predictions:
            - Total predictions: {len(predictions)}
            - Prediction distribution: {prediction_summary}
            
            Files:
            - Predictions saved to: {self.batch_prediction_config.prediction_file_path}
            ========================================
            """
            
            # Save log
            with open(self.batch_prediction_config.prediction_log_file_path, 'w') as f:
                f.write(log_content)
            
            logging.info(f"Prediction summary logged to {self.batch_prediction_config.prediction_log_file_path}")
            
        except Exception as e:
            raise NetworkSecurityException(e, sys)
    
    def initiate_batch_prediction(self, input_data: pd.DataFrame) -> BatchPredictionArtifact:
        """Main method to initiate batch prediction pipeline"""
        try:
            logging.info("Starting batch prediction pipeline")
            
            # Load model and preprocessor
            self.load_model_and_preprocessor()
            
            # Perform batch prediction
            predictions = self.predict_batch(input_data)
            
            # Save predictions
            prediction_file_path = self.save_predictions(input_data, predictions)
            
            # Log prediction summary
            self.log_prediction_summary(input_data, predictions)
            
            # Create artifact
            batch_prediction_artifact = BatchPredictionArtifact(
                prediction_file_path=prediction_file_path,
                prediction_log_file_path=self.batch_prediction_config.prediction_log_file_path
            )
            
            logging.info("Batch prediction pipeline completed successfully")
            return batch_prediction_artifact
            
        except Exception as e:
            raise NetworkSecurityException(e, sys)


class BatchPredictionPipeline:
    """High-level pipeline class for batch prediction"""
    
    def __init__(self):
        self.training_pipeline_config = TrainingPipelineConfig()
        self.batch_prediction_config = BatchPredictionConfig(self.training_pipeline_config)
    
    def run_batch_prediction(self, input_data: pd.DataFrame) -> BatchPredictionArtifact:
        """Run the complete batch prediction pipeline"""
        try:
            logging.info("Initializing batch prediction pipeline")
            
            batch_prediction = BatchPrediction(self.batch_prediction_config)
            batch_prediction_artifact = batch_prediction.initiate_batch_prediction(input_data)
            
            logging.info("Batch prediction pipeline completed successfully")
            return batch_prediction_artifact
            
        except Exception as e:
            raise NetworkSecurityException(e, sys)
    
    def predict_from_file(self, input_file_path: str) -> BatchPredictionArtifact:
        """Run batch prediction from a CSV file"""
        try:
            logging.info(f"Loading input data from file: {input_file_path}")
            
            if not os.path.exists(input_file_path):
                raise NetworkSecurityException(f"Input file not found: {input_file_path}", sys)
            
            # Load data from file
            input_data = pd.read_csv(input_file_path)
            
            # Run batch prediction
            return self.run_batch_prediction(input_data)
            
        except Exception as e:
            raise NetworkSecurityException(e, sys)
    
    def predict_from_dataframe(self, input_data: pd.DataFrame) -> BatchPredictionArtifact:
        """Run batch prediction from a pandas DataFrame"""
        try:
            logging.info("Running batch prediction from DataFrame")
            
            if not isinstance(input_data, pd.DataFrame):
                raise NetworkSecurityException("Input must be a pandas DataFrame", sys)
            
            # Run batch prediction
            return self.run_batch_prediction(input_data)
            
        except Exception as e:
            raise NetworkSecurityException(e, sys)
