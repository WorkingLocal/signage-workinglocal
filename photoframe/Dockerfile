FROM python:3.11-slim

RUN pip install --no-cache-dir icalendar

WORKDIR /app
COPY server.py .

# Photos worden gemount via volume: /app/photos
# Config optioneel via volume: /app/config.json
VOLUME ["/app/photos"]

ENV PHOTO_DIR=/app/photos \
    CONFIG_FILE=/app/config.json \
    PORT=8181

EXPOSE 8181

HEALTHCHECK --interval=30s --timeout=5s \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8181/api/photos')" || exit 1

CMD ["python", "server.py"]
