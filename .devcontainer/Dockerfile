FROM mcr.microsoft.com/devcontainers/python:3.12
RUN apt-get update \
    && apt-get install -y --no-install-recommends curl python3-pip \
    && python3 -m pip install --upgrade pip \
    && rm -rf /var/lib/apt/lists/*
RUN curl -fsSL https://cli.new | sh
