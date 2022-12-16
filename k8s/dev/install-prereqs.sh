#!/bin/sh
kubectl apply -f https://raw.githubusercontent.com/kubernetes/dashboard/v2.6.1/aio/deploy/recommended.yaml
kubectl apply -f dashboard/admin.yaml
sh dashboard/generate-token.sh
# Set up MetalLB
kubectl create namespace metallb-system
helm repo add metallb https://metallb.github.io/metallb
helm repo add bitnami https://charts.bitnami.com/bitnami
helm install metallb metallb/metallb -n metallb-system
kubectl wait --for=condition=Ready pod --all -n metallb-system
kubectl apply -f metallb-config.yaml -n metallb-system
# 
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/main/deploy/static/provider/kind/deploy.yaml
# Set up KNative
kubectl apply -f https://github.com/knative/operator/releases/download/knative-v1.8.1/operator.yaml
kubectl create namespace knative-serving
kubectl create namespace inference-engine
# kubectl apply -f knative/knative-serving.yaml

kind load docker-image aas-backend:latest
kind load docker-image aas-frontend:latest
# Set up Magic DNS
# kubectl apply -f https://github.com/knative/serving/releases/download/knative-v1.7.2/serving-default-domain.yaml
# Make KNative Services Private (only allow within cluster call)
# kubectl apply -f knative/domain.yaml

# Create namespace for engines
# kubectl create namespace ie
