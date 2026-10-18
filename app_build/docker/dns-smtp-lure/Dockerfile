FROM python:3.11-alpine
WORKDIR /app
EXPOSE 53 25 587
CMD ["python", "-c", "import socket; s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM); s.bind(('0.0.0.0', 53)); print('DNS Lure armed on 53'); s.recvfrom(1024)"]
