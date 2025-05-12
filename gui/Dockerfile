# Use Node.js LTS version
FROM node:lts-alpine

# Set working directory
WORKDIR /usr/src/gui

# copy configs
COPY package*.json ./
COPY patches ./patches

# install nodejs dependencies
RUN npm ci

# copy app
COPY app ./app
COPY public ./public
COPY server ./server
COPY types ./types

COPY entrypoint.sh ./entrypoint.sh

COPY tsconfig.json ./tsconfig.json
COPY nuxt.config.ts ./nuxt.config.ts
COPY tailwind.config.js ./tailwind.config.js


# build nuxt
RUN npx nuxi prepare
RUN npx nuxi build

# Expose the port the app runs on
EXPOSE 3000

ENV HOST="0"
ENV PORT=3000

# Define entrypoint
# docker will run the following script when started
ENTRYPOINT ["./entrypoint.sh"]
