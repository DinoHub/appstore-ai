#!/bin/sh
ROOT_DIR=$(pwd)

# Replace environment variables in compiled JS files
# This is done to avoid having to rebuild the image every time the backend URL changes
echo "Configuring backend URL to ${VUE_APP_BACKEND_URL}"
echo "Configuring VUE_APP_KEYCLOAK_CLIENT_ID to ${VUE_APP_KEYCLOAK_CLIENT_ID}"
echo "Configuring VUE_APP_KEYCLOAK_URL to ${VUE_APP_KEYCLOAK_URL}"
echo "Configuring VUE_APP_KEYCLOAK_REALM to ${VUE_APP_KEYCLOAK_REALM}"
echo "Configuring VUE_APP_FRONTEND_VERSION to ${VUE_APP_FRONTEND_VERSION}"
echo "Configuring VUE_APP_BACKEND_VERSION to ${VUE_APP_BACKEND_VERSION}"

# Switch to the node user to execute sed with appropriate permissions
for file in $(find $ROOT_DIR/dist/spa/assets -name '*.js'); do
    echo "Processing $file"
    sed -i "s|VUE_APP_KEYCLOAK_CLIENT_ID|${VUE_APP_KEYCLOAK_CLIENT_ID}|g" $file
    sed -i "s|VUE_APP_KEYCLOAK_URL|${VUE_APP_KEYCLOAK_URL}|g" $file
    sed -i "s|VUE_APP_KEYCLOAK_REALM|${VUE_APP_KEYCLOAK_REALM}|g" $file
    sed -i "s|VUE_APP_BACKEND_URL|${VUE_APP_BACKEND_URL}|g" $file
    sed -i "s|VUE_APP_FRONTEND_VERSION|${VUE_APP_FRONTEND_VERSION}|g" $file
    sed -i "s|VUE_APP_BACKEND_VERSION|${VUE_APP_BACKEND_VERSION}|g" $file
done

exec "$@"
