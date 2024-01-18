APP=mongodb
NAMESPACE=ai-appstore
CHART=charts/dependencies/mongodb
OVERRIDE=environments/development/mongodb-values.yaml

helm upgrade $APP -n $NAMESPACE --values=$OVERRIDE $CHART
