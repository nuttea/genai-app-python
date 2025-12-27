#!/bin/bash
# Check the status of all services

echo "🔍 Checking GenAI Platform Services..."
echo ""

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

echo "✅ Docker is running"
echo ""

# Check if docker-compose is available
if ! command -v docker-compose &> /dev/null; then
    echo "❌ docker-compose is not installed"
    exit 1
fi

echo "📊 Service Status:"
echo "=================="
docker-compose ps
echo ""

# Check FastAPI backend
echo "🔍 Checking FastAPI Backend..."
if curl -f -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ FastAPI backend is healthy (http://localhost:8000)"
    echo "   Response: $(curl -s http://localhost:8000/health)"
else
    echo "❌ FastAPI backend is not responding"
    echo "   Logs:"
    docker-compose logs --tail=20 fastapi-backend
fi
echo ""

# Check Streamlit frontend
echo "🔍 Checking Streamlit Frontend..."
if curl -f -s http://localhost:8501/_stcore/health > /dev/null 2>&1; then
    echo "✅ Streamlit frontend is healthy (http://localhost:8501)"
else
    echo "❌ Streamlit frontend is not responding"
    echo "   Logs:"
    docker-compose logs --tail=20 streamlit-frontend
fi
echo ""

# Test backend connectivity from streamlit container
echo "🔍 Testing Backend Connectivity from Streamlit..."
if docker-compose exec -T streamlit-frontend curl -f -s http://fastapi-backend:8000/health > /dev/null 2>&1; then
    echo "✅ Streamlit can reach FastAPI backend"
else
    echo "❌ Streamlit cannot reach FastAPI backend"
    echo "   This is likely the issue!"
    echo ""
    echo "   Try these solutions:"
    echo "   1. Restart services: docker-compose restart"
    echo "   2. Rebuild: docker-compose up -d --build"
    echo "   3. Full reset: docker-compose down && docker-compose up -d"
fi
echo ""

# Check network
echo "🔍 Checking Docker Network..."
docker network inspect genai-app-python_genai-network > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "✅ Docker network 'genai-network' exists"
    echo "   Containers in network:"
    docker network inspect genai-app-python_genai-network --format '{{range .Containers}}  - {{.Name}}{{"\n"}}{{end}}'
else
    echo "❌ Docker network 'genai-network' not found"
fi
echo ""

echo "📝 Summary:"
echo "==========="
echo "FastAPI Backend:  http://localhost:8000"
echo "API Docs:         http://localhost:8000/docs"
echo "Streamlit UI:     http://localhost:8501"
echo ""
echo "To view logs:"
echo "  docker-compose logs -f fastapi-backend"
echo "  docker-compose logs -f streamlit-frontend"
