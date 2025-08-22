import comet_ml
import joblib
import numpy as np
import os
from tensorflow.keras.callbacks import ModelCheckpoint, LearningRateScheduler, TensorBoard, EarlyStopping
from src.logger import get_logger
from src.custom_exception import CustomException
from src.base_model import BaseModel
from config.paths_config import *

logger = get_logger(__name__)

class ModelTraining:
    def __init__(self,data_path):
        self.data_path = data_path
        self.experiment = comet_ml.Experiment(
            api_key= "c5ztP2rJ0UWNgH6MsbOj1h8mU",
            project_name= "anime-recomender",
            workspace= "vbalimidi"
            )
        logger.info("Model Training & COMET ML initialised...")
    
    def load_data(self):
        try:
            X_train_array = joblib.load(X_TRAIN_ARRAY)
            X_test_array = joblib.load(X_TEST_ARRAY)
            y_train_array = joblib.load(Y_TRAIN_ARRAY)
            y_test_array = joblib.load(Y_TEST_ARRAY)
            logger.info("Data loaded successfully")
            return X_train_array, X_test_array, y_train_array, y_test_array
        except Exception as e:
            logger.error(f"Error loading data: {e}")
            raise CustomException(f"Error loading data: {e}")
    
    def train_model(self):
        try:
            X_train_array, X_test_array, y_train_array, y_test_array = self.load_data()
            n_users = len(joblib.load(USER_ENCODING))
            n_anime = len(joblib.load(ANIME_ENCODING))

            base_model = BaseModel(config_path=CONFIG_PATH)

            model = base_model.RecomenderNet(n_users, n_anime)

            start_learn = 0.00001
            min_learn = 0.00001
            max_learn = 0.00005
            batch_size = 10000

            ramup_epochs = 5
            sustain_epochs = 0
            exp_decay = 0.8

            def learn_func (epoch):
                if epoch < ramup_epochs:
                    return (max_learn-start_learn)/ramup_epochs*epoch + start_learn
                elif epoch < ramup_epochs+sustain_epochs:
                    return max_learn
                else:
                    return (max_learn-min_learn)*exp_decay ** (epoch-ramup_epochs-sustain_epochs)+min_learn

            learn_callback = LearningRateScheduler(lambda epoch: learn_func(epoch), verbose=0)

            model_checkpoint = ModelCheckpoint(filepath=CHECKPOINT_FILE_PATH, save_weights_only=True, monitor='val_loss', mode="min", save_best_only=True)

            early_stopping = EarlyStopping(patience=3, monitor="val_loss", mode="min", restore_best_weights=True)

            my_callbacks = [model_checkpoint, learn_callback, early_stopping]

            os.makedirs(os.path.dirname(CHECKPOINT_FILE_PATH), exist_ok=True)
            os.makedirs(MODEL_DIR, exist_ok=True)
            os.makedirs(WEIGHTS_DIR, exist_ok=True)

            try:
                history = model.fit(
                    x = X_train_array,
                    y = y_train_array,
                    batch_size = batch_size,
                    epochs = 20,
                    verbose = 1,
                    validation_data = (X_test_array, y_test_array),
                    callbacks = my_callbacks
                )
                model.load_weights(CHECKPOINT_FILE_PATH)
                logger.info("Model trained successfully")

                for epoch in range(len(history.history['loss'])):
                    train_loss = history.history['loss'][epoch]
                    val_loss = history.history['val_loss'][epoch]

                    self.experiment.log_metric("train_loss", train_loss, step=epoch)
                    self.experiment.log_metric("val_loss", val_loss, step=epoch)

            except Exception as e:
                logger.error(f"Error during model training: {e}")
                raise CustomException(f"Error during model training: {e}")
            
            self.save_model_weights(model)

        except Exception as e:
            logger.error(f"Error in model training: {e}")
            raise CustomException(f"Error in model training: {e}")  

    def extract_weights(self,layer_name, model):
        try:
            weight_layer = model.get_layer(layer_name)
            weights = weight_layer.get_weights()[0]
            weights = weights/np.linalg.norm(weights, axis=1).reshape((-1,1))
            logger.info(f"Weights extracted for layer: {layer_name}")
            return weights
        except Exception as e:
            logger.error(f"Error extracting weights for layer {layer_name}: {e}")
            raise CustomException(f"Error extracting weights for layer {layer_name}: {e}")

    def save_model_weights(self, model):
        try:
            model.save(MODEL_PATH)
            logger.info(f"Model saved at {MODEL_PATH}")
            user_weights = self.extract_weights("user_embedding", model)
            anime_weights = self.extract_weights("anime_embedding", model)

            joblib.dump(user_weights, USER_WEIGHTS_PATH)
            joblib.dump(anime_weights, ANIME_WEIGHTS_PATH)

            self.experiment.log_asset(MODEL_PATH)
            self.experiment.log_asset(USER_WEIGHTS_PATH)
            self.experiment.log_asset(ANIME_WEIGHTS_PATH)
            
            logger.info("User and Anime weights saved successfully")

        except Exception as e:
            logger.error(f"Error saving model weights: {e}")
            raise CustomException(f"Error saving model weights: {e}")

if __name__ == "__main__":
    model_trainer = ModelTraining(data_path=PROCESSED_DIR)
    model_trainer.train_model()

