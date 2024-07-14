#!/bin/bash

IMAGE=registry.jan.systems/aggro:latest

set -euxo pipefail
docker build --progress plain --platform linux/amd64 -t $IMAGE .
docker push $IMAGE
