from dotenv import load_dotenv
from networksecurity.entity.config_entity import DataIngestionConfig
from networksecurity.exception.exceptions import NetworkSecurityException
from networksecurity.logging.logger import logger
from networksecurity.entity.artifact_entity import ArtifactEntity

import os
import pymongo
import sys
from typing import List
import pandas as pd
from sklearn.model_selection import train_test_split


# Ensure MONGO_URI is loaded
load_dotenv()
MONGO_URL = os.getenv("MONGODB_URL")
print("MONGO_URL:", MONGO_URL)
if not MONGO_URL:
    raise ValueError("MONGODB_URI environment variable is not set.")


class DataIngestion:
    def __init__(self, data_ingestion_config: DataIngestionConfig):
        try:
            self.data_ingestion_config = data_ingestion_config
            self.mongo_client = pymongo.MongoClient(MONGO_URL)
        except Exception as e:
            raise NetworkSecurityException(e, sys)

    def export_collection_as_dataframe(self) -> pd.DataFrame:
        try:
            logger.info("Connecting to MongoDB and fetching data...")
            db = self.mongo_client[self.data_ingestion_config.database_name]
            logger.info(f"Databases available: {self.mongo_client.list_database_names()}")
            logger.info(f"Collections in DB '{db.name}': {db.list_collection_names()}")

            collection = db[self.data_ingestion_config.collection_name]
            logger.info(f"Using collection: {collection.name}")

            data = list(collection.find())
            logger.info(f"Fetched {len(data)} records from MongoDB.")

            if len(data) == 0:
                raise ValueError("No data found in MongoDB collection.")

            df = pd.DataFrame(data)
            if "_id" in df.columns:
                df.drop(columns=["_id"], inplace=True)
            df.dropna(inplace=True)

            logger.info(f"DataFrame shape after cleaning: {df.shape}")
            return df

        except Exception as e:
            raise NetworkSecurityException(e, sys)

    def export_data_into_feature_store(self, data: pd.DataFrame) -> pd.DataFrame:
        try:
            logger.info("Exporting data into feature store...")
            feature_store_path = self.data_ingestion_config.feature_store_file_path
            os.makedirs(os.path.dirname(feature_store_path), exist_ok=True)
            data.to_csv(feature_store_path, index=False)
            logger.info(f"Data exported to {feature_store_path}")
            return data
        except Exception as e:
            raise NetworkSecurityException(e, sys)

    def initiate_train_test_split(self, data: pd.DataFrame) -> List[pd.DataFrame]:
        try:
            logger.info("Splitting data into train and test sets...")
            train, test = train_test_split(
                data,
                test_size=self.data_ingestion_config.train_test_split_ratio,
                random_state=42
            )

            os.makedirs(os.path.dirname(self.data_ingestion_config.training_file_path), exist_ok=True)

            train.to_csv(self.data_ingestion_config.training_file_path, index=False)
            test.to_csv(self.data_ingestion_config.testing_file_path, index=False)

            logger.info(f"Train data saved at {self.data_ingestion_config.training_file_path}")
            logger.info(f"Test data saved at {self.data_ingestion_config.testing_file_path}")
            return [train, test]

        except Exception as e:
            raise NetworkSecurityException(e, sys)

    def initiate_data_ingestion(self) -> ArtifactEntity:
        try:
            logger.info("Initiating complete data ingestion pipeline...")
            data = self.export_collection_as_dataframe()
            data = self.export_data_into_feature_store(data)
            train, test = self.initiate_train_test_split(data)

            artifact = ArtifactEntity(
                train_file_path=self.data_ingestion_config.training_file_path,
                test_file_path=self.data_ingestion_config.testing_file_path
            )
            logger.info("Data ingestion pipeline completed successfully.")
            return artifact

        except Exception as e:
            raise NetworkSecurityException(e, sys)
