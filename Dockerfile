
# Dockerfile for the Face Recognition Service

# Use an official Python runtime as a parent image
FROM continuumio/miniconda3

# Set the working directory to /app
WORKDIR /app

# Update Linux package lists
RUN apt-get update

# Install build tools (gcc etc.)
RUN apt-get install -y build-essential


# Install ops tools
RUN apt-get install -y procps vim


# Install any needed packages specified in requirements.txt
RUN conda install -c pytorch faiss-cpu
RUN conda install -c conda-forge opencv
RUN conda install -c anaconda pyyaml 
RUN conda install -c conda-forge imageio
RUN conda install -c conda-forge scipy==1.1.0
RUN conda install -c conda-forge numpy==1.15.4
RUN conda install -c conda-forge gevent
RUN conda install -c conda-forge gunicorn>=19.0
RUN conda install -c conda-forge falcon>=2.0
RUN conda install -c conda-forge tensorflow==1.14


# Copy the current directory contents into the container at /app
COPY . /app
RUN pwd

# Install MTCNN
RUN pip install mtcnn-0.0.1-py3-none-any.whl

# compile in a version label so we always can find the source in git
ARG VERSION=unspecified
LABEL aiconix.face_detection.version=$VERSION

# Make port 80 available to the world outside this container
EXPOSE 80

# Define environment variable
ENV PYTHONUNBUFFERED TRUE
ENV FACE_DETECTION_CONFIG /app/service.yaml
ENV NUM_WORKER 1

# Run Gunicorn when the container launches
CMD ["sh", "-c", "gunicorn --workers ${NUM_WORKER} --worker-class gevent --bind 0.0.0.0:80 main:app"]
