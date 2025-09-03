FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    iputils-ping iperf3 curl && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY collector.py alerts.py utils.py config.yaml ./

ENV PYTHONUNBUFFERED=1

CMD ["python", "collector.py"]