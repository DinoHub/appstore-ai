#! /bin/bash
# script for tearing down helm charts individually
# used mainly for testing and development purposes

echo "Chart Teardown:"
echo "  be - Backend"
echo "  db - MongoDB"
echo "  ie - Inference Engine Utilities"
echo -n "Enter chart: "
read mode

if [ "$mode" = "be" ]; then
    helm uninstall ai-backend
elif  [ "$mode" = "db" ]; then
    helm uninstall ai-mongo
elif  [ "$mode" = "ie" ]; then
    helm uninstall ai-ie
else
    echo "ModeError"
fi