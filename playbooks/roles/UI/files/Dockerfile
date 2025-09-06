FROM node:20-alpine

# Install git and create app directory
RUN apk add --no-cache git
WORKDIR /app

# Clone the repository 
RUN git clone https://github.com/yisehak-awm/annotation-tool.git . && \
    git checkout writer

# Install dependencies (including dev dependencies for build)
RUN npm ci

# Install remix/vite if they're missing from package.json
RUN npm install -g @remix-run/dev vite

# Build the application
RUN npm run build

# Expose port
EXPOSE 3000

# Start the application
CMD ["npm", "start"]