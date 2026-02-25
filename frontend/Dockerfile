FROM python:3.11-slim

WORKDIR /app

COPY frontend ./frontend

EXPOSE 8080

CMD ["python", "-m", "http.server", "8080", "--directory", "frontend"]
