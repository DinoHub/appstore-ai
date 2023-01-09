#!/bin/sh
ROOT_DIR=$(pwd)

# Replace environment variables in compiled JS files
# This is done to avoid having to rebuild the image every time the backend URL changes
echo "Configuring backend URL to ${VUE_APP_BACKEND_URL}"
for file in $(find $ROOT_DIR/dist/spa/assets -name '*.js'); do
    echo "Processing $file"
    sed -i "s|VUE_APP_BACKEND_URL|${VUE_APP_BACKEND_URL}|g" $file
done

exec "$@"
