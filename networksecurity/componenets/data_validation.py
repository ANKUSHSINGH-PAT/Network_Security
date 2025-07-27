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
    def __init__(self, data_ingestion_artifact: ArtifactEntity, data_validation_config: DataValidationConfig):
        try:
            self.data_ingestion_artifact = data_ingestion_artifact
            self.data_validation_config = data_validation_config
            self.schema = read_yaml_file(SCHEMA_FILE_PATH)
        except Exception as e:
            raise NetworkSecurityException(e, sys) from e

    @staticmethod
    def read_data(file_path: str) -> pd.DataFrame:
        try:
            return pd.read_csv(file_path)
        except Exception as e:
            raise NetworkSecurityException(e, sys) from e

    def validate_number_of_columns(self, dataframe: pd.DataFrame) -> bool:
        try:
            expected_columns = self.schema['columns']
            if len(dataframe.columns) != len(expected_columns):
                logger.error(f"Expected {len(expected_columns)} columns, but got {len(dataframe.columns)}")
                return False
            if set(dataframe.columns) != set(expected_columns):
                logger.error(f"Column mismatch: Expected {expected_columns}, but got {dataframe.columns.tolist()}")
                return False
            return True
        except Exception as e:
            raise NetworkSecurityException(e, sys) from e

    def data_drift(self, train_data: pd.DataFrame, test_data: pd.DataFrame) -> bool:
        try:
            report = {}
            drift_detected = False
            for column in train_data.columns:
                if column in test_data.columns:
                    stat, p_value = ks_2samp(train_data[column], test_data[column])
                    report[column] = {
                        "statistic": stat,
                        "p_value": p_value
                    }
                    if p_value < 0.05:
                        logger.warning(f"Data drift detected in column '{column}' (p-value: {p_value})")
                        drift_detected = True

            drift_report_file_path = self.data_validation_config.drift_report_file_path
            dir_path = os.path.dirname(drift_report_file_path)
            os.makedirs(dir_path, exist_ok=True)
            write_yaml_file(drift_report_file_path, content=report)

            return not drift_detected
        except Exception as e:
            raise NetworkSecurityException(e, sys) from e

    def initiate_data_validation(self) -> DataValidationArtifact:
        try:
            logger.info("Starting data validation process")

            train_file_path = self.data_ingestion_artifact.train_file_path
            test_file_path = self.data_ingestion_artifact.test_file_path

            train_dataframe = self.read_data(train_file_path)
            test_dataframe = self.read_data(test_file_path)

            validation_status = self.validate_number_of_columns(train_dataframe) and \
                                self.validate_number_of_columns(test_dataframe)
            if not validation_status:
                raise NetworkSecurityException("Data validation failed due to column mismatch.", sys)

            status= self.data_drift(train_dataframe, test_dataframe)

            dir_path = os.path.dirname(self.data_validation_config.valid_train_file_path)
            os.makedirs(dir_path, exist_ok=True)


            # Save valid data
            train_dataframe.to_csv(self.data_validation_config.valid_train_file_path, index=False,header=True)
            test_dataframe.to_csv(self.data_validation_config.valid_test_file_path, index=False,header=True)

            data_validation_artifact = DataValidationArtifact(
                valid_train_file_path=self.data_validation_config.valid_train_file_path,
                valid_test_file_path=self.data_validation_config.valid_test_file_path,
                invalid_train_file_path=self.data_validation_config.invalid_train_file_path,
                invalid_test_file_path=self.data_validation_config.invalid_test_file_path,
                drift_report_file_path=self.data_validation_config.drift_report_file_path
            )

            logger.info("Data validation process completed successfully")
            return data_validation_artifact

        except Exception as e:
            raise NetworkSecurityException(e, sys) from e
