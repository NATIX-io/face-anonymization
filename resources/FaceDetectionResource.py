import sys
import os
import io
import importlib
import pandas as pd
import faiss
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
from classifiers.nn_classifier import EmbeddingNNClassifier

def ensure_if_path_exists(pth):
    # Create target Directory if don't exist
    if not os.path.exists(pth):
        os.makedirs(pth)
    return None


def create_initial_tables(pth, __cols__):
    # Create target Directory if don't exist
    if not os.path.exists(pth):
        os.makedirs(pth)      
    
    # Create target file if don't exist
    if not os.path.isfile(os.path.join(pth, 'table_with_name.pkl')):
        df_name = pd.DataFrame(columns=__cols__)    
        df_name.reset_index()[__cols__].to_pickle(os.path.join(pth, 'table_with_name.pkl'))
    
    # Create target file if don't exist
    if not os.path.isfile(os.path.join(pth, 'table_without_name.pkl')):
        df_without_name = pd.DataFrame(columns=__cols__)
        df_without_name.reset_index()[__cols__].to_pickle(os.path.join(pth, 'table_without_name.pkl')) 
    
    return None

def ensure_customer_information_exist(data_path,  __cols__, customer_id="aiconix" ):
    faiss_index_path = os.path.join(data_path, customer_id,"nns")
    ensure_if_path_exists(faiss_index_path)

    table_path = os.path.join(data_path, customer_id,"db")
    create_initial_tables(table_path,   __cols__)

    image_import_path = os.path.join(data_path, customer_id,"pictures")
    ensure_if_path_exists(image_import_path)

def face_bounding_box(face, image):

    x0 = max(0, int(face.bb_p1[0])   ) # left 
    x0 = float(x0)/image.shape[1]

    x1 = min(image.shape[1] , int(face.bb_p2[0])     ) # right
    x1 = float(x1)/image.shape[1]

    y0 = max(0, int(face.bb_p1[1])     ) # up
    y0 = float(y0)/image.shape[0]

    y1 = min(image.shape[0] , int(face.bb_p2[1])      )  # down
    y1 = float(y1) /image.shape[0]           

    result = {"boundingPoly": {
                "vertices": [
                {
                    "x": x0,
                    "y": y0
                },
                {
                    "x": x0,
                    "y": y1
                },
                {
                    "x": x1,
                    "y": y0
                },
                {
                    "x": x1,
                    "y": y1
                }]
                },
                    "confidence": face.bb_confidence}
    return result



def get_image_format(req):
    content_type = req.headers.get('CONTENT-TYPE', None)
    if content_type in ['image/jpeg', 'image/jpg']:
        ext = 'jpg'
    elif content_type == 'image/png':
        ext = 'png'
    else:
        ext = None
    return ext 

class FaceDetectionResource():
    """
        HTTP POST endpoint that takes a single image as input and
        returns bounding boxes for each detected face.
        
        Args for __init__:
            logger: Python logger initialized in the main.py
            detect_min_size (int): minimum image size for MTCNN. At the moment it is 20 as default value in the config file

        Args for on_post:
            req: 1 image data with .png or .jpg format
        
        Response for on_post:
            response (dict): it gives back the face_bounding_box for all the recognized faces (please look above for the specific definition)
        

    """
 

    ## TODO: To write a more elegant way of adding parameters to the init
    def __init__(self, logger, detect_min_size ):
        self.logger = logger
        self.face_detector = FaceDetector(model_path=None, min_size=detect_min_size)
        self.logger.info("Starting: FaceDetectionResource")
    
    def on_post(self, req, resp):
        """
        This method checks: 
            0) Checks the header
            1) read the image extension. if it is png or jpg it continues
            2) it tries to read the image
            3) if it could read the image, it passes it to MTCNN (face_detector)
            4) face_detector gives back all the found faces
            5) Sends back the results
        """
        
        try:
            self.logger.info("FaceDetectionResource: Checking if the file has the necessary quality.")
            if 'CONTENT-TYPE' not in req.headers:
                resp.status = falcon.HTTP_400
                resp.body = 'Missing HTTP header: "Content-Type"\n'
                return

            # determine image format
            image_format = get_image_format(req)
            if image_format is None:
                resp.status = falcon.HTTP_400
                resp.body = 'Unsupported content type: %s\n' % image_format
                return

            # read and decode the image     
            bytes = req.stream.read()
            try:
                image = imageio.imread(bytes, image_format, as_gray=False, pilmode="RGB")
            except Exception as e:
                self.logger.error(e, exc_info=True)
                resp.status = falcon.HTTP_400
                resp.body = 'Error decoding image\n'
                return

            self.logger.info('FaceDetectionResource: Detecting faces')

            # detect faces on image
            faces = self.face_detector.detect_faces(image)
            self.logger.info('FaceDetectionResource: %d faces detected' % len(faces))
            


            # creating the output
            results = []
            for face in faces:
                f_bb = face_bounding_box(face, image)
                results.append(f_bb)

            response = {"detectedFaces": results}
            self.logger.info('FaceDetectionResource: Sending the results')
            resp.status = falcon.HTTP_200
            resp.body = json.dumps(response) + '\n'

        except Exception as e:
            self.logger.error(e, exc_info=True)
            resp.status = falcon.HTTP_500
