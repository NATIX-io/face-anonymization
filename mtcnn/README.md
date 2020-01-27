
# MTCNN

Multi-task Cascaded Convolutional Networks (MTCNN) is an algorithm for detection and alignment of faces on images. The algorithm 
has bin published in the paper [Joint Face Detection and Alignment using Multi-task Cascaded Convolutional Networks](https://arxiv.org/abs/1604.02878).
The official [Github repository](https://github.com/kpzhang93/MTCNN_face_detection_alignment) contains a Mathlab implementation. 

This repository contains a repackaging of the MTCNN Tensorflow implementation from the [davidsandberg/facenet](https://github.com/davidsandberg/facenet/tree/master/src/align)
repository. 

Note that the repository also contains the model itself. The model is stored in the `mtcnn/det*.npy` Numpy files.

# Install

Create a wheel distribution:

    python setup.py bdist_wheel

Install wheel distribution with pip:

    pip install dist/mtcnn-0.0.1-py3-none-any.whl

# Usage 

Align image dataset in `./data/celebs`:

	python -m mtcnn.align_dataset_mtcnn ../data/celebs ../data/celebs_mtcnn_224_5 --image_size 224 --margin 5
