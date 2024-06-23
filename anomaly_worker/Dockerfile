FROM python:3.9-slim

WORKDIR /app

# Install dependencies
COPY ./anomaly_worker/requirements.txt requirements.txt
RUN pip install -r requirements.txt

# Copy worker script
COPY ./anomaly_worker/worker.py worker.py
# Copy shared modules
COPY ./utils /app/utils

# Set PYTHONPATH to include the /app directory and its subdirectories
ENV PYTHONPATH "/app:/app/utils"

CMD ["python", "worker.py"]
