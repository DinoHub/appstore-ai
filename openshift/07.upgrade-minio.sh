APP=minio
NAMESPACE=ai-appstore
CHART=charts/dependencies/minio
OVERRIDE=environments/development/minio-values.yaml

helm upgrade $APP -n $NAMESPACE --values=$OVERRIDE $CHART
# kubectl get pods -n $NAMESPACE
