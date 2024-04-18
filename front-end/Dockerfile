FROM node:lts as build-stage
WORKDIR /app
COPY package-lock.json package.json ./
RUN npm install -g @quasar/cli
RUN npm ci
COPY . .
RUN quasar build


# FROM nginx:stable as production-stage
# COPY --from=build-stage /app/dist /user/share/nginx/html
EXPOSE 8081
# CMD ["nginx", "-g", "daemon off;"]
RUN chmod -R 770 /app/dist/spa/assets
ENTRYPOINT [ "sh", "entrypoint.sh" ]
CMD ["quasar", "serve", "dist/spa", "-p", "8081", "--history"]
