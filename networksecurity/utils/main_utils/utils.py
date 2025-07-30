import yaml
from networksecurity.exception.exceptions import NetworkSecurityException
from networksecurity.logging.logger import logger
import sys
import os
import dill
import pickle
import numpy as np


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
    
def save_numpy_array_data(file_path: str, array: np.array):
    """
    Saves a numpy array to a file.
    :param file_path: Path to the file where the array will be saved.
    :param array: Numpy array to save.
    """
    try:
        dir_path = os.path.dirname(file_path)
        os.makedirs(dir_path, exist_ok=True)
        with open(file_path, 'wb') as file_obj:
            np.save(file_obj, array)
    except Exception as e:
        raise NetworkSecurityException(e, sys) from e

def save_object(file_path: str, obj: object) -> None:
    """
    Saves an object to a file using pickle.
    :param file_path: Path to the file where the object will be saved.
    :param obj: Object to save.
    """
    try:
        logger.info("Entered the save_object method of MainUtils class")
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'wb') as file_obj:
            pickle.dump(obj, file_obj)
        logger.info("Exited the save_object method of MainUtils class")
    except Exception as e:
        raise NetworkSecurityException(e, sys) from e
    
def load_numpy_array_data(file_path: str) -> np.array:
    """
    Loads a numpy array from a file.
    :param file_path: Path to the file from which the array will be loaded.
    :return: Numpy array loaded from the file.
    """
    try:
        with open(file_path, 'rb') as file_obj:
            return np.load(file_obj)
    except Exception as e:
        raise NetworkSecurityException(e, sys) from e
    
def load_object(file_path: str) -> object:
    """
    Loads an object from a file using pickle.
    :param file_path: Path to the file from which the object will be loaded.
    :return: Object loaded from the file.
    """
    try:
        logger.info("Entered the load_object method of MainUtils class")
        with open(file_path, 'rb') as file_obj:
            return pickle.load(file_obj)
        logger.info("Exited the load_object method of MainUtils class")
    except Exception as e:
        raise NetworkSecurityException(e, sys) from e