# Auto-generated Dockerfile for llama-proxy
FROM python:3.13.9-slim
WORKDIR /app
COPY webservices/llama-proxy.py /app/llama-proxy.py
COPY webservices_requirements/llama-proxy.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt
COPY test_data/ /app/test_data/
COPY policies/ /app/policies/
CMD ["python", "/app/llama-proxy.py"]
