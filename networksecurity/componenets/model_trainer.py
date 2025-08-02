import os
import sys
import pickle
import mlflow
from dotenv import load_dotenv

from networksecurity.entity.config_entity import ModelTrainerConfig
from networksecurity.exception.exceptions import NetworkSecurityException
from networksecurity.logging import logger
from networksecurity.constant.training_pipeline import MODEL_FILE_NAME, SAVED_MODEL_DIR
from networksecurity.entity.artifact_entity import ModelTrainerArtifact, DataTransformationArtifact
from networksecurity.utils.main_utils.utils import load_numpy_array_data, load_object
from networksecurity.utils.ml_utils.metric.classification_metric import get_classification_score
from networksecurity.utils.model.estimator import NetworkModel

from networksecurity.utils.main_utils.utils import save_object,evaluate_models

from sklearn.linear_model import LogisticRegression
from sklearn.metrics import r2_score
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import (
    AdaBoostClassifier,
    GradientBoostingClassifier,
    RandomForestClassifier,
)
load_dotenv()

# Access them
mlflow_uri = os.getenv("MLFLOW_TRACKING_URI")
username = os.getenv("MLFLOW_TRACKING_USERNAME")
password = os.getenv("MLFLOW_TRACKING_PASSWORD")

import mlflow

mlflow.set_tracking_uri(mlflow_uri)
mlflow.set_experiment("Network_Security_Experiment")


class ModelTrainer:
    def __init__(self, model_trainer_config: ModelTrainerConfig,
                 data_transformation_artifact: DataTransformationArtifact):
        try:
            self.model_trainer_config = model_trainer_config
            self.data_transformation_artifact = data_transformation_artifact
        
        except Exception as e:
            raise NetworkSecurityException(e, sys) from e
        
    def track_model(self, model, classification_metric):
        """
        Tracks the model and its metrics using MLflow.
        
        :param model: The trained model to be tracked.
        :param classification_metric: The classification metrics of the model.
        """
        try:
            with mlflow.start_run():
                f1_score = classification_metric.f1_score
                precision_score = classification_metric.precision_score
                recall_score = classification_metric.recall_score

                mlflow.log_metric("f1_score", f1_score)
                mlflow.log_metric("precision_score", precision_score)
                mlflow.log_metric("recall_score", recall_score)

                import joblib
                joblib.dump(model, "temp_model.pkl")
                mlflow.log_artifact("temp_model.pkl")
        except Exception as e:
            logger.logging.error(f"Error tracking model with MLflow: {e}")
    def train_model(self, X_train, y_train,x_test, y_test):
        """
        Trains the model using the provided training data.
        
        :param x_train: Features for training.
        :param y_train: Labels for training.
        :return: Trained model.
        """
        models = {
                "Random Forest": RandomForestClassifier(verbose=1),
                "Decision Tree": DecisionTreeClassifier(),
                "Gradient Boosting": GradientBoostingClassifier(verbose=1),
                "Logistic Regression": LogisticRegression(verbose=1),
                "AdaBoost": AdaBoostClassifier(),
            }
        params={
            "Decision Tree": {
                'criterion':['gini', 'entropy', 'log_loss'],
                # 'splitter':['best','random'],
                # 'max_features':['sqrt','log2'],
            },
            "Random Forest":{
                # 'criterion':['gini', 'entropy', 'log_loss'],
                
                # 'max_features':['sqrt','log2',None],
                'n_estimators': [8,16,32,128,256]
            },
            "Gradient Boosting":{
                # 'loss':['log_loss', 'exponential'],
                'learning_rate':[.1,.01,.05,.001],
                'subsample':[0.6,0.7,0.75,0.85,0.9],
                # 'criterion':['squared_error', 'friedman_mse'],
                # 'max_features':['auto','sqrt','log2'],
                'n_estimators': [8,16,32,64,128,256]
            },
            "Logistic Regression":{},
            "AdaBoost":{
                'learning_rate':[.1,.01,.001],
                'n_estimators': [8,16,32,64,128,256]
            }
            
        }
        model_report:dict=evaluate_models(X_train=X_train,y_train=y_train,X_test=x_test,y_test=y_test,
                                          models=models,param=params)
        
        ## To get best model score from dict
        best_model_score = max(sorted(model_report.values()))

        ## To get best model name from dict

        best_model_name = list(model_report.keys())[
            list(model_report.values()).index(best_model_score)
        ]
        best_model = models[best_model_name]
        y_train_pred=best_model.predict(X_train)

        classification_train_metric=get_classification_score(y_true=y_train,y_pred=y_train_pred)

        self.track_model(best_model,classification_train_metric)
        
        ## Track the experiements with mlflow
       


        y_test_pred=best_model.predict(x_test)
        classification_test_metric=get_classification_score(y_true=y_test,y_pred=y_test_pred)
        self.track_model(best_model,classification_test_metric)

        #self.track_mlflow(best_model,classification_test_metric)

        preprocessor = load_object(file_path=self.data_transformation_artifact.transformed_object_file_path)
            
        model_dir_path = os.path.dirname(self.model_trainer_config.trained_model_file_path)
        os.makedirs(model_dir_path,exist_ok=True)

        Network_Model=NetworkModel(preprocessor=preprocessor,model=best_model)
        save_object(self.model_trainer_config.trained_model_file_path,obj=NetworkModel)
        #model pusher
        save_object("final_model/model.pkl",best_model)
        

        ## Model Trainer Artifact
        model_trainer_artifact=ModelTrainerArtifact(trained_model_file_path=self.model_trainer_config.trained_model_file_path,
                             train_metric_artifact=classification_train_metric,
                             test_metric_artifact=classification_test_metric
                             )
        logger.logging.info(f"Model trainer artifact: {model_trainer_artifact}")
        return model_trainer_artifact

        
          
    
    def initiate_model_trainer(self) -> ModelTrainerArtifact:
        """
        Initiates the model training process.
        
        :return: ModelTrainerArtifact containing the trained model and its accuracy.
        """
        try:
            # Load transformed data
            train_file_path = self.data_transformation_artifact.transformed_train_file_path
            test_file_path = self.data_transformation_artifact.transformed_test_file_path
            train_arr = load_numpy_array_data(train_file_path)
            test_arr = load_numpy_array_data(test_file_path)




            x_train,y_train,x_test,y_test=(
                train_arr[:,:-1],
                train_arr[:,-1],
                test_arr[:,:-1],
                test_arr[:,-1]
            )

            model_trainer_artifact=self.train_model(x_train, y_train,x_test, y_test)
            return model_trainer_artifact
        except Exception as e:
            raise NetworkSecurityException(e, sys) from e