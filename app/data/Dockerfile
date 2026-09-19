FROM python:3.12-slim

WORKDIR /


# collector.py shells out to ss / lsof / ps via sudo -n
RUN apt-get update && apt-get install -y --no-install-recommends \
        iproute2 \
        lsof \
        procps \
        sudo \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip3 install  -r requirements.txt

WORKDIR   /app

ENV PYTHONPATH=/

COPY app/__init__.py    __init__.py
COPY app/data/          data/
COPY app/database/      database/
COPY app/analytics/     analytics/
COPY app/models/        models/
COPY app/repositories/  repositories/
COPY app/services/      services/


CMD ["sh", "-c", "while true; do python -m app.services.process_connection_port_manager; sleep 300; done"]