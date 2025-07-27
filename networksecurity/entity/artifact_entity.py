from dataclasses import dataclass

@dataclass
class ArtifactEntity:
    train_file_path: str
    test_file_path: str

@dataclass
class DataValidationArtifact:
    validation_status: bool
    validated_file_path: str
    invalid_file_path: str
    drift_report_file_path: str
    