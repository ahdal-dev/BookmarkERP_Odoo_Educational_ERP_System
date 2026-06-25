FROM python:3.11-slim


WORKDIR /student_performance_service


COPY requirements.txt .

RUN pip install --default-timeout=1000 --retries 5 --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5002

ENV PYTHONPATH=/student_performance_service

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "5002"]