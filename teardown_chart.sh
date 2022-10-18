#! /bin/bash

echo "Chart Teardown:"
echo "  be - Backend"
echo "  db - MongoDB"
echo -n "Enter chart: "
read mode

if [ "$mode" = "be" ]; then
    helm uninstall ai-backend
elif  [ "$mode" = "db" ]; then
    helm uninstall ai-mongo
else
    echo "ModeError"
fi