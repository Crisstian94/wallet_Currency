# Etapa 1: Build
FROM node:22-alpine as build-stage
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

# Etapa 2: Producción
FROM nginx:stable-alpine as production-stage
# Copiamos los archivos generados por Vite a la ruta de Nginx
COPY --from=build-stage /app/dist /usr/share/nginx/html
# Exponemos el puerto estándar de HTTP
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]