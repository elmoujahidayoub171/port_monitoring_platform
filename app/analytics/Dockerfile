FROM python:3.12-slim

WORKDIR /

ENV PYTHONPATH=/

COPY  requirements.txt requirements.txt

RUN pip3 install -r requirements.txt

COPY app/__init__.py  /app/__init__.py
COPY app/database/    /app/database/
COPY app/analytics/   /app/analytics/


CMD ["sh", "-c", "while true; do python -m app.analytics.statistics; sleep 300; done"]
