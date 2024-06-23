FROM python:3.9-slim

WORKDIR /app

# Install dependencies
COPY ./app/requirements.txt requirements.txt
RUN pip install -r requirements.txt

# Copy worker script
COPY ./app/app.py app.py
# Copy shared modules
COPY ./utils /app/utils

# Set PYTHONPATH to include the /app directory and its subdirectories
ENV PYTHONPATH "/app:/app/utils"

CMD ["python", "app.py"]
