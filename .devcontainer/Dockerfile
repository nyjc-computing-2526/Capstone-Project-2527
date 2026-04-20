FROM mcr.microsoft.com/devcontainers/python:3.12
RUN apt-get update \
    && apt-get install -y --no-install-recommends bash curl python3-pip libpq5 \
    && python3 -m pip install --upgrade pip \
    && rm -rf /var/lib/apt/lists/*
RUN curl -fsSL https://cli.new | bash
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["sh", "-c", "gunicorn main:app --bind 0.0.0.0:$PORT"]