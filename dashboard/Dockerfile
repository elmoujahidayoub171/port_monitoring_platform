FROM python:3.12-slim

WORKDIR /app


COPY requirements.txt .

RUN pip3 install -r requirements.txt

COPY app/__init__.py    __init__.py
COPY app/database/      database/
COPY app/analytics/     analytics/
COPY app/blueprints/    blueprints/

WORKDIR /

COPY dashboard/  dashboard/
COPY run.py      run.py

CMD ["python3", "run.py"]