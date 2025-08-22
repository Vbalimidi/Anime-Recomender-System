import os
import pandas as pd
import numpy as np
import joblib
from sklearn.model_selection import train_test_split
from src.logger import get_logger
from src.custom_exception import CustomException
from config.paths_config import *
import sys

logger = get_logger(__name__)

class DataProcessor:
    def __init__(self, input_file, output_dir):
        self.input_file = input_file
        self.output_dir = output_dir
        
        self.rating_df = None
        self.anime_df = None
        self.X_train_array = None
        self.X_test_array = None
        self.y_train_array = None
        self.y_test_array = None

        self.user_encoding = {}
        self.user_decoding = {}
        self.anime_encoding = {}
        self.anime_decoding = {}

        os.makedirs(self.output_dir, exist_ok=True)
        logger.info("Data Processing...")

    def load_data(self, usecols):
        try:
            self.rating_df = pd.read_csv(self.input_file, low_memory=True, usecols=usecols)
            logger.info(f"Data loaded successfully from {self.input_file}")
        except Exception as e:
            logger.error(f"Error loading data: {e}")
            raise CustomException(f"Error loading data: {e}")
    
    def filter_users(self, min_ratings=400):
        try:
            n_ratings = self.rating_df["user_id"].value_counts()
            self.rating_df = self.rating_df[self.rating_df["user_id"].isin(n_ratings[n_ratings>=400].index)].copy()
            logger.info(f"Filtered users with at least {min_ratings} ratings")
        except Exception as e:
            logger.error(f"Error filtering users: {e}")
            raise CustomException(f"Error filtering users: {e}")
    
    def scale_ratings(self):
        try:
            minimun_rating = min(self.rating_df["rating"])
            maximun_rating = max(self.rating_df["rating"])
            self.rating_df["rating"] = self.rating_df["rating"].apply(lambda x: (x-minimun_rating)/(maximun_rating-minimun_rating)).values.astype(np.float64)
            logger.info("Ratings scaled to [0, 1]")
        except Exception as e:
            logger.error(f"Error scaling ratings: {e}")
            raise CustomException(f"Error scaling ratings: {e}")
    
    def encode_data (self):
        try:
            # Users
            user_ids = self.rating_df["user_id"].unique().tolist()
            self.user_encoding = {x: i for i , x in enumerate(user_ids)}
            self.user_decoding = {i: x for i , x in enumerate(user_ids)}
            self.rating_df["user"] = self.rating_df["user_id"].map(self.user_encoding)
            # Animes
            anime_ids = self.rating_df["anime_id"].unique().tolist()
            self.anime_encoding = {x: i for i , x in enumerate(anime_ids)}
            self.anime_decoding = {i: x for i , x in enumerate(anime_ids)}
            self.rating_df["anime"] = self.rating_df["anime_id"].map(self.anime_encoding)
            logger.info("Data encoded successfully")
        except Exception as e:
            logger.error(f"Error encoding data: {e}")
            raise CustomException(f"Error encoding data: {e}")
    
    def split_data(self, test_size=1000, random_state=42):
        try:
            self.rating_df = self.rating_df.sample(frac=1, random_state=42).reset_index(drop=True)
            X = self.rating_df[["user", "anime"]].values
            y = self.rating_df["rating"]
            train_indicies = self.rating_df.shape[0]-test_size
            X_train, X_test, y_train, y_test = (
                X[:train_indicies],
                X[train_indicies :],
                y[:train_indicies],
                y[train_indicies :]
            )
            self.X_train_array = [X_train[: , 0], X_train[:, 1]]
            self.X_test_array = [X_test[: , 0], X_test[:, 1]]
            self.y_train_array = y_train
            self.y_test_array = y_test
            logger.info("Data split into training and testing sets")
        except Exception as e:
            logger.error(f"Error splitting data: {e}")
            raise CustomException(f"Error splitting data: {e}")
        
    def save_artifacts(self):
        try:
            artifacts = {
                "user_encoding": self.user_encoding,
                "user_decoding": self.user_decoding,
                "anime_encoding": self.anime_encoding,
                "anime_decoding": self.anime_decoding,
            }

            for name,data in artifacts.items():
                joblib.dump(data, os.path.join(self.output_dir, f"{name}.pkl"))
                logger.info(f"Saved {name} to {self.output_dir}/{name}.pkl")
            
            joblib.dump(self.X_train_array, X_TRAIN_ARRAY)
            joblib.dump(self.X_test_array, X_TEST_ARRAY)
            joblib.dump(self.y_train_array, Y_TRAIN_ARRAY)
            joblib.dump(self.y_test_array, Y_TEST_ARRAY)

            self.rating_df.to_csv(RATING_DF, index=False)

            logger.info("Artifacts saved successfully")
        except Exception as e:
            logger.error(f"Error saving artifacts: {e}")
            raise CustomException(f"Error saving artifacts: {e}")

    def process_anime_data(self):
        try:
            df = pd.read_csv(ANIME_CSV)
            cols = ["MAL_ID", "Name", "Genres", "sypnopsis"]
            synopsis_df = pd.read_csv(SYNOPSIS_CSV, usecols=cols)

            df = df.replace("Unknown", np.nan)

            def getAnimeName(anime_id):
                try:
                    name = df[df.anime_id == anime_id].eng_version.values[0]
                    if name is np.nan:
                        name = df[df.anime_id == anime_id].Name.values[0]
                except:
                    print("Error")
                return name
            
            df["anime_id"] = df["MAL_ID"]
            df["eng_version"] = df["English name"]
            df["eng_version"] = df.anime_id.apply(lambda x:getAnimeName(x))

            df.sort_values(by=["Score"], inplace=True, ascending=False, kind="quicksort", na_position="last")

            df = df[["anime_id", "eng_version", "Score", "Genres", "Episodes", "Type", "Premiered", "Members"]]

            df.to_csv(DF, index=False)
            synopsis_df.to_csv(SYNOPSIS_DF, index=False)

            logger.info("Anime data processed and saved successfully")

        except Exception as e:
            logger.error(f"Error processing anime data: {e}")
            raise CustomException(f"Error processing anime data: {e}")
        
    def run(self):
        try:
            self.load_data(usecols=["user_id","anime_id", "rating"])
            self.filter_users()
            self.scale_ratings()
            self.encode_data()
            self.split_data()
            self.save_artifacts()
            self.process_anime_data()
            logger.info("Data processing pipeline completed successfully")
        except Exception as e:
            logger.error(f"Error in data processing pipeline: {e}")
            raise CustomException(f"Error in data processing pipeline: {e}")
        
if __name__ == "__main__":
    data_processor = DataProcessor(ANIMELIST_CSV, PROCESSED_DIR)
    data_processor.run()
