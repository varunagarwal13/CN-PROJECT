FROM alpine:3.19
RUN apk add --no-cache curl nginx
USER 10001:10001
EXPOSE 80 8080
CMD ["nginx", "-g", "daemon off;"]
