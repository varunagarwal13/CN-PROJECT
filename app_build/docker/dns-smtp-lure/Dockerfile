FROM python:3.11-alpine
WORKDIR /app
COPY server.py /app/server.py
EXPOSE 53/udp 53/tcp 25 2525
CMD ["python", "-u", "/app/server.py"]
