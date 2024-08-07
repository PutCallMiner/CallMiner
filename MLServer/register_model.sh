#!/bin/bash

# Usage:
# ./register_model.sh model_name model_folder env_file        # Creates new resources, uploads model, and cleans up after execution
# ./register_model.sh model_name model_folder env_file --keep # Creates new resources, uploads model, does not clean up

# Required arguments
MODEL_NAME=$1
MODEL_FOLDER=$2
ENV_FILE=$3
KEEP_RESOURCES=$4

# Check if all required arguments are provided
if [ -z "$MODEL_NAME" ] || [ -z "$MODEL_FOLDER" ] || [ -z "$ENV_FILE" ]; then
    echo "Error: Model name, model folder, and env file must be provided."
    echo "Usage: ./register_model.sh model_name model_folder env_file [--keep]"
    exit 1
fi

# Configurable variables
IMAGE_NAME="model_deployment_${MODEL_NAME}"
CONTAINER_NAME="model_container_${MODEL_NAME}"
REGISTER_SCRIPT="$MODEL_FOLDER/register_model.py"
DOCKERFILE="Dockerfile.${MODEL_NAME}"

# Generate a Dockerfile for the model registration environment
generate_dockerfile () {
    cat > $DOCKERFILE <<EOF
FROM python:3.9-slim
WORKDIR /app
COPY $MODEL_FOLDER /app/
RUN apt-get update && apt-get install -y git
RUN pip install --no-cache-dir -r /app/requirements.txt
CMD ["python", "/app/register_model.py"]
EOF
}

# Function to build and run a new Docker container
setup_container () {
    echo "Building Docker image for $MODEL_NAME..."
    docker build -t $IMAGE_NAME -f $DOCKERFILE .
}

# Function to register the model using provided script
register_model () {
    echo "Registering model using $REGISTER_SCRIPT..."
    docker run -d --name $CONTAINER_NAME --env-file $ENV_FILE $IMAGE_NAME
}

# Function to clean up Docker resources
cleanup () {
    echo "Cleaning up Docker resources..."
    docker stop $CONTAINER_NAME
    docker rm $CONTAINER_NAME
    docker rmi $IMAGE_NAME

    if [ -f $DOCKERFILE ]; then
        rm $DOCKERFILE
    fi
}

# Main script execution
generate_dockerfile
setup_container
register_model

if [ "$KEEP_RESOURCES" != "--keep" ]; then
    cleanup
fi