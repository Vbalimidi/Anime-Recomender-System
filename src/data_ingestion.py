import os
import pandas as pd
from google.cloud import storage
from src.logger import get_logger
from src.custom_exception import CustomException
from config.paths_config import *
from utils.common_functions import read_yaml

logger = get_logger(__name__)

class DataIngestion:
    def __init__(self, config):
        self.config = config["data_ingestion"]
        self.bucket_name = self.config["bucket_name"]
        self.file_name = self.config["bucket_file_names"]

        os.makedirs(RAW_DIR,exist_ok=True)

        logger.info("DATA INGESTION STARTED ....")
    
    def download_csv_from_gcp (self):
        try:
            client = storage.Client()
            bucket = client.bucket(self.bucket_name)

            for filename in self.file_name:
                filepath = os.path.join(RAW_DIR, filename)

                if filename == "animelist.csv":
                    blob = bucket.blob(filename)
                    blob.download_to_filename(filepath)

                    data = pd.read_csv(filepath, nrows=5000000)
                    data.to_csv(filepath, index=False)
                    logger.info("Only downloading 5M rows")
                else:
                    blob = bucket.blob(filename)
                    blob.download_to_filename(filepath)
                    logger.info("Downloading smaller files")
        except Exception as e:
            logger.error("Error while downloading data from GCP")
            raise CustomException ("Failed to download data")
        
    def run(self):
        try:
            logger.info("Starting data ingestion process")
            self.download_csv_from_gcp()
            logger.info("Data ingestion completed")
        except CustomException as ce:
            logger.error(f"CustomException : {str(ce)}")
        finally:
            logger.info("DATA INGESTION COMPLETED")

if __name__=="__main__":
    data_ingestion = DataIngestion(read_yaml(CONFIG_PATH))
    data_ingestion.run()