from networksecurity.entity.artifact_entity import ModelClassificationArtifact
from networksecurity.exception.exceptions import NetworkSecurityException
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from networksecurity.componenets.model_trainer import model_trainer
import sys





def evaluate_classification_model(y_true: list, y_pred: list) -> ModelClassificationArtifact:
    """
    Evaluates the classification model using accuracy, precision, recall, and F1 score.
    
    :param y_true: List of true labels.
    :param y_pred: List of predicted labels.
    :return: ModelClassificationArtifact containing evaluation metrics.
    """
    try:
        accuracy = accuracy_score(y_true, y_pred)
        precision = precision_score(y_true, y_pred, average='weighted')
        recall = recall_score(y_true, y_pred, average='weighted')
        f1 = f1_score(y_true, y_pred, average='weighted')

        confusion_matrix = {
            "true_positive": sum((y_true == 1) & (y_pred == 1)),
            "true_negative": sum((y_true == 0) & (y_pred == 0)),
            "false_positive": sum((y_true == 0) & (y_pred == 1)),
            "false_negative": sum((y_true == 1) & (y_pred == 0))
        }

        return ModelClassificationArtifact(
            accuracy=accuracy,
            precision=precision,
            recall=recall,
            f1_score=f1,
            confusion_matrix=confusion_matrix
        )
    
    except Exception as e:
        raise NetworkSecurityException(e, sys) from e
    
def evaluate_models(X_train, y_train, X_test, y_test):
    """
    Evaluates multiple classification models and returns the best model based on F1 score.
    
    :param X_train: Training features.
    :param y_train: Training labels.
    :param X_test: Testing features.
    :param y_test: Testing labels.
    :return: Best model and its evaluation metrics.
    """
    try:
        models=

        best_model = None
        best_f1_score = 0.0
        best_metrics = None

        for model_name, model in models.items():
            model.fit(X_train, y_train)
            y_pred = model.predict(X_test)
            metrics = evaluate_classification_model(y_test, y_pred)

            if metrics.f1_score > best_f1_score:
                best_f1_score = metrics.f1_score
                best_model = model
                best_metrics = metrics

        return best_model, best_metrics
    
    except Exception as e:
        raise NetworkSecurityException(e, sys) from e