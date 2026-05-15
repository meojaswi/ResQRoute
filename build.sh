#!/bin/bash
set -e

echo "=== Building ResQRoute ==="

# 1. Install frontend dependencies and build
echo "-> Building React frontend..."
cd frontend
npm install --legacy-peer-deps
npm run build
cd ..

# 2. Install backend dependencies
echo "-> Installing Python dependencies..."
pip install -r backend/requirements.txt

echo "=== Build Complete ==="
