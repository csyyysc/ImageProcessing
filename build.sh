#!/bin/bash

# Build script for latest Docker image
# This script builds the Docker image and shows size comparison

echo "🚀 Building latest Docker image..."

# Build the latest image
sudo docker build -t ghcr.io/csyyysc/image-processing --target production .

if [ $? -eq 0 ]; then
    echo "✅ Build successful!"
    
    echo "📊 Image size information:"
    docker images | grep image-processing
    
    echo ""
    echo "🔍 Detailed size breakdown:"
    docker image inspect image-processing:latest --format='Size: {{.Size}} bytes ({{div .Size 1048576}} MB)'
    
    echo ""
    echo "🧹 Layer information:"
    docker history image-processing:latest --format "table {{.CreatedBy}}\t{{.Size}}" | head -10

else
    echo "❌ Build failed!"
    exit 1
fi
