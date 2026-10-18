FROM python:3.11-alpine
RUN apk add --no-cache openssh-client libffi-dev
WORKDIR /app
EXPOSE 22 2222
CMD ["python", "-c", "import socket; s = socket.socket(); s.bind(('0.0.0.0', 22)); s.listen(5); print('Cowrie SSH Lure listening on 22'); s.accept()"]
