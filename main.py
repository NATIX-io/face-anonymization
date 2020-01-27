import sys
import os
import io
import importlib
import uuid
import logging
import random
import base64
import hashlib
import mimetypes
import json
import imageio
import falcon
import yaml
import numpy as np
import mtcnn
from mtcnn.face_detector import FaceDetector
from resources.FaceDetectionResource import FaceDetectionResource

def init_logging():
    """Initialize logging to write to STDOUT."""
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger

def ensure_if_path_exists(pth):
    # Create target Directory if don't exist
    if not os.path.exists(pth):
        os.makedirs(pth)
    return None


def load_yaml(file_path):
    with open(file_path, 'r') as stream:    
        return yaml.load(stream)


 
""" 
In this part, the app initialized to create an API. There are multiple steps to be followed:
1) Initializing the API, loading the config file and loading the logger
2) Initializing different modules
3) adding routes
"""


""" Part 1 """
app = falcon.API()

config_path = os.environ.get('FACE_DETECTION_CONFIG', None)
if config_path is None:
    config_path = 'service.yaml'

config = load_yaml(config_path)

# Start the logging
logger = init_logging()
logger.info('Service config: %s' % config)

# Reading the config parameters
detect_min_size = config['detect_min_size']
assert isinstance(detect_min_size, int)



""" Part 2 """
# Resources
face_detection_resource = FaceDetectionResource(logger, detect_min_size)

""" Part 3 """
# face_detection_resource
app.add_route("/face_detection", face_detection_resource)
