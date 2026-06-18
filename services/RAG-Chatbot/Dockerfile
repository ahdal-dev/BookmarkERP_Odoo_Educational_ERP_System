# Academic Agent microservice image (slim — agent API + RabbitMQ worker).
# Excludes the legacy RAG/admin stack; uses the slim requirements set.
FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUTF8=1

WORKDIR /app

# Install slim deps first for better layer caching.
COPY Backend/requirements-agent.txt /app/Backend/requirements-agent.txt
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r Backend/requirements-agent.txt

# Copy only what the integrated service needs (agent loop, tools, odoo client,
# messaging, slim API + worker).
COPY Backend/agent_service.py Backend/agent_openai.py Backend/agent_tools.py \
     Backend/odoo_client.py Backend/mq.py Backend/worker.py \
     Backend/runtime_config.py Backend/SYSTEM_PROMPT.md /app/Backend/

EXPOSE 8001

# Default command runs the API; the worker is started with an override command
# (see docker-compose academic-agent-worker service).
CMD ["uvicorn", "agent_service:app", "--app-dir", "Backend", "--host", "0.0.0.0", "--port", "8001"]
