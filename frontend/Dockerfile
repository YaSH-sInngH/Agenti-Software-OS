# Dev image for the Next.js cockpit (hot-reload via `next dev`).
FROM node:20-alpine

WORKDIR /app

# Install deps first so they cache independently of source changes.
COPY package.json package-lock.json ./
RUN npm install

COPY . .

EXPOSE 3000

CMD ["npm", "run", "dev"]
