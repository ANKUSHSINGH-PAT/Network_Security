from dataclasses import dataclass

@dataclass
class ArtifactEntity:
    train_file_path: str
    test_file_path: str

@dataclass
class DataValidationArtifact:
    valid_train_file_path: str
    valid_test_file_path: str
    invalid_train_file_path: str
    invalid_test_file_path: str
    drift_report_file_path: str

@dataclass
class DataTransformationArtifact:
    transformed_object_file_path: str
    transformed_train_file_path: str
    transformed_test_file_path: str


@dataclass
class ModelTrainerArtifact:
    trained_model_file_path: str
    model_accuracy: float
    is_trained: bool
    message: str

@dataclass
class ClassificationMetricArtifact:
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    confusion_matrix: dict
