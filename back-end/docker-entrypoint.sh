#!/bin/sh
set -e
. /venv/bin/activate
exec uvicorn src.main:app --port 8080
