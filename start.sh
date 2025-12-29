#!/bin/bash
set -e

echo "🖥️ Starting Xvfb..."
Xvfb :99 -screen 0 1920x1080x24 > /dev/null 2>&1 &
sleep 3

echo "📡 Starting x11vnc..."
x11vnc -display :99 -forever -shared -rfbport 5900 -nopw > /dev/null 2>&1 &
sleep 2

echo "🌐 Starting noVNC via websockify..."
websockify --web=/opt/noVNC 6080 localhost:5900 > /dev/null 2>&1 &
sleep 2

echo "🚀 Starting Flask API..."
exec gunicorn -b 0.0.0.0:7860 -w 2 --timeout 300 app:app
