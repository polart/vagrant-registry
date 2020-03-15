FROM node:13.8.0-alpine AS base

ENV NODE_ENV=development
ENV HOST=0.0.0.0
ENV PORT=3000

EXPOSE 3000

WORKDIR /project

COPY package.json yarn.lock ./

CMD ["yarn", "start"]
