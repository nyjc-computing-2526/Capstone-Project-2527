FROM mcr.microsoft.com/devcontainers/python:3.12
# Install curl, bash, pip, and libpq5.
RUN apt-get update \
    && apt-get install -y --no-install-recommends bash curl python3-pip libpq5 \
    && python3 -m pip install --upgrade pip \
    && rm -rf /var/lib/apt/lists/*
# Install Railway CLI first.
RUN curl -fsSL https://cli.new | bash
WORKDIR /workspace