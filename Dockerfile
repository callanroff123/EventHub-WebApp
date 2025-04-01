FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN apt-get update && \
    apt-get install -y curl && \
    rm -rf /var/lib/apt/lists/*

EXPOSE 5000

# Runs Gunicorn as the WSGI server
# Production-ready, WSGI equivalent to "flask run"
CMD ["gunicorn", "-b", "0.0.0.0:5000", "-w", "4", "blog:app"]