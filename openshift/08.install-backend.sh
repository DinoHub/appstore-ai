APP=aas-backend
NAMESPACE=ai-appstore
CHART=charts/aas-backend
OVERRIDE=environments/development/aas-backend-values.yaml

helm install $APP -n $NAMESPACE --values=$OVERRIDE $CHART
