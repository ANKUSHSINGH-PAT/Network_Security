from dotenv import load_dotenv
from networksecurity.entity.config_entity import DataIngestionConfig,DataValidationConfig
from networksecurity.exception.exceptions import NetworkSecurityException
from networksecurity.logging.logger import logger
from networksecurity.entity.artifact_entity import ArtifactEntity, DataValidationArtifact
from networksecurity.constant.training_pipeline import SCHEMA_FILE_PATH
from networksecurity.utils.main_utils.utils import read_yaml_file,write_yaml_file

from scipy.stats import ks_2samp

import os
import pymongo
import sys
from typing import List
import pandas as pd

class DataValidation:
    def __init__(self, data_ingestion_artifact:ArtifactEntity, data_validation_config:DataValidationConfig):
        try:
           self.data_ingestion_artifact = data_ingestion_artifact
           self.data_validation_config = data_validation_config
           self.schema = self.read_yaml_file(SCHEMA_FILE_PATH)
        except Exception as e:
            raise NetworkSecurityException(e, sys) from e
        
    @staticmethod
    def read_data(file_path: str) -> pd.DataFrame:
        try:
            return pd.read_csv(file_path)
        except Exception as e:
            raise NetworkSecurityException(e, sys) from e
        
    def validate_numer_of_columns(self, dataframe: pd.DataFrame) -> bool:
        try:
            expected_columns = self.schema['columns']
            len_expected = len(expected_columns)
            len_actual = len(dataframe.columns)
            if len_expected != len_actual:
                logger.error(f"Expected {len_expected} columns, but got {len_actual}")
                return False
            
            actual_columns = dataframe.columns.tolist()
            if set(expected_columns) != set(actual_columns):
                logger.error(f"Column mismatch: Expected {expected_columns}, but got {actual_columns}")
                return False
            return True
        except Exception as e:
            raise NetworkSecurityException(e, sys) from e
        
    def data_drift(self, train_data: pd.DataFrame, test_data: pd.DataFrame) -> bool:
        try:
            report={}
            drift_detected = False
            for column in train_data.columns:
                if column in test_data.columns:
                    stat, p_value = ks_2samp(train_data[column], test_data[column])
                    report.update({
                        column: {
                            "statistic": stat,
                            "p_value": p_value
                        }
                    })
                    if p_value < 0.05:  # 5% significance level
                        logger.warning(f"Data drift detected in column '{column}' (p-value: {p_value})")
                        drift_detected = True
            drift_report_file_path = self.data_validation_config.drift_report_file_path
            dir_path= os.path.dirname(drift_report_file_path,report)
            os.makedirs(dir_path, exist_ok=True)
            write_yaml_file(drift_report_file_path, content=report)
        except Exception as e:
            raise NetworkSecurityException(e, sys) from e
        
    def initiate_data_validation(self) -> DataValidationArtifact:
        try:
            logger.info("Starting data validation process")
            self.validate_data()
            self.check_data_drift()
            logger.info("Data validation process completed successfully")
            train_file_path=self.data_ingestion_artifact.train_file_path,
            test_file_path=self.data_ingestion_artifact.test_file_path,
               
            train_dataframe=DataValidation.read_data(train_file_path)
            test_dataframe=DataValidation.read_data(test_file_path)

            validation_status = self.validate_numer_of_columns(train_dataframe) and \
                                self.validate_numer_of_columns(test_dataframe)
            if not validation_status:
                raise NetworkSecurityException("Data validation failed due to column mismatch.")
            status=self.data_drift(train_dataframe, test_dataframe)
            train_dataframe.to_csv(self.data_validation_config.valid_train_file_path, index=False)
            test_dataframe.to_csv(self.data_validation_config.valid_test_file_path, index=False)
        except Exception as e:
            raise NetworkSecurityException(e, sys) from e