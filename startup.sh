#!/bin/bash

# Azure App Service startup script
echo "Starting TpicQ application..."

# Install Python dependencies
pip install -r requirements.txt

# Build React frontend
cd frontend
npm install
npm run build
cd ..

# Copy React build to FastAPI static directory
mkdir -p backend/static
cp -r frontend/build/* backend/static/

# Start the FastAPI server
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000
