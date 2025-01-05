# Use Node.js LTS version
FROM node:lts-alpine

# Set working directory
WORKDIR /usr/src/gui

# copy configs
COPY package*.json ./

# install nodejs dependencies
RUN npm ci

# copy
COPY . ./

# build nuxt
RUN npx nuxi build

# Expose the port the app runs on
EXPOSE 3000

ENV HOST="0"
ENV PORT=3000

# Define entrypoint
# docker will run the following script when started
ENTRYPOINT ["./entrypoint.sh"]
