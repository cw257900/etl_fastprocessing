#!/bin/bash

echo "Setting up ETL Fast Processing System..."

mkdir -p backend/uploads

echo "Setting up backend..."
cd backend

cp .env.example .env

if command -v poetry &> /dev/null; then
    echo "Using Poetry for Python dependencies..."
    poetry install
else
    echo "Using pip for Python dependencies..."
    pip install -r requirements.txt
fi

cd ..

echo "Setting up frontend..."
cd frontend

if command -v pnpm &> /dev/null; then
    echo "Using pnpm for Node dependencies..."
    pnpm install
elif command -v yarn &> /dev/null; then
    echo "Using yarn for Node dependencies..."
    yarn install
else
    echo "Using npm for Node dependencies..."
    npm install
fi

cd ..

echo "Setup complete!"
echo ""
echo "To start the development servers:"
echo "1. Start PostgreSQL and Redis (or use docker-compose up db redis)"
echo "2. Backend: cd backend && poetry run uvicorn app.main:app --reload"
echo "3. Frontend: cd frontend && npm start"
echo ""
echo "Or use Docker Compose: docker-compose up"
