#!/bin/sh
ROOT_DIR=$(pwd)

# Replace environment variables in compiled JS files
# This is done to avoid having to rebuild the image every time the backend URL changes
echo "Configuring backend URL to ${VUE_APP_BACKEND_URL}"
echo "Configuring VUE_APP_KEYCLOAK_CLIENT_ID_ENV to ${VUE_APP_KEYCLOAK_CLIENT_ID_ENV}"
echo "Configuring VUE_APP_KEYCLOAK_URL_ENV to ${VUE_APP_KEYCLOAK_URL_ENV}"
echo "Configuring VUE_APP_KEYCLOAK_REALM_ENV to ${VUE_APP_KEYCLOAK_REALM_ENV}"

# Switch to the node user to execute sed with appropriate permissions
for file in $(find $ROOT_DIR/dist/spa/assets -name '*.js'); do
    echo "Processing $file"
    sed -i "s|VUE_APP_KEYCLOAK_CLIENT_ID_ENV|${VUE_APP_KEYCLOAK_CLIENT_ID_ENV}|g" $file
    sed -i "s|VUE_APP_KEYCLOAK_URL_ENV|${VUE_APP_KEYCLOAK_URL_ENV}|g" $file
    sed -i "s|VUE_APP_KEYCLOAK_REALM_ENV|${VUE_APP_KEYCLOAK_REALM_ENV}|g" $file
    sed -i "s|VUE_APP_BACKEND_URL|${VUE_APP_BACKEND_URL}|g" $file
done

exec "$@"
