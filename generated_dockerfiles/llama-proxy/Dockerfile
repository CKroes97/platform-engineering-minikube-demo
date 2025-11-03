# Auto-generated Dockerfile for llama-proxy
FROM python:3.14.0a7-slim
WORKDIR /app
COPY webservices/llama-proxy.py /app/llama-proxy.py
COPY webservices-requirements/llama-proxy.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt
CMD ["python", "/app/llama-proxy.py"]
