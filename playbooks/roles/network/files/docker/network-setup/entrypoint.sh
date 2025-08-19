#!/bin/sh
# Create network if it doesn't exist
if ! docker network inspect rejuve-services-net >/dev/null 2>&1; then
    echo "🔹 Creating Docker network: rejuve-services-net"
    docker network create rejuve-services-net
else
    echo "ℹ️ Network rejuve-services-net already exists"
fi

# Connect atomspace-api
if docker inspect atomspace-api >/dev/null 2>&1; then
    echo "🔹 Connecting atomspace-api to rejuve-services-net"
    docker network connect rejuve-services-net atomspace-api 2>/dev/null || echo "ℹ️ atomspace-api already connected"
else
    echo "⚠️ atomspace-api container not found"
fi

# Connect annotation_annotation_service_1
if docker inspect annotation_annotation_service_1 >/dev/null 2>&1; then
    echo "🔹 Connecting annotation_annotation_service_1 to rejuve-services-net"
    docker network connect rejuve-services-net annotation_annotation_service_1 2>/dev/null || echo "ℹ️ annotation container already connected"
else
    echo "⚠️ annotation_annotation_service_1 container not found"
fi

echo "✅ Network setup complete!"
