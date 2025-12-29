FROM python:3.11-slim

# התקן Chrome dependencies
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    chromium \
    chromium-driver \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

COPY app.py .

# הגדר משתני סביבה
ENV PYTHONUNBUFFERED=1
ENV SE_NODE_MAX_SESSIONS=5
ENV SE_NODE_SESSION_TIMEOUT=300

EXPOSE 7860

CMD ["python3", "app.py"]
