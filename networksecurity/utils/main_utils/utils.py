import yaml
from networksecurity.exception.exceptions import NetworkSecurityException
from networksecurity.logging.logger import logger
import sys
import os
import dill
import pickle


def read_yaml_file(file_path: str) -> dict:
    """
    Reads a YAML file and returns its content as a dictionary.
    :param file_path: Path to the YAML file.
    :return: Dictionary containing the YAML file content.
    """
    try:
        with open(file_path, 'r') as file:
            return yaml.safe_load(file)
    except Exception as e:
        raise NetworkSecurityException(e, sys) from e
    
def write_yaml_file(file_path: str, content:object,replace:bool=False) -> None:
    """
    Writes a dictionary to a YAML file.
    :param file_path: Path to the YAML file.
    :param data: Dictionary to write to the file.
    """
    try:
        if replace:
            if os.path.exists(file_path):
                os.remove(file_path)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w') as file:
            yaml.dump(content, file)
            
    except Exception as e:
        raise NetworkSecurityException(e, sys) from e