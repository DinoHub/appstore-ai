#!/bin/sh
. venv/bin/activate && python -m uvicorn src.main:app --port 8080