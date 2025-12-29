FROM python:3.11-slim

# התקן Chrome, VNC dependencies
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    chromium \
    chromium-driver \
    x11vnc \
    xvfb \
    git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# התקן noVNC
RUN git clone --depth 1 https://github.com/novnc/noVNC.git /opt/noVNC && \
    ln -s /opt/noVNC/vnc.html /opt/noVNC/index.html

COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

COPY app.py .
COPY start.sh .
RUN chmod +x start.sh

# הגדר משתני סביבה
ENV PYTHONUNBUFFERED=1
ENV SE_NODE_MAX_SESSIONS=5
ENV SE_NODE_SESSION_TIMEOUT=300
ENV DISPLAY=:99
ENV VNC_PORT=5900
ENV NOVNC_PORT=6080

EXPOSE 7860 6080

CMD ["./start.sh"]
