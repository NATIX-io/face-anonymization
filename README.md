# Face Recognition Service

This is an HTTP service that provides functions to detect faces in images. It includes:

* [Face Detection Resource](resources/FaceDetectionResource.py)

For understanding the APIs and resources please refer to the folder [resources](resources) or the explanation [here](resources/README.md)

## Folders

* [bin](bin): executable file creating the necessary folders and copying models before building the docker
* [mtcnn](mtcc): Tensorflow model for detecting faces
* [resources](resources): resources for different APIs


## Docker

In this part we explain how to build and run the docker.

### Build a Docker container

Simply use

```bash
./package-docker.sh
```

or if you want to export the build container you can use

```bash
./package-docker.sh --save-local
```

it will then be saved with the generated version number next to the
repository folder.

### Run Docker container

Just CPU:

```bash
docker run -d --name face_detection -p 8000:80 \
    -v $(pwd)/data:/data face_detection
```

For GPU support, first you need to install tensorflow-gpu and faiss-gpu and then build the docker with:

```bash
docker run -d --name face_detection -p 8000:80 \
    --runtime=nvidia -v $(pwd)/data:/data face_detection
```

After starting the container the service should listen on 127.0.0.1 port 8000.

The number of Gunicorn workers can be configured by setting the `NUM_WORKER` environment variable when running the container, e.g. `-e NUM_WORKER=2`.

### Start service manually

For debugging it can be helpful to start the service manually. Run the container but overwrite the entrypoint with a Bash shell (you need to modify the version manually instead of 0.0.1):

```bash
docker run -it -p 8000:80 --entrypoint=/bin/bash face_detection_service:0.0.1
```

This starts the container and opens a shell but does not start the service. Start the service manually:

```bash
cd /app
gunicorn --workers 1 --worker-class gevent --bind 0.0.0.0:80 main:app
```

### Start service without Docker

```bash
FACE_DETECTION_CONFIG=service-dev.yaml gunicorn --workers 1 --worker-class gevent --bind 0.0.0.0:8000 main:app
```

### Login to the Docker container

Lookup container ID:

```bash
    docker container ps
    CONTAINER ID        IMAGE               COMMAND             CREATED             STATUS              PORTS                  NAMES
    7932a3814453        friendlyhello       "python app.py"     16 seconds ago      Up 15 seconds       0.0.0.0:4000->80/tcp   musing_robinson
```

Open a shell on the container:

```bash
docker exec -it c1de50a17e8d /bin/bash
```

### Cleanup

Remove all containers and images:

```bash
docker rm $(docker ps -a -q)
docker rmi $(docker images -q)
```

## Start service locally

The service requires a YAML config file. The config file path can be specified by setting an environment variable `FACE_RECOGNITION_SERVICE_CONFIG`. The default is to load `service.yaml` from the current directory.

Start service locally:

```bash
PYTHONUNBUFFERED=TRUE FACE_DETECTION_CONFIG=./service.yaml gunicorn --reload --workers 1 --worker-class gevent --bind 0.0.0.0:8080 main:app
```

## Releasing a version

### Build and push container to registry

```bash
git tag -a v#.##.#
./package-docker --push
```

### Update running service

Just an example host we currently use:

```bash
ssh ubuntu@130.61.93.153
```

Then on the host:

```bash
docker stop face-recognition-services
docker pull fra.ocir.io/aiconix/data-science/face_detection
docker run -d --restart=always \
    -h face-recognition-services \
    --name face_detection \
    -p 8000:80 -v $(pwd)/data:/data \
    fra.ocir.io/aiconix/data-science/face_detection
```

## Gunicorn

The Gunicorn configuration is described in [Gunicorn settings](http://docs.gunicorn.org/en/stable/settings.html).

The most important Gunicorn configuration parameters are:

* `--reload` - Restart workers when code changes. This should only be used during development
* `--workers` - The number of worker processes for handling requests
* `--worker-class` - The type of workers to use
* `--bind` - The socket and port to bind
* `--access-logfile` - Path of the access log file
* `--error-logfile` -  Path of the error log file
* `--daemon` - Daemonize the Gunicorn process
