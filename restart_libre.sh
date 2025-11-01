#!/bin/bash

# Name of the container
CONTAINER_NAME="libretranslate_local"
PORT=5600
IMAGE="libretranslate/libretranslate:latest"

echo "Stopping any existing containers using port $PORT..."
docker ps -q --filter "publish=$PORT" | xargs -r docker rm -f
docker rm -f $CONTAINER_NAME 2>/dev/null || true

echo "Pulling latest LibreTranslate image from Docker Hub..."
docker pull $IMAGE

echo "Starting new LibreTranslate container on ARM64..."
docker run -d --platform linux/arm64 --name $CONTAINER_NAME -p $PORT:5000 $IMAGE

echo "Waiting a few seconds for LibreTranslate to start..."
sleep 5

echo "Showing container logs:"
docker logs -f $CONTAINER_NAME

