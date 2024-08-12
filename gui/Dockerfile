
# Use Node.js LTS version
FROM node:lts-alpine

# Set working directory
WORKDIR /usr/src/gui

# Copy package.json and package-lock.json
COPY package.json package-lock.json ./

RUN npm install --global typescript esrun

# Install dependencies
RUN npm install

# Expose the port the app runs on
EXPOSE 3000

# Define entrypoint
# docker will run the following script when started
ENTRYPOINT ["./entrypoint.sh"]
