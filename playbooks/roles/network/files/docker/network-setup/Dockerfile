# Use lightweight Alpine with Docker CLI
FROM docker:24.0.6-cli

# Allow running Docker commands inside container
VOLUME /var/run/docker.sock:/var/run/docker.sock

# Set working directory
WORKDIR /app

# Add an entrypoint script
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Run the entrypoint
ENTRYPOINT ["/app/entrypoint.sh"]
