FROM --platform=$BUILDPLATFORM node:22-bookworm AS index
WORKDIR /site
COPY arm.jonpalmisc.com/ ./
RUN rm -rf pagefind && npx -y pagefind@1.6.0 --site .

# Stage 2: serve the site with nginx (one image per target platform)
FROM nginx:alpine
COPY --from=index /site/ /usr/share/nginx/html/