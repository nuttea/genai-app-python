#!/bin/bash
# Setup Dataset Manager - Ensure all directories and volumes are ready

set -e

echo "🔧 Setting up Dataset Manager..."
echo ""

# 1. Check if assets directory exists
if [ ! -d "assets/ss5-18-images" ]; then
    echo "❌ Error: assets/ss5-18-images directory not found"
    echo "   Please create it and add your election form images"
    exit 1
fi

# Count images
IMAGE_COUNT=$(find assets/ss5-18-images -type f \( -name "*.jpg" -o -name "*.png" \) | wc -l | xargs)
echo "✅ Found $IMAGE_COUNT images in assets/ss5-18-images"

# 2. Create datasets directory
echo ""
echo "📁 Creating datasets directory..."
mkdir -p datasets/vote-extraction
chmod 755 datasets
chmod 755 datasets/vote-extraction
echo "✅ Created datasets/vote-extraction"

# 3. Check if running in Docker
if [ -f "/.dockerenv" ]; then
    echo ""
    echo "🐳 Running in Docker container"
    echo "   Volume mounts should be configured in docker-compose.yml"
else
    echo ""
    echo "💻 Running locally"
    
    # 4. Check if Docker Compose is available
    if command -v docker-compose &> /dev/null; then
        echo ""
        echo "🔄 Recreating Streamlit service with updated volumes..."
        echo "   (This is required to mount new volumes)"
        docker-compose stop streamlit-frontend
        docker-compose rm -f streamlit-frontend
        docker-compose up -d streamlit-frontend
        echo "✅ Service recreated"
        echo ""
        echo "⏳ Waiting for service to be ready..."
        sleep 3
        echo "📱 Access Dataset Manager at: http://localhost:8501"
    else
        echo ""
        echo "⚠️  Docker Compose not found"
        echo "   Run manually: streamlit run frontend/streamlit/pages/2_📊_Dataset_Manager.py"
    fi
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Open http://localhost:8501"
echo "2. Navigate to '📊 Dataset Manager' page"
echo "3. Check the '📁 Storage Paths' expander in the sidebar"
echo "4. Start annotating ground truth!"

