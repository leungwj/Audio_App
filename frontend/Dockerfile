FROM node:18-alpine AS base

WORKDIR /app

COPY package.json ./

RUN npm install

FROM base AS runner

COPY ./ ./

ARG API_SERVER
ENV API_SERVER=${API_SERVER}

EXPOSE 3000
CMD [ "npm", "run", "dev" ]