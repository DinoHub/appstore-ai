#!/bin/sh
# create registry container unless it already exists
reg_name='kind-registry'
reg_port='5001'
if [ "$(docker inspect -f '{{.State.Running}}' "${reg_name}" 2>/dev/null || true)" != 'true' ]; then
  docker run \
    -d --restart=always -p "127.0.0.1:${reg_port}:5000" --name "${reg_name}" \
    registry:2
fi
kind create cluster --config=k8s/dev/kind.yaml

if [ "$(docker inspect -f='{{json .NetworkSettings.Networks.kind}}' "${reg_name}")" = 'null' ]; then
  docker network connect "kind" "${reg_name}"
fi

# Currently registry is broken
# kubectl apply -f k8s/registry.yaml

kubectl apply -f https://raw.githubusercontent.com/kubernetes/dashboard/v2.6.1/aio/deploy/recommended.yaml
kubectl apply -f k8s/dev/dashboard/admin.yaml
sh k8s/dev/dashboard/generate-token.sh
# Set up MetalLB
kubectl create namespace metallb-system
helm repo add metallb https://metallb.github.io/metallb
helm install metallb metallb/metallb -n metallb-system
kubectl wait --for=condition=Ready pod --all -n metallb-system
sleep 20
kubectl apply -f k8s/dev/metallb-config.yaml -n metallb-system

# Setup NGINX Ingress
# Note the below is Kind specific for now
# helm repo add nginx-stable https://helm.nginx.com/stable
# helm repo update
# helm install my-release nginx-stable/nginx-ingress
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/main/deploy/static/provider/kind/deploy.yaml

# Set up KNative
kubectl apply -f https://github.com/knative/operator/releases/download/knative-v1.8.1/operator.yaml
# kubectl create namespace knative-serving

# Load in images
kind load docker-image aas-backend:1.0.0
kind load docker-image aas-frontend:1.0.0
# Set up helm charts
helm install appstore k8s/charts/appstore
# helm install ai-mongodb charts/mongodb/ --values charts/mongodb/values.yaml
# helm install ai-backend charts/ai-be/ --values charts/ai-be/values.yaml
# helm install ai-frontend charts/ai-fe/ --values charts/ai-fe/values.yaml
# helm install inference-engine charts/ai-ie/ --values charts/ai-be/values.yaml  --create-namespace --namespace inference-engine
