FROM python:3.11-slim

RUN apt-get update && \
    apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-ara \
    libgl1 \
    libglib2.0-0 \
    build-essential \
    wget \
    && rm -rf /var/lib/apt/lists/*


WORKDIR /app

ENV TESSERACT_PATH=/usr/bin/tesseract

COPY requirements.txt .

# Install PyTorch CPU-only first with correct index
RUN pip install --default-timeout=1000 --retries 5 --no-cache-dir \
    torch==2.5.1+cpu torchvision==0.20.1+cpu \
    --index-url https://download.pytorch.org/whl/cpu

# Install remaining dependencies
RUN pip install --default-timeout=1000 --retries 5 --no-cache-dir -r requirements.txt

COPY run.py .
COPY app/ ./app/
COPY models/ ./models/

EXPOSE 5000

CMD ["uvicorn", "run:app", "--host", "0.0.0.0", "--port", "5000"]