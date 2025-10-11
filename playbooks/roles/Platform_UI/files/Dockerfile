# syntax=docker/dockerfile:1.4
FROM node:20-alpine

WORKDIR /app


RUN apk add --no-cache git

# Use secret during build to clone private repository
RUN --mount=type=secret,id=github_token \
    export GITHUB_TOKEN=$(cat /run/secrets/github_token) && \
    git clone https://$GITHUB_TOKEN@github.com/rejuve-bio/platform-ui.git . && \
    git checkout main


RUN npm ci && npm run build

# Start the application
CMD ["npm", "start"]
