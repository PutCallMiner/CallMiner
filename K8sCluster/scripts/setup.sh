#!/bin/bash

# HashiCorp Cloud Platform (HCP) Profile setup
echo "Starting HashiCorp Cloud Platform (HCP) Profile setup..."

echo "Logging into HCP..."
hcp auth login

echo "Initializing HCP profile with Vault secrets..."
hcp profile init --vault-secrets

echo "Fetching Organization ID and Project ID from HCP profile..."
export HCP_ORG_ID=$(hcp profile display --format=json | jq -r .OrganizationID)
export HCP_PROJECT_ID=$(hcp profile display --format=json | jq -r .ProjectID)
export APP_NAME=$(hcp profile display --format=json | jq -r .VaultSecrets.AppName)
echo "HCP Profile setup complete."

# HashiCorp Helm Repository setup
echo "Setting up HashiCorp Helm Repository..."
helm repo add hashicorp https://helm.releases.hashicorp.com
echo "Installing Vault Secrets Operator using Helm..."
helm install vault-secrets-operator hashicorp/vault-secrets-operator \
     --namespace vault-secrets-operator-system \
     --create-namespace
echo "Helm Repository setup complete."

# HashiCorp Vault Secret WebApplication setup
echo "Setting up HashiCorp Vault Secret WebApplication..."
kubectl create secret generic vso-callminer-sp \
    --namespace default \
    --from-literal=clientID=$HCP_CLIENT_ID \
    --from-literal=clientSecret=$HCP_CLIENT_SECRET
echo "Creating secrets from configuration files..."
envsubst < K8sCluster/configs/SecretsManager/callminer-secrets-app.yaml | kubectl create -f -
envsubst < K8sCluster/configs/SecretsManager/vso-HCPAuth.yaml | kubectl create -f -
echo "Vault Secret WebApplication setup complete."

# MLFlow server setup
echo "Setting up MLFlow server..."
kubectl apply -f K8sCluster/configs/MLFlowServer/dbdata-pvc.yaml
kubectl apply -f K8sCluster/configs/MLFlowServer/postgres-deployment.yaml
kubectl apply -f K8sCluster/configs/MLFlowServer/mlflow-deployment.yaml
kubectl apply -f K8sCluster/configs/MLFlowServer/nginx-config.yaml
kubectl apply -f K8sCluster/configs/MLFlowServer/nginx-deployment.yaml
echo "MLFlow server setup complete."

# MLServer setup
echo "Building and deploying MLServer models..."
docker build -t callminerput/ner-model:v1.0 -f MLServer/Models/NER/Dockerfile MLServer/Models/NER
docker build -t callminerput/gpt-summarizer-model:v1.0 -f MLServer/Models/gpt_summarizer/Dockerfile MLServer/Models/gpt_summarizer
docker build -t callminerput/asr-model:v1.0 -f MLServer/Models/ASR/Dockerfile MLServer/Models/ASR

kubectl apply -f K8sCluster/configs/MLServer/ner-deployment.yaml
kubectl apply -f K8sCluster/configs/MLServer/gpt-summarizer-deployment.yaml
kubectl apply -f K8sCluster/configs/MLServer/asr-deployment.yaml
echo "MLServer models deployment complete."

# BE setup
echo "Building and deploying BE server..."
docker build -t callminerput/fastapi-app:v1.0 -f BEServer/Dockerfile BEServer

kubectl apply -f K8sCluster/configs/BEServer/mongodb-deployment.yaml
kubectl apply -f K8sCluster/configs/BEServer/fastapi-app-deployment.yaml
echo "BE server deployment complete."

echo "All setup processes are complete."