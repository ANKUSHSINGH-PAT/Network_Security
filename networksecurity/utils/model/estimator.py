from networksecurity.constant.training_pipeline import MODEL_FILE_NAME, SAVED_MODEL_DIR

import os,sys
from networksecurity.exception.exceptions import NetworkSecurityException
from networksecurity.entity.config_entity import ModelTrainerConfig
from networksecurity.entity.artifact_entity import ModelTrainerArtifact, DataTransformationArtifact
from networksecurity.utils.main_utils.utils import load_numpy_array_data, load_object
from networksecurity.logging.logger import logger


class NetworkModel:
    def __init__(self,preprocessor, model):
        try:

            self.preprocessor = preprocessor
            self.model = model
        except Exception as e:
            raise NetworkSecurityException(e, sys) from e
        
    def predict(self, X):
        """
        Predicts the labels for the given input data.
        
        :param X: Input data for prediction.
        :return: Predicted labels.
        """
        try:
            X_transformed = self.preprocessor.transform(X)
            predictions = self.model.predict(X_transformed)
            return predictions
        except Exception as e:
            raise NetworkSecurityException(e, sys) from e
