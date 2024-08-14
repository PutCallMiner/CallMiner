#!/bin/bash

# Secrets setup
kubectl create secret generic callminer-secrets --from-env-file=K8sCluster/configs/.env

# Set up Docker environment for Kind
echo "Configuring Docker to use local Docker daemon (Kind uses the host's Docker daemon)..."

# Build the MLFlow Docker image
echo "Building the MLFlow Docker image..."
docker build -t mlflow:v1.0 -f MLFlowServer/MLFlow/Dockerfile MLFlowServer/MLFlow/

# Load the Docker image into Kind cluster
echo "Loading Docker image into the Kind cluster..."
kind load docker-image mlflow:v1.0

# Apply Kubernetes configurations for MLFlow server
echo "Applying Kubernetes configurations for MLFlow server..."
kubectl apply -f K8sCluster/configs/MLFlowServer/dbdata-pvc.yaml
kubectl apply -f K8sCluster/configs/MLFlowServer/postgres-deployment.yaml
kubectl apply -f K8sCluster/configs/MLFlowServer/mlflow-deployment.yaml
kubectl apply -f K8sCluster/configs/MLFlowServer/nginx-config.yaml
kubectl apply -f K8sCluster/configs/MLFlowServer/nginx-deployment.yaml

echo "MLFlow server setup complete."

# MLServer setup
echo "Building and deploying MLServer models..."

# Build Docker images for MLServer models
docker build -t ner-model:v1.0 -f MLServer/Models/NER/Dockerfile MLServer/Models/NER
docker build -t gpt-summarizer-model:v1.0 -f MLServer/Models/gpt_summarizer/Dockerfile MLServer/Models/gpt_summarizer
docker build -t asr-model:v1.0 -f MLServer/Models/ASR/Dockerfile MLServer/Models/ASR

# Load the Docker images into Kind cluster
echo "Loading Docker images into the Kind cluster..."
kind load docker-image ner-model:v1.0
kind load docker-image gpt-summarizer-model:v1.0
kind load docker-image asr-model:v1.0

# Apply Kubernetes configurations for MLServer models
kubectl apply -f K8sCluster/configs/MLServer/ner-deployment.yaml
kubectl apply -f K8sCluster/configs/MLServer/gpt-summarizer-deployment.yaml
kubectl apply -f K8sCluster/configs/MLServer/asr-deployment.yaml

echo "MLServer models deployment complete."

# BE setup
echo "Building and deploying BE server..."

# Build Docker image for BE server
docker build -t fastapi-app:v1.0 -f BEServer/Dockerfile BEServer

# Load the Docker image into Kind cluster
echo "Loading Docker image into the Kind cluster..."
kind load docker-image fastapi-app:v1.0

# Apply Kubernetes configurations for BE server
kubectl apply -f K8sCluster/configs/BEServer/mongodb-deployment.yaml
kubectl apply -f K8sCluster/configs/BEServer/fastapi-app-deployment.yaml

echo "BE server deployment complete."

echo "All setup processes are complete."
