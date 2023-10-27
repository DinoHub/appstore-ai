APP=aas-frontend
NAMESPACE=ai-appstore
CHART=charts/aas-frontend
OVERRIDE=environments/development/aas-frontend-values.yaml

helm upgrade $APP -n $NAMESPACE --values=$OVERRIDE $CHART
