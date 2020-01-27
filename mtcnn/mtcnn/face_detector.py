"""Detect faces in images. The result is a bounding box and a set of face keypoints."""

import os
from collections import namedtuple
from scipy import misc
import cv2
import numpy as np
import tensorflow as tf
from mtcnn import detect_face

class Face(object):
    """A face in an image."""
    def __init__(self, bb_p1, bb_p2, bb_confidence, left_eye, right_eye, nose, mouth_left, mouth_right, embedding=None):
        """
        Args:
            bb_p1 (int,int): Bounding box upper left corner (x,y)
            bb_p2 (int,int): Bounding box lower right corner (x,y)
            bb_confidence (float): Bounding box confidence
            left_eye (int,int): Left eye keypoint (x,y)
            right_eye (int,int): Right eye keypoint (x,y)
            nose (int,int): Nose keypoint (x,y)
            mouth_left (int,int): Mouth left keypoint (x,y)
            mouth_right (int,int): Mouth right keypoint (x,y)
        """
        self.bb_p1 = bb_p1
        self.bb_p2 = bb_p2
        self.bb_confidence = bb_confidence
        self.left_eye = left_eye
        self.right_eye = right_eye
        self.nose = nose
        self.mouth_left = mouth_left
        self.mouth_right = mouth_right
        self.embedding = embedding

    def __str__(self):
        return 'Face[bb_p1=%s, bb_p2=%s, bb_confidence=%f, left_eye=%s, right_eye=%s, nose=%s, mouth_left=%s, mouth_right=%s]' % (self.bb_p1, self.bb_p2, self.bb_confidence, self.left_eye, self.right_eye, self.nose, self.mouth_left, self.mouth_right)
    
    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        else:
            return False


class FaceDetector(object):

    # This class uses the MTCNN model from:
    #   "Joint Face Detection and Alignment using Multi-task Cascaded Convolutional Networks".
    # 
    # The TF implementation and pre-trained model are from the `David Sandberg` Facenet repository at: 
    #   https://github.com/davidsandberg/facenet/tree/master/src/align

    def __init__(self, model_path, min_size=20, tf_config=None):
        self.minsize = min_size # minimum size of face
        self.threshold = [ 0.6, 0.7, 0.7 ]  # three steps's threshold
        self.factor = 0.709 # scale factor
        print('Load MTCNN model from ', model_path)
        self.graph = tf.Graph()
        with self.graph.as_default():
            self.sess = tf.Session(config=tf_config)
            with self.sess.as_default():
                self.pnet, self.rnet, self.onet = detect_face.create_mtcnn(self.sess, model_path=model_path)

    def detect_faces(self, image):
        with self.graph.as_default():
            with self.sess.as_default():
                boxes, points = detect_face.detect_face(image, self.minsize, self.pnet, self.rnet, self.onet, self.threshold, self.factor)
        return self._assemble_detect_face_result(boxes, points)

    @staticmethod
    def draw_face_bounding_box(image, face, color=(0,0,255), imgcopy=False):
        if imgcopy:
            image = np.copy(image)
        cv2.rectangle(image, face.bb_p1, face.bb_p2, color=color, thickness=2)
        return image

    @staticmethod
    def draw_face_points(image, face, color=(0,0,255), imgcopy=False):
        if imgcopy:
            image = np.copy(image)
        cv2.circle(image, face.nose, 3, color=color, thickness=3, lineType=8, shift=0)
        cv2.circle(image, face.left_eye, 3, color=color, thickness=3, lineType=8, shift=0)
        cv2.circle(image, face.right_eye, 3, color=color, thickness=3, lineType=8, shift=0)
        cv2.circle(image, face.mouth_left, 3, color=color, thickness=3, lineType=8, shift=0)
        cv2.circle(image, face.mouth_right, 3, color=color, thickness=3, lineType=8, shift=0)
        return image
        
    @staticmethod    
    def align_face(img, bounding_box, image_size=112, margin=5):
        """Crop a face from an image on a bounding box with some margin.
        
        Args:
            img (array): The image
            bounding_box (array): The bounding box as [p1.x, p1.y, p2.x, p2.y]
            image_size (int): Height and width of the result image
            margin (int): Margin between the bounding box and the result image

        Returns:
            array: Cropped face image    
        """
        img_size = np.asarray(img.shape)[0:2]
        bb = np.zeros(4, dtype=np.int32)
        
        
        # crop the image to the bounding box plus half
        # the margin on each side
        bb[0] = np.maximum(bounding_box[0]-margin/2, 0)
        bb[1] = np.maximum(bounding_box[1]-margin/2, 0)
        bb[2] = np.minimum(bounding_box[2]+margin/2, img_size[1])
        bb[3] = np.minimum(bounding_box[3]+margin/2, img_size[0])
        cropped = img[bb[1]:bb[3],bb[0]:bb[2],:]
        
        # resize the cropped image to the target size
        aligned = misc.imresize(cropped, (image_size, image_size), interp='bilinear')
        return aligned
    

    def _assemble_detect_face_result(self, boxes, points):
        """Assemble the result of `detect_face.detect_face()` and 
           return a list of `Face` named tuples.
        """
        faces = []
        for i in range(len(boxes)):
            confidence = boxes[i][4]
            bb_p1_x, bb_p1_y, bb_p2_x, bb_p2_y = boxes[i][0:4].astype(int)
            face_points = points[:,i].astype(int).tolist()
            x_coordinates = face_points[:5]
            y_coordinates = face_points[5:]
            face_points = list(zip(x_coordinates, y_coordinates))
            faces.append(Face((bb_p1_x, bb_p1_y), (bb_p2_x, bb_p2_y), confidence, face_points[0], face_points[1], face_points[2], face_points[3], face_points[4]))
        return faces            
