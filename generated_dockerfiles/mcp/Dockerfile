# Auto-generated Dockerfile for mcp
FROM python:3.13.9-slim
WORKDIR /app
COPY webservices/mcp.py /app/mcp.py
COPY webservices-requirements/mcp.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt
CMD ["python", "/app/mcp.py"]
