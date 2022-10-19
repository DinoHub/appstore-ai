#! /bin/bash
# script for launching helm charts individually
# used mainly for testing and development purposes

echo "Chart Deployment Modes:"
echo "  be - Backend"
echo "  db - MongoDB"
echo -n "Enter launch mode: "
read mode

if [ "$mode" = "be" ]; then
    helm install ai-backend charts/ai-be/ --values charts/ai-be/values.yaml
elif  [ "$mode" = "db" ]; then
    helm install ai-mongo charts/mongodb/ --values charts/mongodb/values.yaml
else
    echo "ModeError"
fi