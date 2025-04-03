FROM python:3.9-slim

WORKDIR /app

ARG FLASK_APP
ARG GMAIL_USER_EMAIL
ARG GMAIL_PASSWORD
ARG GMAIL_APP_PASSWORD
ARG RECAPTCHA_PUBLIC_KEY
ARG RECAPTCHA_PRIVATE_KEY
ARG MAIL_SERVER
ARG MAIL_PORT
ARG MAIL_USE_TLS
ARG MAIL_USERNAME
ARG MS_TRANSLATOR_KEY
ARG MS_BLOB_CONNECTION_STRING
ARG MS_BLOB_CONTAINER_NAME
ARG OPENAI_KEY

ENV FLASK_APP=${FLASK_APP}
ENV GMAIL_USER_EMAIL=${GMAIL_USER_EMAIL}
ENV GMAIL_PASSWORD=${GMAIL_PASSWORD}
ENV GMAIL_APP_PASSWORD=${GMAIL_APP_PASSWORD}
ENV RECAPTCHA_PUBLIC_KEY=${RECAPTCHA_PUBLIC_KEY}
ENV RECAPTCHA_PRIVATE_KEY=${RECAPTCHA_PRIVATE_KEY}
ENV MAIL_SERVER=${MAIL_SERVER}
ENV MAIL_PORT=${MAIL_PORT}
ENV MAIL_USE_TLS=${MAIL_USE_TLS}
ENV MAIL_USERNAME=${MAIL_USERNAME}
ENV MAIL_PASSWORD=${MAIL_PASSWORD}
ENV MS_TRANSLATOR_KEY=${MS_TRANSLATOR_KEY}
ENV MS_BLOB_CONNECTION_STRING=${MS_BLOB_CONNECTION_STRING}
ENV MS_BLOB_CONTAINER_NAME=${MS_BLOB_CONTAINER_NAME}
ENV OPENAI_KEY=${OPENAI_KEY}

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