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

# Connect annotation_redis_1
if docker inspect annotation_redis_1 >/dev/null 2>&1; then
    echo "🔹 Connecting annotation_redis_1 to rejuve-services-net"
    docker network connect rejuve-services-net annotation_redis_1 2>/dev/null || echo "ℹ️ annotation_redis_1 already connected"
else
    echo "⚠️ annotation_redis_1 container not found"
fi

# Connect annotation_caddy_1
if docker inspect annotation_caddy_1 >/dev/null 2>&1; then
    echo "🔹 Connecting annotation_caddy_1 to rejuve-services-net"
    docker network connect rejuve-services-net annotation_caddy_1 2>/dev/null || echo "ℹ️ annotation_caddy_1 already connected"
else
    echo "⚠️ annotation_caddy_1 container not found"
fi

# Connect annotation_mongodb_1
if docker inspect annotation_mongodb_1 >/dev/null 2>&1; then
    echo "🔹 Connecting annotation_mongodb_1 to rejuve-services-net"
    docker network connect rejuve-services-net annotation_mongodb_1 2>/dev/null || echo "ℹ️ annotation_mongodb_1 already connected"
else
    echo "⚠️ annotation_mongodb_1 container not found"
fi

# Connect hugegraph-atomspace
if docker inspect hugegraph-atomspace >/dev/null 2>&1; then
    echo "🔹 Connecting hugegraph-atomspace to rejuve-services-net"
    docker network connect rejuve-services-net hugegraph-atomspace 2>/dev/null || echo "ℹ️ hugegraph-atomspace already connected"
else
    echo "⚠️ hugegraph-atomspace container not found"
fi

# Connect neo4j-atomspace
if docker inspect neo4j-atomspace >/dev/null 2>&1; then
    echo "🔹 Connecting neo4j-atomspace to rejuve-services-net"
    docker network connect rejuve-services-net neo4j-atomspace 2>/dev/null || echo "ℹ️ neo4j-atomspace already connected"
else
    echo "⚠️ neo4j-atomspace container not found"
fi

# Connect mork_container
if docker inspect mork_container >/dev/null 2>&1; then
    echo "🔹 Connecting mork_container to rejuve-services-net"
    docker network connect rejuve-services-net mork_container 2>/dev/null || echo "ℹ️ mork_container already connected"
else
    echo "⚠️ mork_container container not found"
fi

# AI Assistant containers
# Connect ai-assistant-assistant-1
if docker inspect ai-assistant-assistant-1 >/dev/null 2>&1; then
    echo "🔹 Connecting ai-assistant-assistant-1 to rejuve-services-net"
    docker network connect rejuve-services-net ai-assistant-assistant-1 2>/dev/null || echo "ℹ️ ai-assistant-assistant-1 already connected"
else
    echo "⚠️ ai-assistant-assistant-1 container not found"
fi

# Connect ai-assistant-qdrant-1
if docker inspect ai-assistant-qdrant-1 >/dev/null 2>&1; then
    echo "🔹 Connecting ai-assistant-qdrant-1 to rejuve-services-net"
    docker network connect rejuve-services-net ai-assistant-qdrant-1 2>/dev/null || echo "ℹ️ ai-assistant-qdrant-1 already connected"
else
    echo "⚠️ ai-assistant-qdrant-1 container not found"
fi

# Connect ai-assistant-redis-1
if docker inspect ai-assistant-redis-1 >/dev/null 2>&1; then
    echo "🔹 Connecting ai-assistant-redis-1 to rejuve-services-net"
    docker network connect rejuve-services-net ai-assistant-redis-1 2>/dev/null || echo "ℹ️ ai-assistant-redis-1 already connected"
else
    echo "⚠️ ai-assistant-redis-1 container not found"
fi

echo "✅ Network setup complete!"