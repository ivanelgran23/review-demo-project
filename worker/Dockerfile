FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DEFAULT_TIMEOUT=180

COPY worker/requirements.txt .
# Ставим torch с CPU из официального репозитория, чтобы ускорить и избежать таймаутов
RUN pip install --no-cache-dir --extra-index-url https://download.pytorch.org/whl/cpu torch==2.1.2
RUN pip install --no-cache-dir -r requirements.txt

COPY common ./common
COPY worker ./worker

CMD ["python", "-u", "-m", "worker.main"]
