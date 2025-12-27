#!/bin/bash
# Setup script for Streamlit frontend

set -e

echo "🚀 Setting up Streamlit frontend..."

# Create .streamlit directory if it doesn't exist
mkdir -p .streamlit

# Check if secrets.toml exists
if [ ! -f .streamlit/secrets.toml ]; then
    echo "📝 Creating secrets.toml from example..."
    cp .streamlit/secrets.toml.example .streamlit/secrets.toml
    echo "✅ Created .streamlit/secrets.toml"
    echo ""
    echo "⚠️  Please edit .streamlit/secrets.toml and update:"
    echo "   - API_BASE_URL (if not using default)"
else
    echo "✅ secrets.toml already exists"
fi

# Install dependencies if in virtual environment or if requested
if [ -n "$VIRTUAL_ENV" ] || [ "$1" = "--install" ]; then
    echo "📦 Installing dependencies..."
    pip install -r requirements.txt
    echo "✅ Dependencies installed"
fi

echo ""
echo "🎉 Setup complete!"
echo ""
echo "To run the application:"
echo "  streamlit run app.py"
echo ""
echo "Or with Docker:"
echo "  cd ../.. && docker-compose up streamlit-frontend"
echo ""

