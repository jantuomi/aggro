#!/bin/bash

IMAGE=registry.digitalocean.com/jan-systems-registry/aggro:latest

set -euxo pipefail
docker build --platform linux/amd64 -t $IMAGE .
docker push $IMAGE
