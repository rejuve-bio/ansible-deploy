#!/bin/sh

# Create network if it doesn't exist
if ! docker network inspect rejuve-services-net >/dev/null 2>&1; then
    echo "🔹 Creating Docker network: rejuve-services-net"
    docker network create rejuve-services-net
else
    echo "ℹ️ Network rejuve-services-net already exists"
fi

# Connect atomspace-api
for name in atomspace-api atomspace_api; do
    if docker inspect "$name" >/dev/null 2>&1; then
        echo "🔹 Connecting $name to rejuve-services-net"
        docker network connect rejuve-services-net "$name" 2>/dev/null || echo "ℹ️ $name already connected"
        break
    fi
done

# Connect annotation_annotation_service_1 
for name in annotation_annotation_service_1 annotation-annotation-service-1; do
    if docker inspect "$name" >/dev/null 2>&1; then
        echo "🔹 Connecting $name to rejuve-services-net"
        docker network connect rejuve-services-net "$name" 2>/dev/null || echo "ℹ️ annotation container already connected"
        break
    fi
done

# Connect annotation_redis_1 
for name in annotation_redis_1 annotation-redis-1; do
    if docker inspect "$name" >/dev/null 2>&1; then
        echo "🔹 Connecting $name to rejuve-services-net"
        docker network connect rejuve-services-net "$name" 2>/dev/null || echo "ℹ️ $name already connected"
        break
    fi
done

# Connect annotation_caddy_1 
for name in annotation_caddy_1 annotation-caddy-1; do
    if docker inspect "$name" >/dev/null 2>&1; then
        echo "🔹 Connecting $name to rejuve-services-net"
        docker network connect rejuve-services-net "$name" 2>/dev/null || echo "ℹ️ $name already connected"
        break
    fi
done

# Connect annotation_mongodb_1 
for name in annotation_mongodb_1 annotation-mongodb-1; do
    if docker inspect "$name" >/dev/null 2>&1; then
        echo "🔹 Connecting $name to rejuve-services-net"
        docker network connect rejuve-services-net "$name" 2>/dev/null || echo "ℹ️ $name already connected"
        break
    fi
done

# Connect hugegraph-atomspace 
for name in hugegraph-atomspace hugegraph_atomspace; do
    if docker inspect "$name" >/dev/null 2>&1; then
        echo "🔹 Connecting $name to rejuve-services-net"
        docker network connect rejuve-services-net "$name" 2>/dev/null || echo "ℹ️ $name already connected"
        break
    fi
done

# Connect neo4j-atomspace 
for name in neo4j-atomspace neo4j_atomspace; do
    if docker inspect "$name" >/dev/null 2>&1; then
        echo "🔹 Connecting $name to rejuve-services-net"
        docker network connect rejuve-services-net "$name" 2>/dev/null || echo "ℹ️ $name already connected"
        break
    fi
done

# Connect mork_container 
for name in mork_container mork-container; do
    if docker inspect "$name" >/dev/null 2>&1; then
        echo "🔹 Connecting $name to rejuve-services-net"
        docker network connect rejuve-services-net "$name" 2>/dev/null || echo "ℹ️ $name already connected"
        break
    fi
done

# Connect ai-assistant-assistant-1 
for name in ai-assistant-assistant-1 ai_assistant_assistant_1; do
    if docker inspect "$name" >/dev/null 2>&1; then
        echo "🔹 Connecting $name to rejuve-services-net"
        docker network connect rejuve-services-net "$name" 2>/dev/null || echo "ℹ️ $name already connected"
        break
    fi
done

# Connect ai-assistant-qdrant-1 
for name in ai-assistant-qdrant-1 ai_assistant_qdrant_1; do
    if docker inspect "$name" >/dev/null 2>&1; then
        echo "🔹 Connecting $name to rejuve-services-net"
        docker network connect rejuve-services-net "$name" 2>/dev/null || echo "ℹ️ $name already connected"
        break
    fi
done

# Connect ai-assistant-redis-1 
for name in ai-assistant-redis-1 ai_assistant_redis_1; do
    if docker inspect "$name" >/dev/null 2>&1; then
        echo "🔹 Connecting $name to rejuve-services-net"
        docker network connect rejuve-services-net "$name" 2>/dev/null || echo "ℹ️ $name already connected"
        break
    fi
done

# Connect authentication-service-web-1
for name in authentication-service-web-1 authentication_service_web_1; do
    if docker inspect "$name" >/dev/null 2>&1; then
        echo "🔹 Connecting $name to rejuve-services-net"
        docker network connect rejuve-services-net "$name" 2>/dev/null || echo "ℹ️ $name already connected"
        break
    fi
done

# Connect authentication-service-db-1
for name in authentication-service-db-1 authentication_service_db_1; do
    if docker inspect "$name" >/dev/null 2>&1; then
        echo "🔹 Connecting $name to rejuve-services-net"
        docker network connect rejuve-services-net "$name" 2>/dev/null || echo "ℹ️ $name already connected"
        break
    fi
done

# Connect ui container
for name in ui ui-1; do
    if docker inspect "$name" >/dev/null 2>&1; then
        echo "🔹 Connecting $name to rejuve-services-net"
        docker network connect rejuve-services-net "$name" 2>/dev/null || echo "ℹ️ $name already connected"
        break
    fi
done

# Connect hypothesis-ui container
for name in hypothesis-ui hypothesis_ui; do
    if docker inspect "$name" >/dev/null 2>&1; then
        echo "🔹 Connecting $name to rejuve-services-net"
        docker network connect rejuve-services-net "$name" 2>/dev/null || echo "ℹ️ $name already connected"
        break
    fi
done

echo "✅ Network setup complete!"