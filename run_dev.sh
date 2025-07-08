#!/bin/bash

# Run development environment for AI Audio project
echo "Starting AI Audio development environment..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
  echo "Docker is not running. Please start Docker and try again."
  exit 1
fi

# Check if .env file exists, if not create it
if [ ! -f ".env" ]; then
  echo "Creating .env file..."
  echo "OPENAI_API_KEY=your_openai_api_key
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=aiaudio
POSTGRES_HOST=db
REDIS_HOST=redis" > .env
  echo "⚠️ Please update the OPENAI_API_KEY in the .env file with your actual API key."
  exit 1
fi

# Check if OPENAI_API_KEY is set in .env file to something other than placeholder
if grep -q "OPENAI_API_KEY=\(your_openai_api_key\|sk-your-openai-api-key\)" .env; then
  echo "⚠️ OPENAI_API_KEY is not set in .env file. Please update it with your actual API key."
  echo "You can get an API key from https://platform.openai.com/api-keys"
  echo "Then update the .env file with: OPENAI_API_KEY=your-actual-key"
  exit 1
fi

# Check if using mock key and warn user
if grep -q "OPENAI_API_KEY=sk-mock-key-for-testing-purposes-only" .env; then
  echo "⚠️ Using mock OpenAI API key. Some features may not work properly."
  echo "For full functionality, please update the .env file with your actual OpenAI API key."
fi

# Build and start the containers
echo "Building and starting containers..."
docker compose up --build -d

# Wait for services to be ready
echo "Waiting for services to be ready..."
sleep 5

# Check if services are running
echo "Checking services..."
if docker compose ps backend | grep -q "Up"; then
  echo "✅ Backend service is running"
else
  echo "❌ Backend service failed to start"
  docker compose logs backend --tail 20
fi

if docker compose ps frontend | grep -q "Up"; then
  echo "✅ Frontend service is running"
else
  echo "❌ Frontend service failed to start"
  docker compose logs frontend --tail 20
fi

if docker compose ps db | grep -q "Up"; then
  echo "✅ PostgreSQL service is running"
else
  echo "❌ PostgreSQL service failed to start"
  docker compose logs db --tail 20
fi

if docker compose ps redis | grep -q "Up"; then
  echo "✅ Redis service is running"
else
  echo "❌ Redis service failed to start"
  docker compose logs redis --tail 20
fi

if docker compose ps nginx | grep -q "Up"; then
  echo "✅ Nginx service is running"
else
  echo "❌ Nginx service failed to start"
  docker compose logs nginx --tail 20
fi

# Print access information
echo ""
echo "Access the application at: http://localhost:8080"
echo "API Documentation: http://localhost:8080/api/docs"
echo ""
echo "To view logs: docker compose logs -f"
echo "To stop: docker compose down"
