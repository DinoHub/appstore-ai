CRD=emissary-crd
CRD_CHART=charts/dependencies/emissary-crds

APP=emissary
NAMESPACE=emissary
CHART=charts/dependencies/emissary-ingress
OVERRIDE=environments/development/emissary-values.yaml

# install crds
helm install $CRD -n $NAMESPACE $CRD_CHART

# install emissary
helm install $APP -n $NAMESPACE --values=$OVERRIDE $CHART --create-namespace
