FROM node:18-alpine

WORKDIR /app

# Install dependencies
COPY frontend/package.json frontend/package-lock.json* ./
RUN npm install --legacy-peer-deps

# Copy source code
COPY frontend/ .

# Start development server
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
