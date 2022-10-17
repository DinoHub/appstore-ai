#!/bin/sh
kubectl apply -f https://raw.githubusercontent.com/kubernetes/dashboard/v2.6.1/aio/deploy/recommended.yaml
kubectl apply -f k8s/dashboard/admin.yaml
sh k8s/dashboard/generate-token.sh
# Set up MetalLB
kubectl create namespace metallb-system
helm repo add metallb https://metallb.github.io/metallb
helm install metallb metallb/metallb -n metallb-system
kubectl wait --for=condition=Ready pod --all -n metallb-system
kubectl apply -f k8s/metallb-config.yaml -n metallb-system

# Set up KNative
kubectl apply -f https://github.com/knative/operator/releases/download/knative-v1.7.1/operator.yaml
kubectl create namespace knative-serving

# Load in images
kind load docker-image appstore-ai-back-end:latest
# Set up helm charts
helm install ai-mongodb charts/mongodb/ --values charts/mongodb/values.yaml
helm install back-end charts/ai-be/ --values charts/ai-be/values.yaml
helm install inference-engine charts/ai-ie/ --values charts/ai-be/values.yaml  --create-namespace --namespace inference-engine
