FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml .
COPY src/ ./src/

RUN pip install --no-cache-dir -e .

ARG PORT=8050
ENV PORT=$PORT
# Inside a container, listen on all interfaces so a published port reaches the server
ENV HOST=0.0.0.0

CMD ["python", "src/main.py"]