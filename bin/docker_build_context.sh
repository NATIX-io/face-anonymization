#!/bin/bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"/..

rm -rf ${DIR}/build/docker

mkdir -p ${DIR}/build/docker
mkdir -p ${DIR}/build/docker/resources


cp ${DIR}/Dockerfile ${DIR}/build/docker

cp ${DIR}/resources/*.py ${DIR}/build/docker/resources
cp ${DIR}/*.py ${DIR}/build/docker


cp ${DIR}/service.yaml ${DIR}/build/docker
cp ${DIR}/mtcnn/dist/mtcnn-0.0.1-py3-none-any.whl ${DIR}/build/docker
