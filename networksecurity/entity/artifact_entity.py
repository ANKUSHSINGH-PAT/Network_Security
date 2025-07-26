from dataclasses import dataclass

@dataclass
class ArtifactEntity:
    train_file_path: str
    test_file_path: str
    