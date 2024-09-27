#!/bin/bash

# Check if uvicorn is installed
if ! command -v uvicorn &> /dev/null
then
    echo "uvicorn is not installed. Please install it using: pip install uvicorn"
    exit 1
fi

# Run the FastAPI application with auto-reloading
uvicorn main:app --host 0.0.0.0 --port 8000 --reload